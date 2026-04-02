// ============================================
// BULK UPLOAD - Complete Handler with EDITABLE ROWS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 BulkGrabber.js loaded!');
    
    const bulkBtn = document.getElementById('BulkUploadbtn');
    
    if (bulkBtn) {
        console.log('✅ Attaching click handler to button');
        bulkBtn.addEventListener('click', handleBulkUpload);
    } else {
        console.error('❌ Button not found!');
    }
});

async function handleBulkUpload() {
    console.log('🚀 handleBulkUpload called!');
    
    const textarea = document.getElementById('bulkGrabberTextarea');
    const lines = textarea.value.split('\n')
        .map(l => l.trim())
        .filter(l => l && !l.startsWith('#'));
    
    if (lines.length === 0) {
        alert('Įveskite bent vieną eilutę!');
        return;
    }
    
    try {
        const response = await fetch('/api/bulk-upload', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ips: lines })
        });
        
        const data = await response.json();
        console.log('📦 Response data:', data);
        
        if (data.attributes && data.attributes.length > 0) {
            await populateEditableTable(data.attributes);
            alert(`✅ Imported ${data.count} attributes!`);
            textarea.value = '';
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
        alert('❌ Failed to upload: ' + error.message);
    }
}

// ============================================
// POPULATE EDITABLE TABLE
// ============================================

async function populateEditableTable(attributes) {
    const tbody = document.getElementById('attrTableBody');
    
    if (!tbody) {
        console.error('❌ Table body not found!');
        return;
    }
    
    // Fetch categories using APIgetter function
    const categoriesData = await getAllCategories();
    const categories = categoriesData.categories || [];
    
    // Clear table
    tbody.innerHTML = '';
    
    // Add editable rows
    for (const attr of attributes) {
        const row = await createEditableRow(attr, categories);
        tbody.appendChild(row);
    }
    
    console.log('✅ Table populated with editable rows!');
}

// ============================================
// CREATE EDITABLE ROW
// ============================================

async function createEditableRow(attr, categories) {
    const tr = document.createElement('tr');
    
    // Date input
    const tdDate = document.createElement('td');
    tdDate.innerHTML = `
        <input type="date" class="form-control form-control-sm" 
               style="border-radius: 8px; font-size: 0.85rem;"
               value="${new Date().toISOString().split('T')[0]}">
    `;
    tr.appendChild(tdDate);
    
    // Category dropdown
    const tdCategory = document.createElement('td');
    const categorySelect = document.createElement('select');
    categorySelect.className = 'form-select form-select-sm';
    categorySelect.style.cssText = 'border-radius: 8px; font-size: 0.85rem;';
    
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        option.selected = (cat === attr.category);
        categorySelect.appendChild(option);
    });
    
    // On category change, update type dropdown
    categorySelect.addEventListener('change', async function() {
        const typeSelect = tr.querySelector('td:nth-child(3) select');
        await updateTypeDropdown(typeSelect, this.value);
    });
    
    tdCategory.appendChild(categorySelect);
    tr.appendChild(tdCategory);
    
    // Type dropdown
    const tdType = document.createElement('td');
    const typeSelect = document.createElement('select');
    typeSelect.className = 'form-select form-select-sm';
    typeSelect.style.cssText = 'border-radius: 8px; font-size: 0.85rem;';
    
    // Fetch types for current category
    await updateTypeDropdown(typeSelect, attr.category, attr.type);
    
    tdType.appendChild(typeSelect);
    tr.appendChild(tdType);
    
    // Value input (editable)
    const tdValue = document.createElement('td');
    tdValue.innerHTML = `
        <input type="text" class="form-control form-control-sm" 
               style="border-radius: 8px; font-size: 0.85rem;"
               value="${escapeHtml(attr.value)}">
    `;
    tr.appendChild(tdValue);
    
    // Action (delete button)
    const tdAction = document.createElement('td');
    tdAction.className = 'text-end';
    tdAction.innerHTML = `
        <button class="btn btn-sm btn-danger" 
                style="border-radius: 8px; padding: 4px 10px;"
                onclick="this.closest('tr').remove()">
            ×
        </button>
    `;
    tr.appendChild(tdAction);
    
    return tr;
}

// ============================================
// UPDATE TYPE DROPDOWN
// ============================================

async function updateTypeDropdown(selectElement, category, selectedType = null) {
    const data = await getTypesForCategory(category);
    const types = data.types || [];
    
    // Clear existing options
    selectElement.innerHTML = '';
    
    // Add new options
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        option.selected = (type === selectedType);
        selectElement.appendChild(option);
    });
}

// ============================================
// HELPER: Escape HTML
// ============================================

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}