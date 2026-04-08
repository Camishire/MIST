const submitBtn = document.getElementById('submitBtn');

if (submitBtn) {
    console.log('✅ Submit button found, attaching listener');
    submitBtn.addEventListener('click', handleEventSubmit);
} else {
    console.error('❌ Submit button NOT found!');
}

async function handleEventSubmit() {
    console.log('🚀 Submitting MISP event...');
    
    // Collect all form data
    const eventData = collectFormData();
    
    // Validate
    if (!validateEventData(eventData)) {
        return;
    }
    
    // Show loading state
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '⏳ Creating...';
    
    try {
        const response = await fetch('/events/create', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-Key': MIST_CONFIG.API_KEY
            },
            body: JSON.stringify(eventData)
        });
        
        if (response.status === 403) {
            alert('❌ Authentication failed: Invalid API Key');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            return;
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✅ Event created successfully!\n\nEvent ID: ${result.event_id}\n\nOpening in MISP...`);
            // Open MISP event in new tab
            window.open(result.url, '_blank');
            
            // Reset form
            resetForm();
        } else {
            alert(`❌ Failed to create event: ${result.message || 'Unknown error'}`);
        }
        
    } catch (error) {
        console.error('❌ Submission error:', error);
        alert(`❌ Error: ${error.message}`);
    } finally {
        // Restore button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// ============================================
// COLLECT FORM DATA
// ============================================

function collectFormData() {
    // Event metadata
    const eventDate = document.getElementById('eventDate').value;
    const distribution = parseInt(document.getElementById('distributionSelect').value);
    const threatLevel = parseInt(document.getElementById('threatLevelSelect').value);
    const creatorKey = document.getElementById('creatorSelect').value; // PATAISYTA: creator → creator_key
    const analysis = parseInt(document.getElementById('analysisSelect').value);
    const eventInfo = document.getElementById('eventInfo').value;
    
    // Tags and galaxies from BadgeManager
    const tags = selectedTags || [];
    const galaxies = selectedGalaxies || [];
    
    // Attributes from table
    const attributes = collectTableAttributes();
    
    return {
        creator_key: creatorKey, // PATAISYTA: creator → creator_key
        date: eventDate,
        distribution: distribution,
        threat_level_id: threatLevel,
        analysis: analysis,
        info: eventInfo,
        tags: tags,
        galaxies: galaxies,
        attributes: attributes
    };
}

// ============================================
// COLLECT TABLE ATTRIBUTES
// ============================================

function collectTableAttributes() {
    const tbody = document.getElementById('attrTableBody');
    const rows = tbody.querySelectorAll('tr');
    const attributes = [];
    
    rows.forEach(row => {
        // Skip empty placeholder row
        if (row.querySelector('td[colspan]')) {
            return;
        }
        
        const dateInput = row.querySelector('td:nth-child(1) input');
        const categorySelect = row.querySelector('td:nth-child(2) select');
        const typeSelect = row.querySelector('td:nth-child(3) select');
        const valueInput = row.querySelector('td:nth-child(4) input');
        const commentTextarea = row.querySelector('td:nth-child(5) textarea');

        if (categorySelect && typeSelect && valueInput && valueInput.value.trim()) {
            attributes.push({
                category: categorySelect.value,
                type: typeSelect.value,
                value: valueInput.value.trim(),
                comment: commentTextarea ? commentTextarea.value.trim() : '',
                to_ids: false
            });
        }
    });
    
    return attributes;
}

// ============================================
// VALIDATION
// ============================================

function validateEventData(data) {
    // Check creator key
    if (!data.creator_key || data.creator_key.trim() === '') {
        alert('❌ Please select creator');
        return false;
    }
    
    // Check required fields
    if (!data.date) {
        alert('❌ Please select event date');
        return false;
    }
    
    if (isNaN(data.distribution) || data.distribution === '') {
        alert('❌ Please select distribution level');
        return false;
    }
    
    if (isNaN(data.threat_level_id) || data.threat_level_id === '') {
        alert('❌ Please select threat level');
        return false;
    }
    
    if (isNaN(data.analysis) || data.analysis === '') {
        alert('❌ Please select analysis status');
        return false;
    }
    
    if (!data.info || data.info.trim() === '') {
        alert('❌ Please enter event description');
        return false;
    }
    
    if (data.attributes.length === 0) {
        alert('❌ Please add at least one attribute');
        return false;
    }
    
    return true;
}

// ============================================
// RESET FORM
// ============================================

function resetForm() {
    // Reset date
    document.getElementById('eventDate').valueAsDate = new Date();
    
    // Reset dropdowns
    document.getElementById('distributionSelect').selectedIndex = 0;
    document.getElementById('creatorSelect').selectedIndex = 0; // Reset creator
    document.getElementById('threatLevelSelect').selectedIndex = 0;
    document.getElementById('analysisSelect').selectedIndex = 0;
    
    // Reset event info
    document.getElementById('eventInfo').value = '';
    
    // Clear badges
    selectedTags = [];
    selectedGalaxies = [];
    renderBadges('selectedTags');
    renderBadges('selectedGalaxies');
    
    // Clear table
    const tbody = document.getElementById('attrTableBody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5 text-muted small">Lentelė tuščia. Pridėkite atributų.</td></tr>';
    
    // Clear bulk textarea
    document.getElementById('bulkGrabberTextarea').value = '';
}

console.log('✅ EventSubmit.js loaded!');