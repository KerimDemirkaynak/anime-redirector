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
            
        print(f"📡 Bağlanılıyor: {full_url}")
        response = scraper.get(full_url, timeout=15, allow_redirects=True)
        final_domain = urlparse(response.url).netloc
        
        # 'www.' ön ekini kaldır ki karşılaştırma hatasız olsun
        if final_domain.startswith("www."):
            final_domain = final_domain[4:]
        return final_domain
    except Exception as e:
        print(f"❌ Hata ({url}): {e}")
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
                print(f"📝 [{file_path}] Metin güncellendi: {old_domain} -> {new_domain}")
        except Exception as e: print(f"Dosya hatası ({file_path}): {e}")

def update_manifest_permissions(domain):
    """Eski domaini host_permissions'a ekler (Geriye dönük uyumluluk için)."""
    # Not: Genellikle yeni domaini eklemek istersin ama senin mantığına dokunmadım.
    permission_pattern = f"*://*.{domain}/*"
    for file_path in MANIFEST_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f: manifest = json.load(f)
            
            # Eğer host_permissions yoksa oluştur
            if "host_permissions" not in manifest: manifest["host_permissions"] = []
            
            if permission_pattern not in manifest["host_permissions"]:
                manifest["host_permissions"].append(permission_pattern)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)
                print(f"🔓 [{file_path}] İzin eklendi: {domain}")
        except Exception as e: print(f"Manifest hatası ({file_path}): {e}")

def increment_version_string(v_str):
    """Versiyonu artırır (1.7 -> 1.8, 1.9 -> 2.0)."""
    try:
        parts = v_str.split('.')
        if len(parts) >= 2:
            major = int(parts[0])
            minor = int(parts[1])
            
            if minor == 9:
                major += 1
                minor = 0
            else:
                minor += 1
            return f"{major}.{minor}"
    except:
        pass
    return v_str

def update_all_versions():
    """Tüm ilgili dosyalardaki versiyon numarasını artırır."""
    print("\n--- 🚀 Versiyon Yükseltme İşlemi Başlatılıyor ---")
    if not os.path.exists(VERSION_FILES[0]): return
    
    new_version = None
    with open(VERSION_FILES[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
        old_version = data.get("version", "1.0")
        new_version = increment_version_string(old_version)
    
    print(f"Versiyon: {old_version} -> {new_version}")
    
    for file_path in VERSION_FILES:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            file_data["version"] = new_version
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=2, ensure_ascii=False)
            print(f"✅ [{file_path}] Versiyon güncellendi.")
        except Exception as e:
            print(f"Versiyon hatası ({file_path}): {e}")

# ------------------- ANA MANTIK (GÜNCELLENDİ) -------------------

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
                    
                    # 1. Mevcut domain nereye gidiyor?
                    print(f"\n🔍 Kontrol ediliyor: {current_target}")
                    new_target = get_final_url(current_target)
                    
                    # Eğer bir değişiklik varsa VE yeni target boş değilse
                    if new_target and new_target != current_target:
                        
                        print(f"⚠️  Potansiyel değişim tespit edildi: {current_target} -> {new_target}")
                        
                        # --- KRİTİK KORUMA: DÖNGÜ KONTROLÜ ---
                        # Bulduğumuz "yeni" adres aslında "eski" adrese geri mi dönüyor?
                        check_back_url = get_final_url(new_target)
                        
                        if check_back_url == current_target:
                            print(f"⛔ SAHTE ALARM: {new_target} adresi tekrar {current_target} adresine yönleniyor.")
                            print("   Bu bir yönlendirme döngüsü (loop) veya alias. DEĞİŞİKLİK YAPILMAYACAK.")
                            continue # Bu kuralı atla, değiştirme!
                        
                        # Eğer buraya geldiysek, gerçek bir göç var demektir.
                        print(f"✅ ONAYLANDI: {current_target} -> {new_target} değişimi uygulanıyor.")
                        
                        # A. Kural güncelle
                        rule["action"]["redirect"]["transform"]["host"] = new_target
                        file_changed = True
                        changes_made = True
                        
                        # B. Metinleri güncelle
                        update_text_files(current_target, new_target)
                        
                        # C. İzin ekle
                        update_manifest_permissions(current_target)
                    
                    else:
                        print(f"🆗 Değişiklik yok: {current_target}")

                    time.sleep(1) # Cloudscraper'ı boğmamak için bekleme
            
            if file_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, indent=2, ensure_ascii=False)
                print(f"💾 Kural dosyası kaydedildi: {file_path}")
                
        except Exception as e:
            print(f"Dosya işlenirken hata ({file_path}): {e}")
            continue

    return changes_made

if __name__ == "__main__":
    print("--- Domain Kontrol Scripti Başladı ---\n")
    if update_rules():
        print("\n🎉 Domain değişiklikleri uygulandı.")
        update_all_versions()
    else:
        print("\n💤 Herhangi bir değişiklik gerekmiyor.")
