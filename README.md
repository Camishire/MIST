# 🔍 MIST - MISP Intelligence Submission Tool

A web-based tool for quickly creating and submitting threat intelligence events to MISP (Malware Information Sharing Platform). Built for SOC analysts who need to bulk-submit IOCs without clicking through MISP's UI a hundred times.

## ✨ What does it do?

MIST lets you:
- **Bulk upload** attributes from paste/CSV and edit them in a nice table
- **Enrich IOCs** automatically with OpenCTI and AbuseIPDB data
- **Tag & categorize** events with galaxies and MISP taxonomies
- **Multi-user support** - each analyst can use their own MISP API key
- **Submit to MISP** with one click and jump straight to the created event

Perfect for those times when you have 50 IPs from a security alert and don't want to manually create 50 MISP attributes.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MISP instance with API access
- (Optional) OpenCTI instance for session-based authentication
- (Optional) AbuseIPDB API key for IP enrichment

### Installation

```bash
# Clone the repo
git clone https://github.com/Camishire/MIST.git
cd MIST

# Install dependencies
pip install -r requirements.txt

# Set up your .env file
cp .env.example .env
# Edit .env with your actual API keys
```

### Configuration

Edit `.env` with your credentials:

```env
# MISP Configuration
MISP_URL=https://your-misp-instance.com

# MISP API Keys (one per analyst/user)
MISP_WORKER1_API_KEY=your_worker1_key_here
MISP_WORKER2_API_KEY=your_worker2_key_here
MISP_WORKER3_API_KEY=your_worker3_key_here

# AbuseIPDB (optional - for IP enrichment)
ABUSEIPDB_API_KEY=your_abuseipdb_key

# OpenCTI (optional - for threat intel enrichment)
OPENCTI_URL=https://your-opencti-instance.com
OPENCTI_API_KEY=your_opencti_key

# MIST API Key (for securing the web interface)
API_KEY=your_random_secure_key_here
```

### Running

#### Local Development
```bash
# Set environment to local (uses mock authentication)
export MIST_ENV=local
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Then visit `http://localhost:8001` in your browser.

#### Production Deployment

**Option 1: Standalone (direct access)**
```bash
# Set environment to production (uses OpenCTI authentication)
export MIST_ENV=production
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Option 2: Behind Apache Reverse Proxy (recommended)**

MIST works best when deployed alongside OpenCTI using Apache as a reverse proxy. This allows session-based authentication and SSL termination.

1. **Update Apache VirtualHost** (e.g., `/etc/apache2/sites-available/your-domain.conf`):

```apache
<VirtualHost *:443>
    ServerName your-domain.com
    
    # SSL configuration (use your existing certs)
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # MIST proxy configuration (order matters!)
    ProxyPass /auth http://127.0.0.1:8001/auth
    ProxyPassReverse /auth http://127.0.0.1:8001/auth
    
    ProxyPass /api http://127.0.0.1:8001/api
    ProxyPassReverse /api http://127.0.0.1:8001/api
    
    ProxyPass /events http://127.0.0.1:8001/events
    ProxyPassReverse /events http://127.0.0.1:8001/events
    
    ProxyPass /mist/static http://127.0.0.1:8001/static
    ProxyPassReverse /mist/static http://127.0.0.1:8001/static
    
    <Location /mist>
        ProxyPass http://127.0.0.1:8001
        ProxyPassReverse http://127.0.0.1:8001
        ProxyPreserveHost On
        ProxyPassReverseCookiePath / /mist
    </Location>
    
    # Your existing OpenCTI proxy (keep last!)
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
```

2. **Create systemd service** (`/etc/systemd/system/mist.service`):

```ini
[Unit]
Description=MIST FastAPI App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/MIST
Environment="MIST_ENV=production"
ExecStart=/opt/MIST/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. **Enable and start**:

```bash
systemctl daemon-reload
systemctl enable mist.service
systemctl start mist.service
systemctl reload apache2
```

4. **Access**: `https://your-domain.com/mist/`

**Authentication:**
- Production mode requires valid OpenCTI session (`opencti_session` cookie)
- Users must login to OpenCTI first, then navigate to `/mist`
- Local mode uses mock authentication for development

## 🔐 Authentication Modes

MIST supports two authentication modes via the `MIST_ENV` environment variable:

