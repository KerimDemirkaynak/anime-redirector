import json
import cloudscraper
from urllib.parse import urlparse
import time
import os

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

def get_final_url(url):
    """
    Verilen URL'in son gittiği adresi bulur (Redirect takibi).
    Cloudflare korumasını aşmak için cloudscraper kullanılır.
    """
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
    """
    Belirtilen metin dosyalarında (HTML, MD) eski domaini yenisiyle değiştirir.
    """
    for file_path in OTHER_FILES:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_domain in content:
                new_content = content.replace(old_domain, new_domain)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[{file_path}] METİN GÜNCELLENDİ: {old_domain} -> {new_domain}")
                
        except Exception as e:
            print(f"Metin dosyası güncellenirken hata ({file_path}): {e}")

def update_manifest_permissions(domain):
    """
    Eskiyen domaini manifest dosyalarındaki host_permissions listesine ekler.
    Format: *://*.domain.com/*
    """
    permission_pattern = f"*://*.{domain}/*"
    
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path):
            print(f"Manifest bulunamadı: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # host_permissions alanı yoksa oluştur
            if "host_permissions" not in manifest:
                manifest["host_permissions"] = []
            
            # Eğer izin zaten yoksa ekle
            if permission_pattern not in manifest["host_permissions"]:
                manifest["host_permissions"].append(permission_pattern)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)
                print(f"[{file_path}] MANIFEST GÜNCELLENDİ (İzin Eklendi): {domain}")
            else:
                print(f"[{file_path}] İzin zaten mevcut: {domain}")
                
        except Exception as e:
            print(f"Manifest güncellenirken hata ({file_path}): {e}")

def update_rules():
    changes_made = False
    
    for file_path in RULE_FILES:
        if not os.path.exists(file_path):
            print(f"Dosya bulunamadı: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            file_changed = False
            
            for rule in rules:
                if rule.get("action", {}).get("type") == "redirect":
                    current_target = rule["action"]["redirect"]["transform"]["host"]
                    
                    new_target = get_final_url(current_target)
                    
                    # Değişiklik varsa
                    if new_target and new_target != current_target:
                        print(f"[{file_path}] DEĞİŞİKLİK TESPİT EDİLDİ: {current_target} -> {new_target}")
                        
                        # 1. Kuralı Güncelle
                        rule["action"]["redirect"]["transform"]["host"] = new_target
                        file_changed = True
                        changes_made = True
                        
                        # 2. Metin Dosyalarını Güncelle (HTML, README)
                        update_text_files(current_target, new_target)
                        
                        # 3. Manifest İzinlerine ESKİ domaini ekle
                        update_manifest_permissions(current_target)
                    
                    time.sleep(2)
            
            if file_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, indent=2, ensure_ascii=False)
                print(f"Kurallar dosyası kaydedildi: {file_path}")
                
        except Exception as e:
            print(f"Dosya işlenirken hata ({file_path}): {e}")
            continue

    return changes_made

if __name__ == "__main__":
    if update_rules():
        print("Tüm güncellemeler başarıyla tamamlandı.")
    else:
        print("Herhangi bir değişiklik gerekmiyor.")
