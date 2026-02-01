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
    """URL'den temiz domain elde eder (https://www.site.com -> site.com)"""
    if not url.startswith("http"):
        url = "https://" + url.strip()
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def find_redirect_target(url):
    """Verilen URL'in gittiği son adresi bulur."""
    scraper = cloudscraper.create_scraper(browser='chrome')
    try:
        if not url.startswith("http"):
            full_url = f"https://{url}"
        else:
            full_url = url
            
        print(f"🌍 Hedef aranıyor: {full_url} ...")
        response = scraper.get(full_url, timeout=15, allow_redirects=True)
        final_domain = clean_domain(response.url)
        original_domain = clean_domain(full_url)
        
        if final_domain != original_domain:
            print(f"   ✅ Bulundu: {final_domain}")
            return final_domain
        else:
            print("   ⚠️ Yönlendirme tespit edilemedi.")
            return None
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return None

def get_next_id(rule_file):
    """En büyük ID'yi bulup 1 fazlasını döner."""
    try:
        with open(rule_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
            if not rules: return 1
            max_id = max(r.get('id', 0) for r in rules)
            return max_id + 1
    except:
        return 1

def add_rule_to_json(old_domain, new_domain):
    """Rules.json dosyalarına yeni kuralı ekler."""
    for file_path in RULE_FILES:
        if not os.path.exists(file_path): continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            # Zaten var mı kontrol et
            exists = any(old_domain in r.get("condition", {}).get("requestDomains", []) for r in rules)
            if exists:
                print(f"   ⚠️ Kural zaten var, atlanıyor: {file_path}")
                continue

            new_id = get_next_id(file_path)
            
            new_rule = {
                "id": new_id,
                "priority": 1,
                "action": {
                    "type": "redirect",
                    "redirect": { "transform": { "scheme": "https", "host": new_domain } }
                },
                "condition": {
                    "requestDomains": [old_domain],
                    "resourceTypes": [
                        "main_frame", "sub_frame", "stylesheet", "script", "image", 
                        "font", "object", "xmlhttprequest", "ping", "csp_report", 
                        "media", "websocket", "other"
                    ]
                }
            }
            
            rules.append(new_rule)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2, ensure_ascii=False)
            print(f"   💾 Kural eklendi: {file_path} (ID: {new_id})")
            
        except Exception as e:
            print(f"   ❌ JSON Hatası ({file_path}): {e}")

def add_permission_to_manifest(domain):
    """Manifest dosyalarına host izni ekler."""
    pattern = f"*://*.{domain}/*"
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "host_permissions" not in data:
                data["host_permissions"] = []
                
            if pattern not in data["host_permissions"]:
                data["host_permissions"].append(pattern)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"   🔓 İzin eklendi: {file_path}")
        except Exception as e:
            print(f"   ❌ Manifest Hatası: {e}")

def add_to_html_popup(old_domain, new_domain):
    """Popup.html dosyalarına listeyi ekler."""
    # HTML şablonu (Firefox ve Chrome yapılarına uygun genel yapı)
    html_item = f'                <li><span class="domain">{old_domain} ➔ {new_domain}</span></li>'
    
    for file_path in HTML_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Zaten ekli mi?
            if old_domain in content:
                print(f"   ⚠️ HTML'de zaten var: {file_path}")
                continue
                
            # </ul> etiketinden hemen öncesine ekle
            if "</ul>" in content:
                new_content = content.replace("</ul>", f"{html_item}\n            </ul>")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   🎨 HTML güncellendi: {file_path}")
        except Exception as e:
            print(f"   ❌ HTML Hatası: {e}")

def increment_version():
    """Versiyonu 1.7 -> 1.8 şeklinde artırır."""
    print("\n📦 Versiyon güncelleniyor...")
    if not os.path.exists(VERSION_FILES[0]): return

    # Yeni versiyonu belirle
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
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data["version"] = new_ver
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ❌ Versiyon hatası ({file_path}): {e}")

# --- ANA İŞLEM ---

def process_new_sites():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ '{INPUT_FILE}' dosyası bulunamadı! Lütfen oluşturup içine linkleri yapıştırın.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updates_made = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"): continue

        old_domain = ""
        new_domain = ""

        # Ayırıcı (>) var mı kontrol et
        if ">" in line:
            parts = line.split(">")
            old_domain = clean_domain(parts[0])
            new_domain = clean_domain(parts[1])
        else:
            # Sadece tek link verilmiş, otomatik bul
            old_domain = clean_domain(line)
            target = find_redirect_target(old_domain)
            if target:
                new_domain = target
            else:
                print(f"⛔ {old_domain} için yeni adres bulunamadı, manuel ekleyin.")
                continue

        print(f"\n🚀 İŞLENİYOR: {old_domain} -> {new_domain}")
        
        # 1. Rules.json güncelle
        add_rule_to_json(old_domain, new_domain)
        
        # 2. Manifest izinleri ekle
        add_permission_to_manifest(old_domain)
        
        # 3. Popup HTML güncelle
        add_to_html_popup(old_domain, new_domain)
        
        updates_made = True

    if updates_made:
        increment_version()
        print("\n✅ Tüm işlemler başarıyla tamamlandı!")
        
        # Dosya içeriğini temizle (isteğe bağlı)
        # with open(INPUT_FILE, 'w') as f: f.write("") 
        # print("   (yeni_siteler.txt temizlendi)")
    else:
        print("\n⚠️ Herhangi bir işlem yapılmadı.")

if __name__ == "__main__":
    process_new_sites()
