// ============================================
// BULK UPLOAD - Complete Handler with EDITABLE ROWS
// ============================================

console.log('🔍 BulkGrabber.js loaded!');

const bulkBtn = document.getElementById('BulkUploadbtn');

if (bulkBtn) {
    console.log('✅ Attaching click handler to BulkUploadbtn');
    bulkBtn.addEventListener('click', handleBulkUpload);
} else {
    console.error('❌ BulkUploadbtn not found!');
}

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
            headers: { 
                'Content-Type': 'application/json',
                'X-API-Key': MIST_CONFIG.API_KEY
            },
            body: JSON.stringify({ ips: lines })
        });
        
        if (response.status === 403) {
            alert('❌ Authentication failed: Invalid API Key');
            return;
        }
        
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

    // Comment field with auto-resize textarea
    const tdComment = document.createElement('td');
    tdComment.innerHTML = `
        <div style="display: flex; align-items: start; gap: 4px;">
            <textarea class="form-control form-control-sm auto-resize-textarea" 
                style="border-radius: 8px; font-size: 0.85rem; resize: none; overflow: hidden; min-height: 31px; line-height: 1.4;"
                placeholder="Optional comment..."
                rows="1"></textarea>
            <button class="btn btn-sm btn-outline-secondary abuse-check-btn"
                style="border-radius: 8px; font-size: 0.85rem; flex-shrink: 0; height: 31px;"
                title="AbuseIPDB enrichment">
                ⭐
            </button>
        </div>
    `;
    tr.appendChild(tdComment);

    // Auto-resize functionality
    const commentTextarea = tdComment.querySelector('.auto-resize-textarea');
    commentTextarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    // AbuseIPDB button handler
    const abuseCheckBtn = tdComment.querySelector('.abuse-check-btn');
    abuseCheckBtn.addEventListener('click', async function() {
        const ip = tdValue.querySelector('input').value.trim();
        if (!ip) {
            alert('Please enter an IP address to check!');
            return;
        }
        
        // Show loading state
        const originalHTML = abuseCheckBtn.innerHTML;
        abuseCheckBtn.disabled = true;
        abuseCheckBtn.innerHTML = '⏳';
        
        try {
            const result = await getAbuseIPDBData(ip);
            
            if (result.error) {
                commentTextarea.value = `AbuseIPDB error: ${result.error}`;
            } else {
                const score = result.abuseConfidenceScore || 0;
                const reports = result.totalReports || 0;
                const country = result.countryCode || 'N/A';
                
                commentTextarea.value = `Abuse: ${score}%, Reports: ${reports}, Country: ${country}`;
            }
            
            // Trigger auto-resize after setting value
            commentTextarea.style.height = 'auto';
            commentTextarea.style.height = commentTextarea.scrollHeight + 'px';
            
        } catch (error) {
            console.error('Error checking AbuseIPDB:', error);
            commentTextarea.value = `Failed: ${error.message}`;
            commentTextarea.style.height = 'auto';
            commentTextarea.style.height = commentTextarea.scrollHeight + 'px';
        } finally {
            // Restore button
            abuseCheckBtn.disabled = false;
            abuseCheckBtn.innerHTML = originalHTML;
        }
    });
    
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

async function GetAbuseIPDBBulkdata(ips) {
    const abuseCheckBulkBtn = document.getElementById('AbuseIPDBBulk');
    abuseCheckBulkBtn.addEventListener('click', async function() {
        const ipList = ips.map(ip => ip.trim()).filter(ip => ip);
        if (ipList.length === 0) {
            alert('Please enter at least one IP address to check!');
            return;
        }

        abuseCheckBulkBtn.disabled = true;
        abuseCheckBulkBtn.innerHTML = '⏳'

        try{
            const result = await getAbuseIPDBBulkData(ipList);
            console.log('Bulk AbuseIPDB data:', result);
        } catch (error) {
            console.error('Error checking Bulk AbuseIPDB:', error);
        } finally {
            abuseCheckBulkBtn.disabled = false;
            abuseCheckBulkBtn.innerHTML = 'Check Bulk AbuseIPDB';

        }
        });

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