- **`MIST_ENV=production`**: Real OpenCTI session-based auth (production deployments)
- **`MIST_ENV=local`** (or unset): Mock authentication for local testing

Set this in your systemd service, `.env` file, or export before running uvicorn.

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /events/create` - Create full MISP event with attributes, tags, galaxies
- `POST /events` - Simple event creation (backwards compatibility)
- `GET /api/creators` - Get available MISP API key options

### Enrichment Services
- `GET /api/enrich/{ip}` - Enrich IP with both OpenCTI and AbuseIPDB data
- `GET /api/check-opencti/{ip}` - Get OpenCTI threat intelligence for IP
- `GET /api/check-abuseipdb/{ip}` - Get AbuseIPDB reputation data for IP

### Metadata
- `GET /api/categories` - Get available MISP attribute categories
- `GET /api/categories/{category}/types` - Get valid types for a category
- `GET /api/tags/categories` - Get all MISP tags grouped by category
- `GET /api/galaxies/categories` - Get all MISP galaxy clusters by category

### Authentication
- `GET /auth/status` - Check authentication status
- `GET /auth/login` - Redirect to OpenCTI login (production mode)

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- PyMISP (MISP API client)
- Pydantic (data validation)

**Frontend:**
- Vanilla JavaScript (no framework bloat)
- Custom CSS (pink Y2K Monster High aesthetic)
- Custom table editor for bulk attribute management

**Integrations:**
- MISP (threat intelligence platform)
- OpenCTI (session auth + threat intel enrichment)
- AbuseIPDB (IP reputation)

## 🎯 Features in Detail

### Bulk Attribute Upload
Paste IOCs from anywhere (CSV, text, Excel) and MIST will parse them into an editable table. Change categories, types, add comments - all before submitting.

### Smart Dropdowns
Category and type dropdowns are dynamically populated from your MISP instance. Select a category and the type dropdown automatically filters to show only valid options.

### Creator Selection
Multiple analysts can use the same MIST instance. Each person selects their identity (Worker 1/2/3) and events are created under their MISP API key.

### Tag & Galaxy Search
Search through thousands of MISP tags and galaxy clusters with autocomplete. Add attribution, threat actors, TTPs - whatever fits your event.

### Enrichment Integration
Click to enrich IPs with:
- **OpenCTI**: Get related threat intel, indicators, observables
- **AbuseIPDB**: Check IP reputation and abuse reports

Results are automatically formatted into the comment field for easy submission.

## 📝 Development Notes

### Project Structure
```python
MIST/
├── app/
│   ├── services/          # Business logic (MISP, OpenCTI, AbuseIPDB)
│   ├── config.py          # Settings & environment variables
│   ├── constants.py       # MISP constants (distributions, threat levels)
│   ├── models.py          # Pydantic models
│   ├── opencti_auth.py    # Production OpenCTI authentication
│   └── opencti_auth_local.py  # Mock authentication for local dev
├── static/
│   ├── scripts/           # Frontend JavaScript modules
│   ├── style.css          # Pink Y2K aesthetic
│   └── index.html         # Main interface
├── main.py                # FastAPI app entry point (deprecated, use app/main.py)
└── requirements.txt       # Python dependencies
```

### Adding New MISP Workers
Edit `.env` and add more keys:
```env
MISP_WORKER4_API_KEY=another_key_here
```

Then update `app/constants.py`:
```python
def get_creator_options():
    return {
        "worker1": settings.misp_worker1_api_key,
        "worker2": settings.misp_worker2_api_key,
        "worker3": settings.misp_worker3_api_key,
        "worker4": settings.misp_worker4_api_key,  # Add this
    }
```

## 🔒 Security Notes

- **Never commit `.env`** - it contains sensitive API keys
- Use the included `.env.example` as a template
- Set a strong `API_KEY` to protect the web interface
- Production mode requires OpenCTI authentication
- Run behind HTTPS in production (Apache reverse proxy recommended)

## 🤝 Contributing

This is a personal SOC tool, but PRs are welcome! If you find bugs or have ideas:
1. Open an issue
2. Fork the repo
3. Make your changes
4. Submit a PR

## 📄 License

MIT License - do whatever you want with it.

## 🙏 Acknowledgments

Built out of frustration with MISP's bulk import workflows. Special thanks to PyMISP maintainers for making the API actually usable

---

**Questions?** Open an issue or check the code - it's pretty straightforward.
