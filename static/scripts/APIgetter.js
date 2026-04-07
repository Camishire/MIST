// ============================================
// API GETTER - All GET requests
// ============================================

async function getDistributionOptions() {
    try {
        const response = await fetch('/api/distribution');
        const data = await response.json();
        return data.options || {};
    } catch (error) {
        console.error('Error fetching distribution:', error);
        return {};
    }
}

async function getThreatLevelOptions() {
    try {
        const response = await fetch('/api/threat-level');
        const data = await response.json();
        return data.options || {};
    } catch (error) {
        console.error('Error fetching threat level:', error);
        return {};
    }
}

async function getAnalysisOptions() {
    try {
        const response = await fetch('/api/analysis');
        const data = await response.json();
        return data.options || {};
    } catch (error) {
        console.error('Error fetching analysis:', error);
        return {};
    }
}

async function getTagsCategories() {
    try {
        const response = await fetch('/api/tags/categories');
        return await response.json();
    } catch (error) {
        console.error('Error fetching tags:', error);
        return {};
    }
}

async function getGalaxiesCategories() {
    try {
        const response = await fetch('/api/galaxies/categories');
        return await response.json();
    } catch (error) {
        console.error('Error fetching galaxies:', error);
        return {};
    }
}

async function getAllCategories() {
    try {
        const response = await fetch('/api/categories');
        return await response.json();
    } catch (error) {
        console.error('Error fetching categories:', error);
        return { categories: [] };
    }
}

async function getTypesForCategory(category) {
    try {
        const response = await fetch(`/api/categories/${encodeURIComponent(category)}/types`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching types for category ${category}:`, error);
        return { types: [] };
    }
}

async function getAbuseIPDBData(ip) {
    try {
        const response = await fetch(`/api/check-abuseipdb/${encodeURIComponent(ip)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('AbuseIPDB data:', data);
        return data;
    } catch (error) {
        console.error(`Error fetching AbuseIPDB data for ${ip}:`, error);
        throw error;
    }
}

async function getAbuseIPDBBulkData(ips) {
    try {
        const response = await fetch(`/api/check-abuseipdb/bulk?ips=${encodeURIComponent(ips.join(","))}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('AbuseIPDB bulk data:', data);
        return data;
    } catch (error) {
        console.error(`Error fetching AbuseIPDB bulk data:`, error);
        throw error;
    }
}

console.log('✅ APIgetter.js loaded!');