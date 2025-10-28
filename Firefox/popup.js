document.addEventListener('DOMContentLoaded', () => {
    // DOM elementlerini seç
    const toggleSwitch = document.getElementById('toggle-switch');
    const statusText = document.querySelector('.status');
    const rulesContainer = document.querySelector('.rules');
    
    // Kurallarımızın ID'si
    const RULESET_ID = "ruleset_1";

    // Arayüzü duruma göre güncelleyen fonksiyon
    function updateUI(isEnabled) {
        // Durum metnini ve stilini ayarla
        if (isEnabled) {
            statusText.textContent = browser.i18n.getMessage('popupStatusActive');
            statusText.classList.remove('inactive');
        } else {
            statusText.textContent = browser.i18n.getMessage('popupStatusInactive');
            statusText.classList.add('inactive');
        }
        // Kural listesini gizle/göster
        rulesContainer.style.display = isEnabled ? 'block' : 'none';
        // Switch'in durumunu ayarla
        toggleSwitch.checked = isEnabled;
    }

    // Kuralları etkinleştiren/devre dışı bırakan fonksiyon
    async function setRulesetEnabled(isEnabled) {
        if (isEnabled) {
            await browser.declarativeNetRequest.updateEnabledRulesets({
                enableRulesetIds: [RULESET_ID]
            });
        } else {
            await browser.declarativeNetRequest.updateEnabledRulesets({
                disableRulesetIds: [RULESET_ID]
            });
        }
    }

    // Switch'e tıklandığında çalışacak fonksiyon
    toggleSwitch.addEventListener('change', async (event) => {
        const isEnabled = event.target.checked;
        // Yeni durumu hafızaya kaydet
        await browser.storage.local.set({ extensionEnabled: isEnabled });
        // Kuralları güncelle
        await setRulesetEnabled(isEnabled);
        // Arayüzü güncelle
        updateUI(isEnabled);
    });

    // Sayfa yüklendiğinde hafızadaki durumu al ve arayüzü ayarla
    async function initialize() {
        // Hafızadan durumu oku (varsayılan: etkin)
        const result = await browser.storage.local.get({ extensionEnabled: true });
        const isEnabled = result.extensionEnabled;
        
        // Arayüzü ve kuralları ilk duruma göre ayarla
        updateUI(isEnabled);
        // Arka planda kuralların durumunun doğru olduğundan emin ol
        await setRulesetEnabled(isEnabled);
    }

    // Yerelleştirme ve versiyon fonksiyonları
    function localizeHtmlPage() {
        document.title = browser.i18n.getMessage('popupTitle');
        const i18nElements = document.querySelectorAll('[data-i18n]');
        i18nElements.forEach(element => {
            const messageKey = element.getAttribute('data-i18n');
            const message = browser.i18n.getMessage(messageKey);
            if (message) {
                element.textContent = message;
            }
        });
    }

    function displayVersion() {
        const manifest = browser.runtime.getManifest();
        const versionInfo = document.getElementById('version-info');
        if (versionInfo) {
            versionInfo.textContent = `${manifest.name} v${manifest.version}`;
        }
    }
    
    // Başlangıç fonksiyonlarını çağır
    localizeHtmlPage();
    displayVersion();
    initialize();
});