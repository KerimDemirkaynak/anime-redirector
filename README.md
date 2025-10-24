# Web Yönlendirici ve Engelleyici Chrome Uzantısı

Bu proje, belirli web sitelerini engelleyen ve bazılarını yeni adreslerine yönlendiren basit ve etkili bir Chrome uzantısıdır. `declarativeNetRequest` API'si kullanılarak geliştirilmiştir, bu sayede tarayıcı performansını etkilemeden hızlı ve güvenli bir şekilde çalışır.

## 🚀 Özellikler

- **Site Yönlendirme:** Eski veya değişen web sitesi adreslerini otomatik olarak güncel adreslerine yönlendirir.
- **Site Engelleme:** İstenmeyen veya dikkat dağıtıcı web sitelerine erişimi engeller.
- **Yüksek Performans:** `declarativeNetRequest` API'si sayesinde tarayıcıya ek yük bindirmeden, verimli bir şekilde çalışır.
- **Kolay Kurulum:** Basit ve hızlı bir şekilde Chrome tarayıcınıza manuel olarak eklenebilir.

## 🛠️ Nasıl Çalışır?

Uzantı, `rules.json` dosyasında tanımlanan kurallara göre çalışır. Bu kurallar, hangi sitelerin engelleneceğini ve hangilerinin yönlendirileceğini belirtir.

### Yönlendirme Kuralları:

- `vidmoly.to` → `https://vidmoly.net`
- `animecix.net`, `anm.cx` → `https://animecix.tv`
- `asyaanimeleri.com` → `https://asyaanimeleri.top`
- `hianime.to` → `https://hianime.pe`
- `turkanime.co` → `https://turkanime.tv`

### Engelleme Kuralları:

Aşağıdaki alan adlarına ve alt alan adlarına yapılan tüm istekler engellenir:

- `chatango.com`
- `anizmnet.chatango.com`
- `st.chatango.com`

## ⚙️ Kurulum

Bu uzantıyı manuel olarak Chrome tarayıcınıza kurmak için aşağıdaki adımları izleyin:

1.  Bu depoyu bilgisayarınıza `ZIP` olarak indirin ve dosyaları bir klasöre çıkarın veya `git clone` komutu ile klonlayın.
2.  Chrome tarayıcınızı açın ve adres çubuğuna `chrome://extensions` yazarak **Uzantılar** sayfasına gidin.
3.  Sağ üst köşedeki **Geliştirici modu**'nu etkinleştirin.
4.  Sol üstte beliren **Paketlenmemiş öğe yükle** butonuna tıklayın.
5.  Proje dosyalarının bulunduğu klasörü seçin.

Uzantı başarıyla yüklenecek ve tarayıcınızın uzantılar listesinde etkin hale gelecektir.

## 📜 Teknik Detaylar

Bu uzantı, Chrome'un `declarativeNetRequest` API'sini kullanır. Bu API, ağ isteklerini programatik olarak engellemek veya değiştirmek için güçlü ve performansa duyarlı bir yol sağlar.

- **`manifest.json`**: Uzantının temel yapılandırmasını, adını, sürümünü, izinlerini ve kuralların yolunu tanımlar.
- **`rules.json`**: Uzantının uygulayacağı tüm yönlendirme ve engelleme kurallarını içerir.

## 🙏 Katkıda Bulunma

Katkılarınız için her zaman açığız! Bir hatayı bildirmek, yeni bir özellik önermek veya mevcut kuralları güncellemek için lütfen bir "issue" açın veya "pull request" gönderin.
