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
- (Optional) OpenCTI and AbuseIPDB API keys for enrichment

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

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (systemd service recommended)
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then visit `http://localhost:8000` in your browser.

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Main web interface
- `POST /events/create` - Create full MISP event with attributes, tags, galaxies
- `POST /events` - Simple event creation (backwards compatibility)
- `GET /api/creators` - Get available MISP API key options

### Enrichment Services
- `POST /enrich/opencti` - Enrich IP with OpenCTI threat intelligence
- `POST /enrich/abuseipdb` - Get AbuseIPDB reputation data for IPs

### Metadata
- `GET /api/categories` - Get available MISP attribute categories
- `GET /api/types` - Get available MISP attribute types (optionally filtered by category)
- `GET /api/tags` - Search MISP tags
- `GET /api/galaxies` - Search MISP galaxy clusters

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- PyMISP (MISP API client)
- Pydantic (data validation)

**Frontend:**
- Vanilla JavaScript (no framework bloat)
- Bootstrap 5 (UI components)
- Custom table editor for bulk attribute management

**Integrations:**
- MISP (threat intelligence platform)
- OpenCTI (threat intel enrichment)
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

## 📝 Development Notes

### Project Structure
```
MIST/
├── app/
│   ├── services/          # Business logic (MISP, OpenCTI, AbuseIPDB)
│   ├── config.py          # Settings & environment variables
│   ├── constants.py       # MISP constants (distributions, threat levels)
│   └── models.py          # Pydantic models
├── static/
│   ├── js/                # Frontend JavaScript modules
│   └── css/               # Styles
├── main.py                # FastAPI app entry point
└── requirements.txt       # Python dependencies
```

### Adding New MISP Workers
Edit `.env` and add more keys:
```env
MISP_WORKER4_API_KEY=another_key_here
```

Then update `config.py`:
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
- Consider running behind a reverse proxy (nginx) with HTTPS

## 🤝 Contributing

This is a personal SOC tool, but PRs are welcome! If you find bugs or have ideas:
1. Open an issue
2. Fork the repo
3. Make your changes
4. Submit a PR

## 📄 License

MIT License - do whatever you want with it.

## 🙏 Acknowledgments

Built out of frustration with MISP's bulk import workflows. Special thanks to the PyMISP maintainers for making the API actually usable.

---

**Questions?** Open an issue or check the code - it's pretty straightforward.
