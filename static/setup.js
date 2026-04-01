// ============================================
// PAGE SETUP - Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing MIST Creator...');
    
    // Load all dropdowns
    await setupDistributionDropdown();
    await setupThreatLevelDropdown();
    await setupAnalysisDropdown();
    await setupTagsDropdown();
    await setupGalaxiesDropdown();
    
    console.log('✅ All dropdowns loaded!');
});

// ============================================
// DISTRIBUTION DROPDOWN
// ============================================
async function setupDistributionDropdown() {
    console.log('Setting up Distribution dropdown...');
    const options = await getDistributionOptions();
    renderSimpleDropdown('distributionDropdownRoot', options, 'Distribution', 'distributionSelect');
}

// ============================================
// THREAT LEVEL DROPDOWN
// ============================================
async function setupThreatLevelDropdown() {
    const options = await getThreatLevelOptions();
    renderSimpleDropdown('threatLevelDropdownRoot', options, 'Threat Level', 'threatLevelSelect');
}

// ============================================
// ANALYSIS DROPDOWN
// ============================================
async function setupAnalysisDropdown() {
    const options = await getAnalysisOptions();
    renderSimpleDropdown('analysisDropdownRoot', options, 'Analysis', 'analysisSelect');
}

// ============================================
// TAGS DROPDOWN
// ============================================
async function setupTagsDropdown() {
    const data = await getTagsCategories();
    renderNestedDropdown('tagsDropdownRoot', data, 'Tags', 'selectedTags');
}

// ============================================
// GALAXIES DROPDOWN
// ============================================
async function setupGalaxiesDropdown() {
    const data = await getGalaxiesCategories();
    renderNestedDropdown('galaxyDropdownRoot', data, 'Galaxies', 'selectedGalaxies');
}