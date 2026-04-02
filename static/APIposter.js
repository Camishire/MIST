

async function postBulkUpload(data) {
    try {
        const response = await fetch('/api/bulk-upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    } catch (error) {
        console.error('Error posting bulk upload:', error);
        throw error;
    }
}