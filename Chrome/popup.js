document.addEventListener('DOMContentLoaded', () => {
    // DOM elementlerini seç
    const toggleSwitch = document.getElementById('toggle-switch');
    const statusText = document.querySelector('.status');
    const rulesContainer = document.querySelector('.rules');
    
    const RULESET_ID = "ruleset_1";

    // Arayüzü duruma göre güncelleyen fonksiyon
    function updateUI(isEnabled) {
        if (isEnabled) {
            statusText.textContent = "Extension is active and protecting sites.";
            statusText.classList.remove('inactive');
        } else {
            statusText.textContent = "Extension is currently disabled.";
            statusText.classList.add('inactive');
        }
        
        rulesContainer.classList.toggle('disabled', !isEnabled);
        toggleSwitch.checked = isEnabled;
    }

    // Kuralları etkinleştiren/devre dışı bırakan fonksiyon
    async function setRulesetEnabled(isEnabled) {
        if (isEnabled) {
            // DEĞİŞİKLİK: 'browser' yerine 'chrome' kullanıldı
            await chrome.declarativeNetRequest.updateEnabledRulesets({
                enableRulesetIds: [RULESET_ID]
            });
        } else {
            // DEĞİŞİKLİK: 'browser' yerine 'chrome' kullanıldı
            await chrome.declarativeNetRequest.updateEnabledRulesets({
                disableRulesetIds: [RULESET_ID]
            });
        }
    }

    // Switch'e tıklandığında çalışacak fonksiyon
    toggleSwitch.addEventListener('change', async (event) => {
        const isEnabled = event.target.checked;
        // DEĞİŞİKLİK: 'browser' yerine 'chrome' kullanıldı
        await chrome.storage.local.set({ extensionEnabled: isEnabled });
        await setRulesetEnabled(isEnabled);
        updateUI(isEnabled);
    });

    // Sayfa yüklendiğinde hafızadaki durumu al ve arayüzü ayarla
    async function initialize() {
        // DEĞİŞİKLİK: 'browser' yerine 'chrome' kullanıldı
        const result = await chrome.storage.local.get({ extensionEnabled: true });
        const isEnabled = result.extensionEnabled;
        
        updateUI(isEnabled);
        await setRulesetEnabled(isEnabled);
    }

    // Sadece versiyon bilgisini gösteren fonksiyon
    function displayVersion() {
        // DEĞİŞİKLİK: 'browser' yerine 'chrome' kullanıldı
        const manifest = chrome.runtime.getManifest();
        const versionInfo = document.getElementById('version-info');
        if (versionInfo) {
            versionInfo.textContent = `${manifest.name} v${manifest.version}`;
        }
    }
    
    // Başlangıç fonksiyonlarını çağır
    displayVersion();
    initialize();
});