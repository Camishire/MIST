let selectedTags = [];
let selectedGalaxies = [];

const MAX_TAGS = 5;
const MAX_GALAXIES = 7;

const categoryLabels = {
    'tlp': '🔴 TLP',
    'threat_level': '🚨 Threat Level',
    'source_type': '🔍 Source',
    'workflow': '📊 Workflow',
    'malware_action': '🦠 Malware',
    'hacking_action': '⚡ Hacking',
    'social_action': '🎭 Social',
    'admiralty_scale': '⭐ Admiralty',
    'country': '📍 Country',
    'sector': '🏢 Sector',
    'mitre_attack': '🎯 MITRE ATT&CK',
    'threat_actor': '👤 Actor',
    'ransomware': '🔒 Ransomware',
    'tool': '🔧 Tool',
    'malware': '🦠 Malware'
};

const distributionLabels = {
    0: 'Your Organisation Only',
    1: 'This community only',
    2: 'Connected communities',
    3: 'All communities',
    4: 'Sharing group',
}

const threatLevelLabels = {
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Undefined'
};

const analysisLabels = {
    0: 'Initial',
    1: 'Ongoing',
    2: 'Completed'
};

/**
 * Pagalbinė funkcija ištraukti duomenis iš Python set stringo: "{'val', 'desc'}"
 */
function parsePythonSet(setString) {
    if (typeof setString !== 'string' || !setString.startsWith('{')) {
        return { value: setString, description: "" };
    }
    // Pašaliname skliaustelius ir suskaldome pagal kabutes
    const parts = setString.replace(/[{}]/g, "").split(/', '|", "/);
    let val1 = parts[0].replace(/['"]/g, "").trim();
    let val2 = parts[1] ? parts[1].replace(/['"]/g, "").trim() : "";

    // Logika: MISP reikšmė paprastai turi ":" arba "="
    if (val2 && !val1.includes(':') && !val1.includes('=') && (val2.includes(':') || val2.includes('='))) {
        return { value: val2, description: val1 };
    }
    return { value: val1, description: val2 };
}

async function loadData() {
    try {
        const [tagsRes, galaxiesRes] = await Promise.all([
            fetch('/api/tags/categories'),
            fetch('/api/galaxies/categories')
        ]);

        const tagsData = await tagsRes.json();
        const galaxiesData = await galaxiesRes.json();

        renderNestedDropdown('tagsDropdownRoot', tagsData, 'Tags', 'selectedTags');
        renderNestedDropdown('galaxyDropdownRoot', galaxiesData, 'Galaxies', 'selectedGalaxies');

        // Inicijuojame Bootstrap Tooltipus po to, kai sugeneruojame HTML
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        renderSimpleDropdown('distributionDropdownRoot', distributionLabels, 'Distribution');
        renderSimpleDropdown('threatLevelDropdownRoot', threatLevelLabels, 'Threat Level');
        renderSimpleDropdown('analysisDropdownRoot', analysisLabels, 'Analysis');

    } catch (error) {
        console.error('Klaida kraunant duomenis:', error);
    }
}

function renderNestedDropdown(containerId, data, typeLabel, targetListId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `
        <div class="dropdown">
            <button class="btn btn-white border w-100 dropdown-toggle shadow-sm d-flex justify-content-between align-items-center" 
                    type="button" data-bs-toggle="dropdown" data-bs-boundary="viewport" style="border-radius: 12px;">
                Pasirinkti ${typeLabel}
            </button>
            <ul class="dropdown-menu w-100 shadow-lg border-0">`;

    for (const [category, items] of Object.entries(data)) {
        const label = categoryLabels[category] || category.replace(/_/g, ' ').toUpperCase();
        
        html += `
            <li class="dropend">
                <a class="dropdown-item dropdown-toggle d-flex justify-content-between align-items-center py-2" href="#">
                    ${label}
                </a>
                <ul class="dropdown-menu shadow-lg border-0">`;
        
        items.forEach(rawItem => {
            const { value, description } = parsePythonSet(rawItem);
            const formattedName = typeLabel === 'Tags' ? formatTagName(value) : formatGalaxyName(value);
            
            html += `<li>
                <a class="dropdown-item small py-2" href="#" 
                   data-bs-toggle="tooltip" 
                   data-bs-placement="right" 
                   title="${escapeJs(description)}"
                   onclick="addItem('${escapeJs(value)}', '${targetListId}')">
                   ${formattedName}
                </a>
            </li>`;
        });

        html += `</ul></li>`;
    }

    html += `</ul></div>`;
    container.innerHTML = html;
}

function renderSimpleDropdown(containerId, labels, typeLabel) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `
        <select class="form-select shadow-sm" style="border-radius: 12px;">
            <option selected disabled>Pasirinkti ${typeLabel}</option>`;

    for (const [value, label] of Object.entries(labels)) {
        html += `<option value="${value}">${label}</option>`;
    }

    html += `</select>`;
    container.innerHTML = html;
}

function addItem(value, listType) {
    const isTag = listType === 'selectedTags';
    const list = isTag ? selectedTags : selectedGalaxies;
    const max = isTag ? MAX_TAGS : MAX_GALAXIES;

    if (list.includes(value)) return;
    if (list.length >= max) {
        alert(`Maksimalus kiekis (${max}) pasiektas!`);
        return;
    }

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

/**
 * Formatuoja Tagų pavadinimus (pvz., tlp:clear -> Clear)
 */
function formatTagName(tag) {
    if (!tag) return "";

    // Jei yra lygybės ženklas (pvz., cert-ist:threat_level="high")
    if (tag.includes('=')) {
        const parts = tag.split('=');
        const value = parts[parts.length - 1];
        // Pašaliname kabutes jei yra
        const cleanValue = value.replace(/^"|"$/g, '');
        return cleanValue.toUpperCase();
    }

    // Jei yra tik dvitaškis (pvz., tlp:amber+strict)
    if (tag.includes(':')) {
        const parts = tag.split(':');
        const value = parts[parts.length - 1];
        const cleanValue = value.replace(/^"|"$/g, '');
        return cleanValue.toUpperCase();
    }

    return tag;
}

/**
 * Formatuoja Galaxy pavadinimus (pvz., misp-galaxy:sector="Higher education" -> Higher education)
 */
function formatGalaxyName(galaxy) {
    if (!galaxy) return "";

    const match = galaxy.match(/"(.+?)"/);

    if (galaxy.includes('=')) {
        const parts = galaxy.split('=');
        const value = parts[parts.length - 1];
        // Pašaliname kabutes jei yra
        const cleanValue = value.replace(/^"|"$/g, '');
        return cleanValue.toUpperCase();
    }

    // Jei kabučių nėra, paimame paskutinę dalį po dvitaškio
    if (galaxy.includes(':')) {
        return galaxy.split(':').pop();
    }

    return galaxy;
}

function escapeJs(text) {
    if (!text) return "";
    return text.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

document.addEventListener('DOMContentLoaded', loadData);