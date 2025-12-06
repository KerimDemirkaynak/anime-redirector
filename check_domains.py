import json
import cloudscraper
from urllib.parse import urlparse
import time
import os

# Projenizdeki rules.json dosya yolları
RULE_FILES = [
    "Chrome/rules.json",
    "Firefox/rules.json",
    "Chrome/Simple Version/rules.json"
]

def get_final_url(url):
    """
    Verilen URL'in son gittiği adresi bulur (Redirect takibi).
    Cloudflare korumasını aşmak için cloudscraper kullanılır.
    """
    scraper = cloudscraper.create_scraper(browser='chrome')
    try:
        # Eğer protokol yoksa ekle
        if not url.startswith("http"):
            full_url = f"https://{url}"
        else:
            full_url = url
            
        print(f"Kontrol ediliyor: {full_url}")
        
        response = scraper.get(full_url, timeout=15, allow_redirects=True)
        
        # Son varış noktasının domainini al
        final_domain = urlparse(response.url).netloc
        
        # 'www.' kısmını temizle
        if final_domain.startswith("www."):
            final_domain = final_domain[4:]
            
        return final_domain
    except Exception as e:
        print(f"Hata ({url}): {e}")
        return None

def update_rules():
    changes_made = False
    
    # Her dosya için işlem yap
    for file_path in RULE_FILES:
        if not os.path.exists(file_path):
            print(f"Dosya bulunamadı, atlanıyor: {file_path}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            file_changed = False
            
            for rule in rules:
                # Sadece yönlendirme (redirect) kurallarını kontrol et
                if rule.get("action", {}).get("type") == "redirect":
                    current_target = rule["action"]["redirect"]["transform"]["host"]
                    
                    # Hedef sitenin güncel adresini bul
                    new_target = get_final_url(current_target)
                    
                    # Eğer yeni bir adres bulunduysa ve eskisinden farklıysa
                    if new_target and new_target != current_target:
                        print(f"[{file_path}] DEĞİŞİKLİK: {current_target} -> {new_target}")
                        
                        # Kuralı güncelle
                        rule["action"]["redirect"]["transform"]["host"] = new_target
                        file_changed = True
                        changes_made = True
                    
                    # Sunucuları yormamak için kısa bir bekleme
                    time.sleep(2)
            
            # Dosyada değişiklik varsa kaydet
            if file_changed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, indent=2, ensure_ascii=False)
                print(f"Dosya kaydedildi: {file_path}")
                
        except Exception as e:
            print(f"Dosya işlenirken hata oluştu {file_path}: {e}")
            continue

    return changes_made

if __name__ == "__main__":
    if update_rules():
        print("Domain değişiklikleri uygulandı.")
    else:
        print("Herhangi bir değişiklik gerekmiyor.")
