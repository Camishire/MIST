// ============================================
// BULK ABUSEIPDB ENRICHMENT HANDLER
// ============================================

console.log('🔍 BulkAbuseHandler.js loaded!');

const bulkAbuseBtn = document.getElementById('AbuseIPDBBulk');

if (bulkAbuseBtn) {
    console.log('✅ Bulk AbuseIPDB button found, attaching listener');
    bulkAbuseBtn.addEventListener('click', handleBulkAbuseEnrichment);
} else {
    console.error('❌ AbuseIPDBBulk button not found!');
}

async function handleBulkAbuseEnrichment() {
    console.log('🚀 Bulk enrichment started (AbuseIPDB + OpenCTI)');
    
    const tbody = document.getElementById('attrTableBody');
    const rows = tbody.querySelectorAll('tr');
    
    // Collect all IP addresses from ip-dst type attributes
    const ipRows = [];
    const ips = [];
    
    rows.forEach(row => {
        // Skip empty placeholder row
        if (row.querySelector('td[colspan]')) {
            return;
        }
        
        const typeSelect = row.querySelector('td:nth-child(3) select');
        const valueInput = row.querySelector('td:nth-child(4) input');
        
        // Check if type is ip-dst or ip-src
        if (typeSelect && valueInput) {
            const type = typeSelect.value;
            const value = valueInput.value.trim();
            
            if ((type === 'ip-dst' || type === 'ip-src') && value) {
                ipRows.push(row);
                ips.push(value);
            }
        }
    });
    
    if (ips.length === 0) {
        alert('❌ No IP attributes found in the table!');
        return;
    }
    
    // Show loading state
    const bulkBtn = document.getElementById('AbuseIPDBBulk');
    const originalHTML = bulkBtn.innerHTML;
    bulkBtn.disabled = true;
    bulkBtn.innerHTML = `⏳ (${ips.length})`;
    
    try {
        console.log(`📡 Fetching enrichment data for ${ips.length} IPs...`);
        const results = await getEnrichedDataForIndicators(ips);
        
        console.log('🔍 DEBUG: results type:', typeof results);
        console.log('🔍 DEBUG: Array.isArray(results):', Array.isArray(results));
        console.log('🔍 DEBUG: results:', results);
        
        // Check if results is actually an array
        if (!Array.isArray(results)) {
            console.error('❌ Results is not an array! Converting...');
            // Maybe it's wrapped in a property?
            const resultsArray = results.results || results.data || results;
            console.log('🔍 Trying to extract array:', resultsArray);
            
            // If still not array, just show error
            if (!Array.isArray(resultsArray)) {
                throw new Error('Backend did not return an array');
            }
            
            // Use the extracted array
            processResults(resultsArray, ipRows);
        } else {
            processResults(results, ipRows);
        }
        
    } catch (error) {
        console.error('❌ Bulk enrichment error:', error);
        alert(`❌ Failed to enrich IPs: ${error.message}`);
    } finally {
        // Restore button
        bulkBtn.disabled = false;
        bulkBtn.innerHTML = originalHTML;
    }
}

function processResults(results, ipRows) {
    // results is an array of combined enrichment objects
    const resultMap = {};
    results.forEach(result => {
        resultMap[result.ipAddress] = result;
    });
    
    // Update each row with the result
    let successCount = 0;
    ipRows.forEach(row => {
        const valueInput = row.querySelector('td:nth-child(4) input');
        const commentTextarea = row.querySelector('td:nth-child(5) textarea');
        
        if (valueInput && commentTextarea) {
            const ip = valueInput.value.trim();
            const result = resultMap[ip];
            
            if (result) {
                if (result.formatted_comment) {
                    commentTextarea.value = result.formatted_comment;
                    successCount++;
                } else if (result.error) {
                    commentTextarea.value = `Error: ${result.error}`;
                } else {
                    commentTextarea.value = 'No threat data found';
                }
                
                // Trigger auto-resize
                commentTextarea.style.height = 'auto';
                commentTextarea.style.height = commentTextarea.scrollHeight + 'px';
            }
        }
    });
}

console.log('✅ Bulk AbuseIPDB handler loaded!');