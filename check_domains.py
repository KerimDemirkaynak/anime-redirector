import json
import cloudscraper
from urllib.parse import urlparse
import time
import os

# ------------------- DOSYA LİSTELERİ -------------------

# 1. JSON Kurallarının Olduğu Dosyalar
RULE_FILES = [
    "Chrome/rules.json",
    "Firefox/rules.json",
    "Chrome/Simple Version/rules.json"
]

# 2. Domainlerin Metin Olarak Geçtiği Dosyalar (HTML, README vb.)
OTHER_FILES = [
    "Chrome/popup.html",
    "Firefox/popup.html",
    "README.md"
]

# 3. İzinlerin Ekleneceği Manifest Dosyaları
MANIFEST_FILES = [
    "Chrome/manifest.json",
    "Firefox/manifest.json",
    "Chrome/Simple Version/manifest.json"
]

# 4. Versiyonun Güncelleneceği Dosyalar
VERSION_FILES = [
    "Chrome/manifest.json",
    "Firefox/manifest.json",
    "Chrome/Simple Version/manifest.json",
    "data.json"
]

# ------------------- YARDIMCI FONKSİYONLAR -------------------

def get_final_url(url):
    """Verilen URL'in son gittiği adresi bulur (Redirect takibi)."""
    scraper = cloudscraper.create_scraper(browser='chrome')
    try:
        if not url.startswith("http"):
            full_url = f"https://{url}"
        else:
            full_url = url
            
        print(f"Kontrol ediliyor: {full_url}")
        response = scraper.get(full_url, timeout=15, allow_redirects=True)
        final_domain = urlparse(response.url).netloc
        if final_domain.startswith("www."):
            final_domain = final_domain[4:]
        return final_domain
    except Exception as e:
        print(f"Hata ({url}): {e}")
        return None

def update_text_files(old_domain, new_domain):
    """HTML ve MD dosyalarındaki metinleri günceller."""
    for file_path in OTHER_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
            if old_domain in content:
                new_content = content.replace(old_domain, new_domain)
                with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
                print(f"[{file_path}] Metin güncellendi: {old_domain} -> {new_domain}")
        except Exception as e: print(f"Hata ({file_path}): {e}")

def update_manifest_permissions(domain):
    """Eski domaini host_permissions'a ekler."""
    permission_pattern = f"*://*.{domain}/*"
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: manifest = json.load(f)
            if "host_permissions" not in manifest: manifest["host_permissions"] = []
            
            if permission_pattern not in manifest["host_permissions"]:
                manifest["host_permissions"].append(permission_pattern)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)
                print(f"[{file_path}] İzin eklendi: {domain}")
        except Exception as e: print(f"Hata ({file_path}): {e}")

def increment_version_string(v_str):
    """
    Versiyonu belirtilen mantığa göre artırır.
    Örnek: 1.7 -> 1.8
    Örnek: 5.9 -> 6.0
    """
    try:
        parts = v_str.split('.')
        # Genellikle format X.Y şeklindedir
        if len(parts) >= 2:
            major = int(parts[0])
            minor = int(parts[1])
            
            if minor == 9:
                major += 1
                minor = 0
            else:
                minor += 1
            
            # Kalan parçalar varsa (örn: 1.7.1) onları korumuyoruz, 
            # basit X.Y formatına sadık kalıyoruz.
            return f"{major}.{minor}"
    except:
        pass
    return v_str

def update_all_versions():
    """Tüm ilgili dosyalardaki versiyon numarasını artırır."""
    print("--- Versiyon Yükseltme İşlemi Başlatılıyor ---")
    
    # Referans olması için önce bir dosyadan eski versiyonu okuyalım
    if not os.path.exists(VERSION_FILES[0]): return
    
    new_version = None
    
    # 1. Yeni versiyon numarasını belirle
    with open(VERSION_FILES[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        old_version = data.get("version", "1.0")
        new_version = increment_version_string(old_version)
    
    print(f"Versiyon Yükseltilecek: {old_version} -> {new_version}")
    
    # 2. Tüm dosyalara uygula
    for file_path in VERSION_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            file_data["version"] = new_version
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
                
            print(f"[{file_path}] Versiyon güncellendi.")
        except Exception as e:
            print(f"Versiyon hatası ({file_path}): {e}")

# ------------------- ANA MANTIK -------------------

def update_rules():
    changes_made = False
    
    for file_path in RULE_FILES:
        if not os.path.exists(file_path): continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f: rules = json.load(f)
            file_changed = False
            
            for rule in rules:
                if rule.get("action", {}).get("type") == "redirect":
                    current_target = rule["action"]["redirect"]["transform"]["host"]
                    new_target = get_final_url(current_target)
                    
                    if new_target and new_target != current_target:
                        print(f"[{file_path}] DEĞİŞİKLİK: {current_target} -> {new_target}")
                        
                        # A. Kural güncelle
                        rule["action"]["redirect"]["transform"]["host"] = new_target
                        file_changed = True
                        changes_made = True
                        
                        # B. Metinleri güncelle
                        update_text_files(current_target, new_target)
                        
                        # C. İzin ekle
                        update_manifest_permissions(current_target)
                    
                    time.sleep(1) # Hız sınırı
            
            if file_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, indent=2, ensure_ascii=False)
                print(f"Kural dosyası kaydedildi: {file_path}")
                
        except Exception as e:
            print(f"Dosya işlenirken hata ({file_path}): {e}")
            continue

    return changes_made

if __name__ == "__main__":
    # Eğer herhangi bir değişiklik yapıldıysa (True dönerse)
    if update_rules():
        print("Domain değişiklikleri uygulandı.")
        # Versiyonu sadece değişiklik varsa artır
        update_all_versions()
    else:
        print("Herhangi bir değişiklik gerekmiyor.")
