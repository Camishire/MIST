// ============================================
// DROPDOWN RENDERING
// ============================================

function renderSimpleDropdown(containerId, options, typeLabel, selectedId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return;
    }

    let html = `
        <select class="form-select shadow-sm" id="${selectedId}" style="border-radius: 12px;">
            <option value="" selected disabled>Pasirinkti ${typeLabel}...</option>`;
    
    const entries = Object.entries(options);
    
    entries.forEach(([value, label]) => {
        html += `<option value="${value}">${label}</option>`;
    });
    
    html += `</select>`;
    container.innerHTML = html;
}

function renderNestedDropdown(containerId, data, typeLabel, targetListId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const categoryLabels = {
        'tlp': '🔴 TLP',
        'threat_level': '🚨 Threat Level',
        'malware_action': '🦠 Malware',
        'hacking_action': '⚡ Hacking',
        'social_action': '🎭 Social',
        'country': '📍 Country',
        'sector': '🏢 Sector',
        'mitre_attack': '🎯 MITRE ATT&CK'
    };

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
            let value, description;
            
            if (Array.isArray(rawItem)) {
                value = rawItem[0];
                description = rawItem[1] || '';
            } else {
                value = rawItem;
                description = '';
            }
            
            const formatted = typeLabel === 'Tags' ? formatTagName(value) : formatGalaxyName(value);
            
            html += `<li>
                <a class="dropdown-item small py-2" href="#" 
                   ${description ? `data-bs-toggle="tooltip" data-bs-placement="right" title="${escapeHtml(description)}"` : ''}
                   onclick="addItem('${escapeJs(value)}', '${targetListId}'); return false;">
                   ${formatted}
                </a>
            </li>`;
        });
        
        html += `</ul></li>`;
    }
    html += `</ul></div>`;
    container.innerHTML = html;
    
    // Initialize tooltips AFTER rendering
    setTimeout(() => {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
    }, 100);
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function formatTagName(tag) {
    if (tag.includes('=')) {
        const match = tag.match(/"(.+?)"/);
        return match ? match[1].toUpperCase() : tag;
    }
    return tag.split(':').pop().toUpperCase();
}

function formatGalaxyName(galaxy) {
    const match = galaxy.match(/"(.+?)"/);
    return match ? match[1] : galaxy;
}

function escapeJs(text) {
    if (!text) return "";
    return text.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}

function escapeHtml(text) {
    if (!text) return "";
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

console.log('✅ Dropdowns.js loaded!');