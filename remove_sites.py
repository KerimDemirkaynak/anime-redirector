import json
import os
import re

# --- AYARLAR ---
# Silinecek sitelerin listesini alacağımız dosya
INPUT_FILE = "silinecek_siteler.txt"

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
    """URL'den temiz domain elde eder (boşlukları ve protokolleri temizler)."""
    if not url: return ""
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.strip()
    except:
        return url.strip()

def remove_from_json(domain):
    """rules.json dosyalarından hedef domaini içeren kuralları siler."""
    for file_path in RULE_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            new_rules = []
            for rule in rules:
                req_domains = rule.get("condition", {}).get("requestDomains", [])
                target_host = rule.get("action", {}).get("redirect", {}).get("transform", {}).get("host", "")
                
                # Eğer domain engellenenler listesinde, yönlendirilen veya yönlendiren taraftaysa bu kuralı listeye dahil etme (sil)
                if domain in req_domains or domain == target_host:
                    continue
                new_rules.append(rule)
            
            if len(new_rules) != len(rules):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(new_rules, f, indent=2, ensure_ascii=False)
                print(f"   🗑️ Kural silindi: {file_path}")
        except Exception as e:
            print(f"   ❌ JSON Hatası ({file_path}): {e}")

def remove_from_manifest(domain):
    """manifest.json dosyalarından host_permissions izinlerini siler."""
    pattern = f"*://*.{domain}/*"
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "host_permissions" in data and pattern in data["host_permissions"]:
                data["host_permissions"].remove(pattern)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"   🔒 İzin kaldırıldı: {file_path}")
        except Exception as e:
            print(f"   ❌ Manifest Hatası ({file_path}): {e}")

def remove_from_html(domain):
    """popup.html dosyalarından ilgili <li> elemanını tespit edip siler."""
    for file_path in HTML_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # HTML içindeki <li> etiketlerini bularak içinde domain geçiyorsa tüm satırı/bloğu siler
            # Regex açıklaması: <li> ile başlayıp </li> ile biten ve içinde hedef domain geçen bloğu eşleştirir
            pattern = re.compile(r'\s*<li>(?:(?!<li>).)*?' + re.escape(domain) + r'(?:(?!<li>).)*?</li>', re.IGNORECASE | re.DOTALL)
            new_content, count = pattern.subn('', content)
            
            if count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"   🧹 HTML listesinden silindi ({count} eşleşme): {file_path}")
        except Exception as e:
            print(f"   ❌ HTML Hatası ({file_path}): {e}")

def increment_version():
    """Manifest ve JSON dosyalarındaki versiyon numarasını bir üst sürüme günceller."""
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

def process_remove_sites():
    # Dosya yoksa SADE bir şekilde oluştur
    if not os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Silinmesini istediğiniz domainleri alt alta yazın (eski veya yeni adres fark etmez).\n")
            f.write("# ornek-site.com\n")
        print(f"📄 '{INPUT_FILE}' oluşturuldu. Lütfen silinecek siteleri bu dosyaya ekleyip script'i tekrar çalıştırın.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updates_made = False
    lines_to_keep = []

    for line in lines:
        stripped_line = line.strip()
        
        # Boş satırları veya yorumları atla (ama dosyada tutmak için listeye ekle)
        if not stripped_line or stripped_line.startswith("#"):
            lines_to_keep.append(line)
            continue

        domain = clean_domain(stripped_line)
        if not domain: continue

        print(f"\n🗑️ İŞLENİYOR: '{domain}' uzantıdan temizleniyor...")
        
        remove_from_json(domain)
        remove_from_manifest(domain)
        remove_from_html(domain)
        
        updates_made = True

    if updates_made:
        increment_version()
        # Sadece işlenmeyenleri ve yorumları geri yaz (silinenler dosyadan çıkarılır)
        with open(INPUT_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines_to_keep)
        print("\n✅ Temizlik tamamlandı. İşlenen siteler listeden kaldırıldı.")
    else:
        print("\n⚠️ Herhangi bir işlem yapılmadı.")

if __name__ == "__main__":
    process_remove_sites()
