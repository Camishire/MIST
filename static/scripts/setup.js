document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing MIST Creator...');
    
    await setupDistributionDropdown();
    await setupCreatorDropdown();
    await setupThreatLevelDropdown();
    await setupAnalysisDropdown();
    await setupTagsDropdown();
    await setupGalaxiesDropdown();
    
    console.log('All dropdowns loaded!');
});

async function setupDistributionDropdown() {
    const options = await getDistributionOptions();
    renderSimpleDropdown('distributionDropdownRoot', options, 'Distribution', 'distributionSelect');
}

async function setupCreatorDropdown() {
    const options = await getCreatorOptions();
    renderSimpleDropdown('creatorDropdownRoot', options, 'Creator', 'creatorSelect');
}

async function setupThreatLevelDropdown() {
    const options = await getThreatLevelOptions();
    renderSimpleDropdown('threatLevelDropdownRoot', options, 'Threat Level', 'threatLevelSelect');
}

async function setupAnalysisDropdown() {
    const options = await getAnalysisOptions();
    renderSimpleDropdown('analysisDropdownRoot', options, 'Analysis', 'analysisSelect');
}

async function setupTagsDropdown() {
    const data = await getTagsCategories();
    renderNestedDropdown('tagsDropdownRoot', data, 'Tags', 'selectedTags');
}

async function setupGalaxiesDropdown() {
    const data = await getGalaxiesCategories();
    renderNestedDropdown('galaxyDropdownRoot', data, 'Galaxies', 'selectedGalaxies');
}