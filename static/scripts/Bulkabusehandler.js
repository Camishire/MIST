console.log('BulkAbuseHandler.js loaded.');

const bulkAbuseBtn = document.getElementById('AbuseIPDBBulk');

if (bulkAbuseBtn) {
    bulkAbuseBtn.addEventListener('click', handleBulkAbuseEnrichment);
}

async function handleBulkAbuseEnrichment() {
    const tbody = document.getElementById('attrTableBody');
    const rows = tbody.querySelectorAll('tr');
    
    const ipRows = [];
    const ips = [];
    
    rows.forEach(row => {
        if (row.querySelector('td[colspan]')) {
            return;
        }
        
        const typeSelect = row.querySelector('td:nth-child(3) select');
        const valueInput = row.querySelector('td:nth-child(4) input');
        
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
        alert('No IP attributes found in the table!');
        return;
    }
    
    const bulkBtn = document.getElementById('AbuseIPDBBulk');
    const originalHTML = bulkBtn.innerHTML;
    bulkBtn.disabled = true;
    bulkBtn.innerHTML = `(${ips.length})`;
    
    try {
        console.log(`Fetching enrichment data for ${ips.length} IPs...`);
        const results = await getEnrichedDataForIndicators(ips);
        
        console.log('DEBUG: results type:', typeof results);
        console.log('DEBUG: Array.isArray(results):', Array.isArray(results));
        console.log('DEBUG: results:', results);
        
        if (!Array.isArray(results)) {
            console.error('Results is not an array! Converting...');
            const resultsArray = results.results || results.data || results;
            console.log('Trying to extract array:', resultsArray);
            
            if (!Array.isArray(resultsArray)) {
                throw new Error('Backend did not return an array');
            }
            
            processResults(resultsArray, ipRows);
        } else {
            processResults(results, ipRows);
        }
        
    } catch (error) {
        console.error('Bulk enrichment error:', error);
        alert(`Failed to enrich IPs: ${error.message}`);
    } finally {
        bulkBtn.disabled = false;
        bulkBtn.innerHTML = originalHTML;
    }
}

function processResults(results, ipRows) {
    const resultMap = {};
    results.forEach(result => {
        resultMap[result.ipAddress] = result;
    });
    
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
                
                commentTextarea.style.height = 'auto';
                commentTextarea.style.height = commentTextarea.scrollHeight + 'px';
            }
        }
    });
}

console.log('Bulk AbuseIPDB handler loaded!');