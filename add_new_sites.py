import json
import cloudscraper
from urllib.parse import urlparse
import os
import re

# --- AYARLAR ---
INPUT_FILE = "yeni_siteler.txt"

RULE_FILES = [
    "Chrome/rules.json",
    "Firefox/rules.json",
    "Chrome/Simple Version/rules.json"
]

MANIFEST_FILES = [
    "Chrome/manifest.json",
    "Firefox/manifest.json",
    "Chrome/Simple Version/manifest.json"
]

HTML_FILES = [
    "Chrome/popup.html",
    "Firefox/popup.html"
]

VERSION_FILES = MANIFEST_FILES + ["data.json"]

# --- YARDIMCI FONKSİYONLAR ---

def clean_domain(url):
    """
    URL'den temiz domain elde eder ve BOŞLUKLARI TEMİZLER.
    """
    if not url: return ""
    
    # 1. En önemli adım: Sağdaki soldaki görünmez boşlukları sil
    url = url.strip()
    
    # 2. Protokol yoksa ekle (urlparse düzgün çalışsın diye)
    if not url.startswith("http"):
        url = "https://" + url
        
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # 3. www. varsa kaldır
        if domain.startswith("www."):
            domain = domain[4:]
            
        # 4. Son bir kez daha boşluk kontrolü yap (garanti olsun)
        return domain.strip()
    except:
        return url.strip()

def find_redirect_target(url):
    """Verilen URL'in gittiği son adresi bulur."""
    scraper = cloudscraper.create_scraper(browser='chrome')
    try:
        # url zaten clean_domain ile temizlendi ama request için tam hali lazım
        full_url = f"https://{url}"
            
        print(f"🌍 Hedef aranıyor: {full_url} ...")
        response = scraper.get(full_url, timeout=15, allow_redirects=True)
        
        final_domain = clean_domain(response.url)
        
        if final_domain and final_domain != url:
            print(f"   ✅ Bulundu: {final_domain}")
            return final_domain
        else:
            print("   ⚠️ Yönlendirme yok veya aynı.")
            return None
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return None

def get_next_id(rule_file):
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
            if not rules: return 1
            return max(r.get('id', 0) for r in rules) + 1
    except: return 1

def add_rule_to_json(old_domain, new_domain):
    for file_path in RULE_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: rules = json.load(f)
            
            # Mükerrer kayıt kontrolü
            if any(old_domain in r.get("condition", {}).get("requestDomains", []) for r in rules):
                print(f"   ⚠️ Kural zaten var: {file_path}")
                continue

            new_id = get_next_id(file_path)
            new_rule = {
                "id": new_id,
                "priority": 1,
                "action": { "type": "redirect", "redirect": { "transform": { "scheme": "https", "host": new_domain } } },
                "condition": { "requestDomains": [old_domain], "resourceTypes": ["main_frame", "sub_frame", "stylesheet", "script", "image", "font", "object", "xmlhttprequest", "ping", "csp_report", "media", "websocket", "other"] }
            }
            rules.append(new_rule)
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(rules, f, indent=2, ensure_ascii=False)
            print(f"   💾 Kural eklendi: {file_path} (ID: {new_id})")
        except Exception as e: print(f"   ❌ JSON Hatası ({file_path}): {e}")

def add_permission_to_manifest(domain):
    pattern = f"*://*.{domain}/*"
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
            if "host_permissions" not in data: data["host_permissions"] = []
            if pattern not in data["host_permissions"]:
                data["host_permissions"].append(pattern)
                with open(file_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"   🔓 İzin eklendi: {file_path}")
        except Exception as e: print(f"   ❌ Manifest Hatası: {e}")

def add_to_html_popup(old_domain, new_domain):
    html_item = f'                <li><span class="domain">{old_domain} ➔ {new_domain}</span></li>'
    for file_path in HTML_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
            if old_domain in content: continue
            if "</ul>" in content:
                new_content = content.replace("</ul>", f"{html_item}\n            </ul>")
                with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
                print(f"   🎨 HTML güncellendi: {file_path}")
        except: pass

def increment_version():
    print("\n📦 Versiyon güncelleniyor...")
    if not os.path.exists(VERSION_FILES[0]): return
    new_ver = "1.0"
    with open(VERSION_FILES[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        parts = data.get("version", "1.0").split('.')
        if len(parts) >= 2:
            major, minor = int(parts[0]), int(parts[1])
            if minor == 9: major += 1; minor = 0
            else: minor += 1
            new_ver = f"{major}.{minor}"
    
    print(f"   Yeni Versiyon: {new_ver}")
    for file_path in VERSION_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
            data["version"] = new_ver
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
        except: pass

# --- ANA İŞLEM ---

def process_new_sites():
    # Dosya yoksa SADE bir şekilde oluştur
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Alt alta linkleri yapıştır. Örnek:\n")
            f.write("# eski-site.com\n")
            f.write("# eski-site.com > yeni-site.com\n\n")
        print(f"📄 '{INPUT_FILE}' oluşturuldu.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updates_made = False
    lines_to_keep = []

    for line in lines:
        stripped_line = line.strip() # Satır başı/sonu boşluklarını sil
        
        # Boş satırları veya yorumları atla (ama dosyada tutmak için listeye ekle)
        if not stripped_line or stripped_line.startswith("#"):
            lines_to_keep.append(line)
            continue

        old_domain, new_domain = "", ""

        # Ayırıcı (>) var mı? Varsa sağını solunu iyice temizle
        if ">" in stripped_line:
            parts = stripped_line.split(">")
            old_domain = clean_domain(parts[0])
            new_domain = clean_domain(parts[1])
        else:
            # Tek link varsa
            old_domain = clean_domain(stripped_line)
            target = find_redirect_target(old_domain)
            if target: 
                new_domain = target
            else:
                print(f"⛔ {old_domain} için hedef bulunamadı.")
                lines_to_keep.append(line)
                continue

        # Eğer domain boş çıktıysa (hatalı satır) atla
        if not old_domain or not new_domain:
            continue

        print(f"\n🚀 İŞLENİYOR: '{old_domain}' -> '{new_domain}'")
        add_rule_to_json(old_domain, new_domain)
        add_permission_to_manifest(old_domain)
        add_to_html_popup(old_domain, new_domain)
        
        updates_made = True

    if updates_made:
        increment_version()
        # Sadece işlenmeyenleri ve yorumları geri yaz
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines_to_keep)
        print("\n✅ Tamamlandı ve liste temizlendi.")
    else:
        print("\n⚠️ Herhangi bir işlem yapılmadı.")

if __name__ == "__main__":
    process_new_sites()
