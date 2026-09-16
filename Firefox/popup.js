document.addEventListener('DOMContentLoaded', () => {
    const toggleSwitch = document.getElementById('toggle-switch');
    const statusText = document.querySelector('.status');
    const rulesContainer = document.querySelector('.rules');
    const rulesList = document.getElementById('rules-list');
    const addRuleBtn = document.getElementById('add-rule-btn');
    const oldDomainInput = document.getElementById('old-domain');
    const newDomainInput = document.getElementById('new-domain');
    const actionRadios = document.querySelectorAll('input[name="actionType"]');

    let customRules = [];

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
        
        oldDomainInput.placeholder = browser.i18n.getMessage('placeholderOldDomain');
        newDomainInput.placeholder = browser.i18n.getMessage('placeholderNewDomain');
    }

    function updateUI(isEnabled) {
        if (isEnabled) {
            statusText.textContent = browser.i18n.getMessage('popupStatusActive');
            statusText.classList.remove('inactive');
        } else {
            statusText.textContent = browser.i18n.getMessage('popupStatusInactive');
            statusText.classList.add('inactive');
        }
        rulesContainer.classList.toggle('disabled', !isEnabled);
        toggleSwitch.checked = isEnabled;
    }

    async function applyRulesToDNR(rules, isEnabled) {
        const existingRules = await browser.declarativeNetRequest.getDynamicRules();
        const existingIds = existingRules.map(r => r.id);
        
        const removeRuleIds = existingIds;
        const addRules = [];

        if (isEnabled) {
            rules.forEach(rule => {
                let action = { type: 'block' };
                if (rule.newDomain) {
                    action = {
                        type: 'redirect',
                        redirect: { transform: { scheme: 'https', host: rule.newDomain } }
                    };
                }
                addRules.push({
                    id: rule.id,
                    priority: 1,
                    action: action,
                    condition: {
                        requestDomains: [rule.oldDomain],
                        resourceTypes: ['main_frame', 'sub_frame', 'stylesheet', 'script', 'image', 'font', 'object', 'xmlhttprequest', 'ping', 'csp_report', 'media', 'websocket', 'other']
                    }
                });
            });
        }

        await browser.declarativeNetRequest.updateDynamicRules({ removeRuleIds, addRules });
    }

    function renderRulesList() {
        rulesList.innerHTML = '';
        customRules.forEach(rule => {
            const li = document.createElement('li');
            
            const details = document.createElement('span');
            details.className = 'rule-details';
            
            const source = document.createElement('span');
            source.className = 'domain-source';
            source.textContent = rule.oldDomain;
            details.appendChild(source);
            
            if (rule.newDomain) {
                const arrow = document.createElement('span');
                arrow.className = 'arrow';
                arrow.textContent = ' → ';
                
                const target = document.createElement('span');
                target.className = 'domain-target';
                target.textContent = rule.newDomain;
                
                details.appendChild(arrow);
                details.appendChild(target);
            } else {
                const blocked = document.createElement('span');
                blocked.className = 'status-blocked';
                blocked.textContent = browser.i18n.getMessage('ruleStatusBlocked');
                blocked.style.marginLeft = '8px';
                details.appendChild(blocked);
            }
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = browser.i18n.getMessage('buttonDelete') || 'Sil';
            deleteBtn.onclick = () => removeRule(rule.id);
            
            li.appendChild(details);
            li.appendChild(deleteBtn);
            rulesList.appendChild(li);
        });
    }

    actionRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'block') {
                newDomainInput.style.display = 'none';
            } else {
                newDomainInput.style.display = 'block';
            }
        });
    });

    async function addRule() {
        let oldDomain = oldDomainInput.value.trim().toLowerCase();
        let newDomain = newDomainInput.value.trim().toLowerCase();
        const actionType = document.querySelector('input[name="actionType"]:checked').value;
        
        if (!oldDomain) return;

        oldDomain = oldDomain.replace(/^https?:\/\//, '').split('/')[0];
        
        if (actionType === 'block') {
            newDomain = '';
        } else if (newDomain) {
            newDomain = newDomain.replace(/^https?:\/\//, '').split('/')[0];
        }

        let newId = 1;
        if (customRules.length > 0) {
            newId = Math.max(...customRules.map(r => r.id)) + 1;
        }

        const rule = { id: newId, oldDomain, newDomain };
        customRules.push(rule);
        
        await saveAndApplyRules();
        
        oldDomainInput.value = '';
        newDomainInput.value = '';
    }

    async function removeRule(id) {
        customRules = customRules.filter(r => r.id !== id);
        await saveAndApplyRules();
    }

    async function saveAndApplyRules() {
        await browser.storage.local.set({ customRules });
        const result = await browser.storage.local.get({ extensionEnabled: true });
        await applyRulesToDNR(customRules, result.extensionEnabled);
        renderRulesList();
    }

    toggleSwitch.addEventListener('change', async (event) => {
        const isEnabled = event.target.checked;
        await browser.storage.local.set({ extensionEnabled: isEnabled });
        await applyRulesToDNR(customRules, isEnabled);
        updateUI(isEnabled);
    });

    addRuleBtn.addEventListener('click', addRule);

    async function initialize() {
        const result = await browser.storage.local.get({ extensionEnabled: true, customRules: [] });
        const isEnabled = result.extensionEnabled;
        customRules = result.customRules;
        
        updateUI(isEnabled);
        await applyRulesToDNR(customRules, isEnabled);
        renderRulesList();
    }

    function displayVersion() {
        const manifest = browser.runtime.getManifest();
        const versionInfo = document.getElementById('version-info');
        if (versionInfo) {
            versionInfo.textContent = manifest.name + " v" + manifest.version;
        }
    }
    
    localizeHtmlPage();
    displayVersion();
    initialize();
});

