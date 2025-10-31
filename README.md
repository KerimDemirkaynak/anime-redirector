# 🌐 Web Yönlendirici ve Engelleyici  
### (Chromium & Firefox tabanlı tüm tarayıcılar için)

Bu proje, belirli web sitelerini engelleyen ve bazılarını yeni adreslerine yönlendiren basit ve etkili bir **tarayıcı uzantısıdır**.  
`declarativeNetRequest` API'si kullanılarak geliştirilmiştir; bu sayede tarayıcı performansını etkilemeden hızlı ve güvenli bir şekilde çalışır.

---

## 🧩 Desteklenen Tarayıcılar

| Tür | Tarayıcılar | Kurulum |
|------|--------------|-----------|
| **Chromium tabanlı** | Chrome, Edge, Brave, Opera, Vivaldi, Arc, vs. | Manuel yükleme |
| **Firefox tabanlı** | Firefox, Waterfox, LibreWolf, Tor Browser, vs. | Mağaza üzerinden yükleme |

👉 [Firefox için indir](https://addons.mozilla.org/tr/android/addon/web-redirector-and-blocker/)

---

## 🚀 Özellikler

- **Site Yönlendirme:** Eski veya değişen web sitesi adreslerini otomatik olarak güncel adreslerine yönlendirir.  
- **Site Engelleme:** İstenmeyen veya dikkat dağıtıcı web sitelerine erişimi engeller.  
- **Yüksek Performans:** `declarativeNetRequest` API'si sayesinde tarayıcıya ek yük bindirmeden, verimli bir şekilde çalışır.  
- **Tam Uyumluluk:** Tüm Chromium **ve** tüm Firefox tabanlı tarayıcılarda çalışır.  
- **Kolay Kurulum:** Chromium tabanlılarda manuel, Firefox tabanlılarda mağaza üzerinden kurulum imkânı.

---

## 🛠️ Nasıl Çalışır?

Uzantı, `rules.json` dosyasında tanımlanan kurallara göre çalışır.  
Bu kurallar, hangi sitelerin engelleneceğini ve hangilerinin yönlendirileceğini belirtir.

### 🔁 Yönlendirme Kuralları

| Eski Adresler | Yeni Adres |
|----------------|------------|
| `vidmoly.to` | `https://vidmoly.net` |
| `animecix.net`, `anm.cx` | `https://animecix.tv` |
| `asyaanimeleri.com` | `https://asyaanimeleri.top` |
| `hianime.to` | `https://hianime.pe` |
| `turkanime.co` | `https://turkanime.tv` |

### 🚫 Engelleme Kuralları

Aşağıdaki alan adlarına ve alt alan adlarına yapılan tüm istekler engellenir:

chatango.com
anizmnet.chatango.com
st.chatango.com

---

## ⚙️ Kurulum

### 🔹 Chromium tabanlı tarayıcılar (Chrome, Edge, Brave, Opera, Vivaldi vb.)

1. `ZIP` dosyasını indirin ve çıkarın.  
2. Tarayıcınızda `chrome://extensions` (veya eşdeğeri) adresine gidin.  
3. Sağ üstteki **Geliştirici modu**’nu etkinleştirin.  
4. **Paketlenmemiş öğe yükle** seçeneğiyle proje klasörünü yükleyin.  

### 🔹 Firefox tabanlı tarayıcılar (Firefox, Tor, Waterfox vb.)

1. Aşağıdaki bağlantıdan yükleyin:  
   👉 [Firefox için Web Yönlendirici ve Engelleyici](https://addons.mozilla.org/tr/android/addon/web-redirector-and-blocker/)  
2. Android veya masaüstü fark etmeksizin, yükleme tamamlandıktan sonra otomatik olarak etkinleşir.

---

## 📜 Teknik Detaylar

Uzantı, hem Chromium hem de Firefox tabanlı tarayıcıların desteklediği `declarativeNetRequest` sistemini kullanır.  

- **`manifest.json`** → Uzantının temel yapılandırmasını, adını, sürümünü ve izinlerini tanımlar.  
- **`rules.json`** → Tüm yönlendirme ve engelleme kurallarını içerir.  

---

## 🤝 Katkıda Bulunma

Katkılar her zaman memnuniyetle karşılanır!  
Bir hata bildirmek, yeni bir yönlendirme eklemek veya mevcut kuralları güncellemek için bir **issue** açabilir ya da **pull request** gönderebilirsiniz.

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.
