// ==========================================
// MOCK DUOMENYS (Pakaitalas API užklausoms)
// ==========================================
const mockTagsData = {
    "tlp": [
        "{'tlp:clear', 'You can share this with anyone, without restriction.'}",
        "{'tlp:green', 'You can share this with members of your organization only.'}",
        "{'tlp:amber', 'You can share this with members of your organization and other organizations you trust.'}",
        "{'tlp:red', 'You can share this with members of your organization only.'}"
    ],
    "threat_level": [
        "{'cert-ist:threat_level=\"high\"', 'High severity threat that requires immediate attention.'}",
        "{'cert-ist:threat_level=\"medium\"', 'Medium severity threat that requires monitoring.'}",
        "{'cert-ist:threat_level=\"low\"', 'Low severity threat that requires minimal attention.'}"
    ],
    "malware_action": [
        "{'veris:action:malware:variety=\"Backdoor\"', 'Allows unauthorized access to a computer.'}",
        "{'veris:action:malware:variety=\"Ransomware\"', 'Encrypts files and demands payment.'}"
    ],
    "hacking_action": [
        "{'veris:action:hacking:variety=\"Brute force\"', 'Trying many possible passwords.'}",
        "{'veris:action:hacking:variety=\"SQLi\"', 'Exploits vulnerabilities in SQL databases.'}"
    ]
};

const mockGalaxiesData = {
    "mitre_attack": [
        "{'misp-galaxy:mitre-attack-pattern=\"Phishing - T1566\"', 'Tricking individuals into providing info.'}",
        "{'misp-galaxy:mitre-attack-pattern=\"Brute Force - T1110\"', 'Trying many passwords to gain access.'}"
    ],
    "country": [
        "misp-galaxy:country=\"lithuania\"",
        "misp-galaxy:country=\"estonia\""
    ],
    "sector": [
        "misp-galaxy:sector=\"Higher education\"",
        "misp-galaxy:sector=\"Financial services\""
    ]
};

// ==========================================
// KONSTANTOS IR KONFIGŪRACIJA
// ==========================================
let selectedTags = [];
let selectedGalaxies = [];

const MAX_TAGS = 10;
const MAX_GALAXIES = 10;

const categoryLabels = {
    'tlp': '🔴 TLP',
    'threat_level': '🚨 Threat Level',
    'malware_action': '🦠 Malware',
    'hacking_action': '⚡ Hacking',
    'mitre_attack': '🎯 MITRE ATT&CK',
    'country': '📍 Country',
    'sector': '🏢 Sector'
};

const distributionLabels = { 0: 'Your Organisation Only', 1: 'This community only', 2: 'Connected communities', 3: 'All communities' };
const threatLevelLabels = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Undefined' };
const analysisLabels = { 0: 'Initial', 1: 'Ongoing', 2: 'Completed' };

// ==========================================
// PAGALBINĖS FUNKCIJOS
// ==========================================

