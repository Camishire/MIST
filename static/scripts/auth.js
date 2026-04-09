console.log('🔐 Auth checker loaded...');

// Check authentication on page load
async function checkAuth() {
    try {
        const response = await fetch('/auth/status');
        
        if (response.status === 401) {
            // Not authenticated - redirect to OpenCTI
            const data = await response.json();
            console.log('❌ Not authenticated. Redirecting to OpenCTI...');
            
            document.body.innerHTML = `
                <div style="
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                ">
                    <h1 style="font-size: 48px; margin-bottom: 20px;">🔒 Authentication Required</h1>
                    <p style="font-size: 20px; margin-bottom: 30px;">
                        Please login to OpenCTI to access MIST
                    </p>
                    <a href="${data.opencti_url}" style="
                        background: white;
                        color: #667eea;
                        padding: 15px 40px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: bold;
                        font-size: 18px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    ">
                        Login to OpenCTI →
                    </a>
                    <p style="margin-top: 40px; opacity: 0.8; font-size: 14px;">
                        Redirecting in <span id="countdown">3</span> seconds...
                    </p>
                </div>
            `;
            
            // Countdown and redirect
            let count = 3;
            const countdownEl = document.getElementById('countdown');
            const interval = setInterval(() => {
                count--;
                if (countdownEl) countdownEl.textContent = count;
                
                if (count === 0) {
                    clearInterval(interval);
                    window.location.href = data.opencti_url;
                }
            }, 1000);
            
            return false;
        }
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Authenticated as:', data.user.name);
            
            // Store user info globally
            window.MIST_USER = data.user;
            
            const userName = data.user.name || data.user.email;
            console.log(`👋 Welcome, ${userName}!`);
            
            return true;
        }
        
        throw new Error('Unexpected response from auth check');
        
    } catch (error) {
        console.error('❌ Auth check failed:', error);
        
        // Show error page
        document.body.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            ">
                <h1 style="color: #e74c3c; font-size: 48px; margin-bottom: 20px;">⚠️ Connection Error</h1>
                <p style="font-size: 18px; color: #555; margin-bottom: 30px;">
                    Could not connect to authentication service
                </p>
                <pre style="
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: left;
                    font-size: 14px;
                    color: #333;
                    max-width: 600px;
                    overflow-x: auto;
                ">${error.message}</pre>
                <button onclick="location.reload()" style="
                    margin-top: 30px;
                    background: #3498db;
                    color: white;
                    padding: 12px 30px;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    cursor: pointer;
                ">
                    Retry
                </button>
            </div>
        `;
        
        return false;
    }
}

// Run auth check immediately
checkAuth();

console.log('✅ Auth.js loaded!');