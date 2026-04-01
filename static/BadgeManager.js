// ============================================
// BADGE MANAGEMENT
// ============================================

let selectedTags = [];
let selectedGalaxies = [];

const MAX_TAGS = 5;
const MAX_GALAXIES = 7;

function addItem(value, targetListId) {
    const isTag = targetListId === 'selectedTags';
    const list = isTag ? selectedTags : selectedGalaxies;
    const max = isTag ? MAX_TAGS : MAX_GALAXIES;
    
    // Check for duplicates
    if (list.includes(value)) {
        alert('Šis elementas jau pridėtas!');
        return false;
    }
    
    // Check max limit
    if (list.length >= max) {
        alert(`Maksimalus kiekis (${max}) pasiektas!`);
        return false;
    }
    
    // Add to array
    list.push(value);
    
    // Re-render badges
    renderBadges(targetListId);
    
    return false; // Prevent default link behavior
}

function removeItem(index, listType) {
    if (listType === 'selectedTags') {
        selectedTags.splice(index, 1);
        renderBadges('selectedTags');
    } else {
        selectedGalaxies.splice(index, 1);
        renderBadges('selectedGalaxies');
    }
}

function renderBadges(listId) {
    const container = document.getElementById(listId);
    if (!container) return;
    
    const isTag = listId === 'selectedTags';
    const list = isTag ? selectedTags : selectedGalaxies;
    
    // Empty state
    if (list.length === 0) {
        const emptyText = isTag ? 'Pasirinkite žymes iš sąrašo' : 'Pasirinkite galaktikas';
        container.innerHTML = `<small class="text-muted w-100 text-center">${emptyText}</small>`;
        return;
    }
    
    // Render badges
    container.innerHTML = list.map((value, index) => {
        const formatted = isTag ? formatTagName(value) : formatGalaxyName(value);
        return `
            <div class="misp-badge">
                <span class="val">${formatted}</span>
                <span class="remove" onclick="removeItem(${index}, '${listId}')">×</span>
            </div>
        `;
    }).join('');
}

// Helper functions (if not already defined)
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