function parsePythonSet(setString) {
    if (typeof setString !== 'string' || !setString.startsWith('{')) {
        return { value: setString, description: "" };
    }
    const parts = setString.replace(/[{}]/g, "").split(/', '|", "/);
    let val1 = parts[0].replace(/['"]/g, "").trim();
    let val2 = parts[1] ? parts[1].replace(/['"]/g, "").trim() : "";

    if (val2 && !val1.includes(':') && !val1.includes('=') && (val2.includes(':') || val2.includes('='))) {
        return { value: val2, description: val1 };
    }
    return { value: val1, description: val2 };
}

function formatTagName(tag) {
    if (!tag) return "";
    if (tag.includes('=')) {
        const match = tag.match(/"(.+?)"/);
        if (match) return match[1].charAt(0).toUpperCase() + match[1].slice(1);
    }
    if (tag.includes(':')) {
        const lastPart = tag.split(':').pop();
        return lastPart.charAt(0).toUpperCase() + lastPart.slice(1);
    }
    return tag;
}

function formatGalaxyName(galaxy) {
    if (!galaxy) return "";
    const match = galaxy.match(/"(.+?)"/);
    if (match) return match[1];
    if (galaxy.includes(':')) return galaxy.split(':').pop();
    return galaxy;
}

function escapeJs(text) {
    if (!text) return "";
    return text.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

// ==========================================
// RENDERINIMO FUNKCIJOS
// ==========================================

function renderNestedDropdown(containerId, data, typeLabel, targetListId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `
        <div class="dropdown">
            <button class="btn btn-white border w-100 dropdown-toggle shadow-sm d-flex justify-content-between align-items-center" 
                    type="button" data-bs-toggle="dropdown" style="border-radius: 12px;">
                Pasirinkti ${typeLabel}
            </button>
            <ul class="dropdown-menu w-100 shadow-lg border-0">`;

    for (const [category, items] of Object.entries(data)) {
        const label = categoryLabels[category] || category.toUpperCase();
        html += `
            <li class="dropend">
                <a class="dropdown-item dropdown-toggle d-flex justify-content-between align-items-center py-2" href="#">
                    ${label}
                </a>
                <ul class="dropdown-menu shadow-lg border-0">`;
        
        items.forEach(rawItem => {
            const { value, description } = parsePythonSet(rawItem);
            const formatted = typeLabel === 'Tags' ? formatTagName(value) : formatGalaxyName(value);
            html += `<li>
                <a class="dropdown-item small py-2" href="#" 
                   data-bs-toggle="tooltip" data-bs-placement="right" title="${escapeJs(description)}"
                   onclick="addItem('${escapeJs(value)}', '${targetListId}')">
                   ${formatted}
                </a>
            </li>`;
        });
        html += `</ul></li>`;
    }
    html += `</ul></div>`;
    container.innerHTML = html;
}

function addItem(value, listType) {
    const isTag = listType === 'selectedTags';
    const list = isTag ? selectedTags : selectedGalaxies;
    const max = isTag ? MAX_TAGS : MAX_GALAXIES;

    if (list.includes(value)) return;
    if (list.length >= max) return;

    list.push(value);
    renderBadges(listType);
}

function renderBadges(listType) {
    const container = document.getElementById(listType);
    const list = listType === 'selectedTags' ? selectedTags : selectedGalaxies;
    const isTag = listType === 'selectedTags';

    if (list.length === 0) {
        container.innerHTML = '<small class="text-muted w-100 text-center">Nieko nepasirinkta</small>';
        return;
    }

    container.innerHTML = list.map((item, index) => `
        <div class="misp-badge">
            <span class="val">${isTag ? formatTagName(item) : formatGalaxyName(item)}</span>
            <span class="remove" onclick="removeItem(${index}, '${listType}')">×</span>
        </div>
    `).join('');
}

function removeItem(index, listType) {
    if (listType === 'selectedTags') {
        selectedTags.splice(index, 1);
    } else {
        selectedGalaxies.splice(index, 1);
    }
    renderBadges(listType);
}

// ==========================================
// INICIJAVIMAS (DOM READY)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Užkrauname paprastus dropdown'us
    // Pridėkite šias eilutes į loadData() funkciją po galaxiesData gavimo:

// Mock duomenys paprastiems dropdown'ams
    const distributionLabels = { 0: 'Your Organisation Only', 1: 'This community only', 2: 'Connected communities', 3: 'All communities' };
    const threatLevelLabels = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Undefined' };
    const analysisLabels = { 0: 'Initial', 1: 'Ongoing', 2: 'Completed' };

    // Iškviečiame generavimo funkciją metaduomenims
    renderSimpleDropdown('distributionDropdownRoot', distributionLabels, 'Distribution');
    renderSimpleDropdown('threatLevelDropdownRoot', threatLevelLabels, 'Threat Level');
    renderSimpleDropdown('analysisDropdownRoot', analysisLabels, 'Analysis');

    // Taip pat įsitikinkite, kad kviečiate Tags ir Galaxies generavimą:
    renderNestedDropdown('tagsDropdownRoot', tagsData, 'Tags', 'selectedTags');
    renderNestedDropdown('galaxyDropdownRoot', galaxiesData, 'Galaxies', 'selectedGalaxies');
    
    // Suaktyviname Tooltipus
    setTimeout(() => {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(t => new bootstrap.Tooltip(t));
    }, 500);
});

function renderSimpleDropdown(containerId, labels, typeLabel) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `<select class="form-select shadow-sm" style="border-radius: 12px;">
        <option selected disabled>Pasirinkti ${typeLabel}...</option>`;
    
    for (const [value, label] of Object.entries(labels)) {
        html += `<option value="${value}">${label}</option>`;
    }
    
    html += `</select>`;
    container.innerHTML = html;
}