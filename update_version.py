import json
import os
import re
import sys

MANIFEST_FILES = [
    "Chrome/manifest.json",
    "Firefox/manifest.json",
    "Chrome/Simple Version/manifest.json"
]
DATA_FILE = "data.json"
INDEX_FILE = "index.html"

def update_versions(new_version):
    print(f"🚀 Yeni sürüm {new_version} olarak ayarlanıyor...\n")
    
    # 1. JSON DOSYALARINI GÜNCELLE (Manifestler ve data.json)
    json_files = MANIFEST_FILES + [DATA_FILE]
    for file_path in json_files:
        if not os.path.exists(file_path): continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Versiyon değerini değiştir
            data["version"] = new_version
            
            # data.json içindeki GitHub release zip/crx linklerindeki vX.X sürümlerini de düzelt
            if file_path == DATA_FILE and "downloads" in data:
                if "chromeZip" in data["downloads"]:
                    data["downloads"]["chromeZip"] = re.sub(r'/v\d+\.\d+/', f'/v{new_version}/', data["downloads"]["chromeZip"])
                if "chromeCrx" in data["downloads"]:
                    data["downloads"]["chromeCrx"] = re.sub(r'/v\d+\.\d+/', f'/v{new_version}/', data["downloads"]["chromeCrx"])
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ {file_path} güncellendi.")
        except Exception as e:
            print(f"❌ Hata ({file_path}): {e}")

    # 2. INDEX.HTML GÜNCELLEMESİ
    # Site zaten JS ile data.json'dan sürüm çekiyor ama HTML'e sabit yazılmış 
    # "Sürüm 1.7" / "Version 1.7" gibi CRX linki metinlerini de zorla güncelliyoruz.
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Regex ile eski sürüm numaralarını yenisiyle değiştir
            new_content = re.sub(r'Sürüm \d+\.\d+', f'Sürüm {new_version}', content)
            new_content = re.sub(r'Version \d+\.\d+', f'Version {new_version}', new_content)
            
            if content != new_content:
                with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ {INDEX_FILE} güncellendi (Sabit metinler düzeltildi).")
            else:
                print(f"ℹ️ {INDEX_FILE} incelendi (Değişecek sabit yazı bulunmadı).")
        except Exception as e:
            print(f"❌ Hata ({INDEX_FILE}): {e}")

if __name__ == "__main__":
    # GitHub Actions'tan veya terminalden parametre gelirse al, yoksa input bekle
    if len(sys.argv) > 1:
        target_version = sys.argv[1].strip()
    else:
        target_version = input("Lütfen yeni sürüm numarasını girin (Örn: 2.1): ").strip()
        
    if target_version:
        update_versions(target_version)
    else:
        print("⚠️ Geçersiz sürüm numarası.")
