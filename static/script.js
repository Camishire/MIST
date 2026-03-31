let selectedTags = [];
let selectedGalaxies = [];

const MAX_TAGS = 5;
const MAX_GALAXIES = 7;

async function loadTagsAndGalaxies() {
    try {
        // Load tags
        const tagsResponse = await fetch('/api/tags/categories');
        const tagsData = await tagsResponse.json();
        populateTagsTabs(tagsData);
        
        // Load galaxies
        const galaxiesResponse = await fetch('/api/galaxies/categories');
        const galaxiesData = await galaxiesResponse.json();
        populateGalaxiesTabs(galaxiesData);
        
    } catch (error) {
        console.error('Error loading tags/galaxies:', error);
    }
}

// ============================================
// POPULATE TAGS TABS
// ============================================
function populateTagsTabs(categories) {
    const container = document.getElementById('tagsTabsContainer');
    
    const categoryNames = {
        'tlp': '🔴 TLP',
        'threat_level': '🚨 Threat',
        'source_type': '🔍 Source',
        'workflow': '📊 Workflow',
        'malware_action': '🦠 Malware',
        'hacking_action': '⚡ Hacking',
        'social_action': '🎭 Social',
        'admiralty_scale': '⭐ Admiralty'
    };
    
    let tabsHtml = '<ul class="nav nav-pills mb-2" role="tablist">';
    let contentHtml = '<div class="tab-content">';
    
    let isFirst = true;
    
    for (const [category, tags] of Object.entries(categories)) {
        const activeClass = isFirst ? 'active' : '';
        const showClass = isFirst ? 'show active' : '';
        
        // Tab button
        tabsHtml += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${activeClass}" id="tag-${category}-tab" data-bs-toggle="pill" 
                        data-bs-target="#tag-${category}" type="button" role="tab">
                    ${categoryNames[category] || category}
                </button>
            </li>
        `;
        
        // Tab content with dropdown
        contentHtml += `
            <div class="tab-pane fade ${showClass}" id="tag-${category}" role="tabpanel">
                <select class="form-select form-select-sm" id="tag-select-${category}">
                    <option value="">Choose ${categoryNames[category] || category}...</option>
        `;
        
        tags.forEach(tag => {
            contentHtml += `<option value="${escapeHtml(tag)}">${formatTagName(tag)}</option>`;
        });
        
        contentHtml += `
                </select>
                <button class="btn btn-primary btn-sm mt-2" onclick="addTagFromTab('${category}')">+ Add</button>
            </div>
        `;
        
        isFirst = false;
    }
    
    tabsHtml += '</ul>';
    contentHtml += '</div>';
    
    container.innerHTML = tabsHtml + contentHtml;
}

// ============================================
// POPULATE GALAXIES TABS
// ============================================
function populateGalaxiesTabs(categories) {
    const container = document.getElementById('galaxiesTabsContainer');
    
    const categoryNames = {
        'country': '📍 Country',
        'sector': '🏢 Sector',
        'mitre_attack': '🎯 MITRE',
        'threat_actor': '👤 Actor',
        'ransomware': '🔒 Ransomware',
        'tool': '🔧 Tool',
        'malware': '🦠 Malware'
    };
    
    let tabsHtml = '<ul class="nav nav-pills mb-2" role="tablist">';
    let contentHtml = '<div class="tab-content">';
    
    let isFirst = true;
    
    for (const [category, galaxies] of Object.entries(categories)) {
        const activeClass = isFirst ? 'active' : '';
        const showClass = isFirst ? 'show active' : '';
        
        tabsHtml += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${activeClass}" id="galaxy-${category}-tab" data-bs-toggle="pill" 
                        data-bs-target="#galaxy-${category}" type="button" role="tab">
                    ${categoryNames[category] || category}
                </button>
            </li>
        `;
        
        contentHtml += `
            <div class="tab-pane fade ${showClass}" id="galaxy-${category}" role="tabpanel">
                <select class="form-select form-select-sm" id="galaxy-select-${category}">
                    <option value="">Choose ${categoryNames[category] || category}...</option>
        `;
        
        galaxies.forEach(galaxy => {
            contentHtml += `<option value="${escapeHtml(galaxy)}">${formatGalaxyName(galaxy)}</option>`;
        });
        
        contentHtml += `
                </select>
                <button class="btn btn-primary btn-sm mt-2" onclick="addGalaxyFromTab('${category}')">+ Add</button>
            </div>
        `;
        
        isFirst = false;
    }
    
    tabsHtml += '</ul>';
    contentHtml += '</div>';
    
    container.innerHTML = tabsHtml + contentHtml;
}

