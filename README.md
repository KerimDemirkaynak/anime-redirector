# TrAnimeİzle Yönlendirici Chrome Eklentisi

Bu basit Chrome eklentisi, `www.tranimeizle.co` adresine yapılan tüm istekleri (ana sayfa, anime sayfaları, bölümler vb.) otomatik olarak `www.tranimeizle.top` adresindeki karşılıklarına yönlendirir.

## 🤔 Neden Gerekli?

Eğer `tranimeizle.co` adresini sık kullanıyorsanız ve artık `tranimeizle.top` adresini tercih ediyorsanız veya eski linklere tıkladığınızda otomatik olarak yeni siteye gitmek istiyorsanız bu eklenti işinizi kolaylaştırır. Tüm URL yapısını koruyarak yönlendirme yapar.

**Örnek:**
`https://www.tranimeizle.co/attack-on-titan-1-bolum-izle` adresine gitmeye çalıştığınızda otomatik olarak `https://www.tranimeizle.top/attack-on-titan-1-bolum-izle` adresine yönlendirilirsiniz.

## ✨ Özellikler

*   **Otomatik Yönlendirme:** `www.tranimeizle.co` altındaki tüm URL'leri `www.tranimeizle.top` adresindeki karşılıklarına yönlendirir.
*   **Performanslı:** Chrome'un modern `declarativeNetRequest` API'sini kullanarak hızlı ve verimli yönlendirme sağlar. Tarayıcıyı yavaşlatmaz.
*   **Basit ve Hafif:** Sadece tek bir işlevi yerine getirir, gereksiz izin veya kaynak tüketimi yoktur.

## 🚀 Kurulum

Bu eklenti (henüz) Chrome Web Mağazası'nda olmadığı için manuel olarak yüklemeniz gerekmektedir:

1.  **Depoyu İndirin:**
    *   Bu deponun sağ üst köşesindeki yeşil **`< > Code`** butonuna tıklayın.
    *   **Download ZIP** seçeneğini seçin.
    *   İndirdiğiniz ZIP dosyasını bilgisayarınızda uygun bir klasöre çıkarın (örn: `tranimeizle-yonlendirici`).

2.  **Chrome'a Yükleyin:**
    *   Chrome tarayıcınızı açın.
    *   Adres çubuğuna `chrome://extensions` yazın ve Enter'a basın.
    *   Sağ üst köşedeki **Geliştirici modu** (Developer mode) anahtarını **açık** konuma getirin.
    *   Sol üstte beliren **Paketlenmemiş öğe yükle** (Load unpacked) butonuna tıklayın.
    *   Açılan pencerede, 1. adımda ZIP dosyasını çıkardığınız **klasörü** (örn: `tranimeizle-yonlendirici`) seçin ve **Klasör Seç** (Select Folder) butonuna tıklayın.

3.  **Tamamlandı!** Eklenti şimdi Chrome eklentileri listenizde görünmeli ve aktif olmalıdır. Artık `tranimeizle.co` adreslerine gitmeye çalıştığınızda otomatik olarak `tranimeizle.top` adresine yönlendirileceksiniz.

## 🛠️ Teknik Detaylar

Eklenti, Chrome'un `declarativeNetRequest` API'sini kullanarak ağ isteklerini yakalar ve belirtilen kurala göre (`rules.json` içinde tanımlanmıştır) yönlendirme işlemini gerçekleştirir. Bu yöntem, eski `webRequest` API'sine göre daha performanslı ve gizlilik odaklıdır.

## 📁 Dosya Yapısı

```
/
├── manifest.json     # Eklentinin temel yapılandırma ve izin dosyası
├── rules.json        # Yönlendirme kuralını tanımlayan dosya
├── icons/            # Eklenti ikonları (isteğe bağlı)
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md         # Bu dosya (Proje açıklaması)
```

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

Bu eklenti resmi bir TrAnimeİzle ürünü değildir ve site sahipleriyle herhangi bir ilişkisi bulunmamaktadır. Yalnızca kişisel kullanım kolaylığı sağlamak amacıyla geliştirilmiştir.