// ============================================
// ADD TAG FROM TAB
// ============================================
function addTagFromTab(category) {
    const select = document.getElementById(`tag-select-${category}`);
    const tag = select.value;
    
    if (!tag) {
        alert('Please select a tag first!');
        return;
    }
    
    if (selectedTags.includes(tag)) {
        alert('This tag is already added!');
        return;
    }
    
    if (selectedTags.length >= MAX_TAGS) {
        alert(`Maximum ${MAX_TAGS} tags allowed!`);
        return;
    }
    
    selectedTags.push(tag);
    renderSelectedTags();
    select.value = ''; // Reset
}

// ============================================
// ADD GALAXY FROM TAB
// ============================================
function addGalaxyFromTab(category) {
    const select = document.getElementById(`galaxy-select-${category}`);
    const galaxy = select.value;
    
    if (!galaxy) {
        alert('Please select a galaxy first!');
        return;
    }
    
    if (selectedGalaxies.includes(galaxy)) {
        alert('This galaxy is already added!');
        return;
    }
    
    if (selectedGalaxies.length >= MAX_GALAXIES) {
        alert(`Maximum ${MAX_GALAXIES} galaxies allowed!`);
        return;
    }
    
    selectedGalaxies.push(galaxy);
    renderSelectedGalaxies();
    select.value = '';
}

// ============================================
// HELPER FUNCTIONS
// ============================================
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatTagName(tag) {
    if (tag.includes('=')) {
        const match = tag.match(/"(.+?)"/);
        return match ? match[1].charAt(0).toUpperCase() + match[1].slice(1) : tag;
    }
    return tag.split(':').pop().replace(/_/g, ' ').toUpperCase();
}

function formatGalaxyName(galaxy) {
    const match = galaxy.match(/"(.+?)"/);
    return match ? match[1] : galaxy;
}

// ============================================
// RENDER SELECTED TAGS
// ============================================
function renderSelectedTags() {
    const container = document.getElementById('selectedTags');
    
    if (selectedTags.length === 0) {
        container.innerHTML = '<small class="text-muted">Selected tags will appear here...</small>';
        return;
    }
    
    container.innerHTML = selectedTags.map((tag, index) => `
        <span class="tag-badge">
            ${formatTagName(tag)}
            <span class="badge-remove" onclick="removeTag(${index})">✕</span>
        </span>
    `).join('');
}

// ============================================
// RENDER SELECTED GALAXIES
// ============================================
function renderSelectedGalaxies() {
    const container = document.getElementById('selectedGalaxies');
    
    if (selectedGalaxies.length === 0) {
        container.innerHTML = '<small class="text-muted">Selected galaxies will appear here...</small>';
        return;
    }
    
    container.innerHTML = selectedGalaxies.map((galaxy, index) => `
        <span class="galaxy-badge">
            ${formatGalaxyName(galaxy)}
            <span class="badge-remove" onclick="removeGalaxy(${index})">✕</span>
        </span>
    `).join('');
}

// ============================================
// REMOVE TAG/GALAXY
// ============================================
function removeTag(index) {
    selectedTags.splice(index, 1);
    renderSelectedTags();
}

function removeGalaxy(index) {
    selectedGalaxies.splice(index, 1);
    renderSelectedGalaxies();
}

// ============================================
// LOAD ON PAGE READY
// ============================================
window.addEventListener('DOMContentLoaded', function() {
    loadTagsAndGalaxies();
});