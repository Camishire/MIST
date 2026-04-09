from typing import List
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.models import CreateEventRequest, CreateEventFullRequest
from app.services.abuseipdb import check_ip_abuse, check_ip_abuse_bulk
from app.services.misp import create_misp_event, create_misp_event_simple
from app.services.opencti import check_ip_in_opencti, format_opencti_result_for_comment
from app.constants import (
    get_all_tags, get_all_galaxies, get_all_categories, get_creator_options, get_types_for_category,
    DISTRIBUTION_OPTIONS, THREAT_LEVEL_OPTIONS, ANALYSIS_OPTIONS
)
from app.services.misp_parser import parse_bulk_upload
from app.config import settings
import logging
import os

# Toggle between real and mock auth
if os.getenv("MIST_ENV") == "production":
    from app.opencti_auth import require_opencti_auth, OpenCTIAuth
    print("🔒 Using REAL OpenCTI authentication")
else:
    from app.opencti_auth_local import require_opencti_auth, OpenCTIAuth
    print("🧪 Using MOCK authentication (local testing)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name=settings.api_key_name, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key_value:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API Key. Please provide a valid X-API-Key header."
        )
    return api_key


# FASTAPI APP
app = FastAPI(
    title="MIST API",
    description="MISP Intelligence Submission Tool - Create MISP events with ease",
    version="2.0"
)

@app.middleware("http")
async def disable_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")


# OPENCTI AUTH ENDPOINTS
@app.get("/auth/status")
async def auth_status(user = Depends(require_opencti_auth)):
    """Check if user has valid OpenCTI session"""
    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user.get("user_email")
        }
    }

@app.get("/auth/login")
async def login_redirect():
    """Redirect to OpenCTI login"""
    return OpenCTIAuth.get_login_redirect()


# MAIN PAGE (PROTECTED WITH OPENCTI AUTH)
@app.get("/")
def root(user = Depends(require_opencti_auth)):
    """Serve the main HTML interface - requires OpenCTI login"""
    logger.info(f"User accessed MIST: {user['name']} (ID: {user['id']})")
    return FileResponse("static/index.html")


# PUBLIC ENDPOINTS
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MIST API", "version": "2.0", "auth": "OpenCTI"}


# METADATA OPTIONS (Protected with OpenCTI auth)
@app.get("/api/distribution")
def get_distribution(user = Depends(require_opencti_auth)):
    """Get distribution level options"""
    return {"options": DISTRIBUTION_OPTIONS}

@app.get("/api/creators")
def get_creators(user = Depends(require_opencti_auth)):
    """Get available creators"""
    return {"options": get_creator_options()}

@app.get("/api/threat-level")
def get_threat_level(user = Depends(require_opencti_auth)):
    """Get threat level options"""
    return {"options": THREAT_LEVEL_OPTIONS}

@app.get("/api/analysis")
def get_analysis(user = Depends(require_opencti_auth)):
    """Get analysis status options"""
    return {"options": ANALYSIS_OPTIONS}

@app.get("/api/tags/categories")
def list_tags(user = Depends(require_opencti_auth)):
    """Get all available tags by category"""
    return get_all_tags()

@app.get("/api/galaxies/categories")
def list_galaxies(user = Depends(require_opencti_auth)):
    """Get all available galaxies by category"""
    return get_all_galaxies()

@app.get("/api/categories")
def get_categories(user = Depends(require_opencti_auth)):
    """Get all attribute categories"""
    return {"categories": get_all_categories()}

@app.get("/api/categories/{category}/types")
def get_category_types(category: str, user = Depends(require_opencti_auth)):
    """Get valid types for a specific category"""
    types = get_types_for_category(category)
    return {"category": category, "types": types}


# PROTECTED ENDPOINTS (OpenCTI Auth)
class BulkUploadRequest(BaseModel):
    ips: list[str]

@app.post("/api/bulk-upload")
def bulk_upload(
    request: BulkUploadRequest,
    user = Depends(require_opencti_auth)
):
    if not request.ips:
        raise HTTPException(status_code=400, detail="No data provided")
    
    result = parse_bulk_upload(request.ips)
    logger.info(f"Bulk upload by {user['name']}: {len(request.ips)} items")
    return result

@app.post("/events")
def create_event(
    request: CreateEventRequest,
    user = Depends(require_opencti_auth)
):
    result = create_misp_event_simple(
        creator_key=request.creator_key,
        title=request.title,
        ips=request.ips,
        distribution=request.distribution,
        threat_level_id=request.threat_level_id,
        analysis=request.analysis
    )
    
    logger.info(f"Simple event created by {user['name']}: Event ID {result['Event']['id']}")
    
    return {
        "success": True,
        "message": "Event created!",
        "event_id": result['Event']['id'],
        "url": f"{settings.misp_url}/events/view/{result['Event']['id']}"
    }

@app.post("/events/create")
def create_event_full(
    request: CreateEventFullRequest,
    user = Depends(require_opencti_auth)
):
    attributes = [attr.dict() for attr in request.attributes]
    
    try:
        result = create_misp_event(
            creator_key=request.creator_key,
            date=request.date,
            distribution=request.distribution,
            threat_level_id=request.threat_level_id,
            analysis=request.analysis,
            info=request.info,
            tags=request.tags,
            galaxies=request.galaxies,
            attributes=attributes
        )
        
        logger.info(f"Full event created by {user['name']} ({user['user_email']}): Event ID {result['Event']['id']}")
        
        return {
            "success": True,
            "message": "Event created successfully!",
            "event_id": result['Event']['id'],
            "url": f"{settings.misp_url}/events/view/{result['Event']['id']}",
            "created_by": user['name']
        }
        
    except Exception as e:
        logger.error(f"Event creation failed for {user['name']}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ENRICHMENT ENDPOINTS (Protected with OpenCTI auth) 
@app.get("/api/check-abuseipdb/bulk")
def check_abuseipdb_bulk(ips: str, user = Depends(require_opencti_auth)):
    ip_list = ips.split(",")
    logger.info(f"AbuseIPDB bulk check by {user['name']}: {len(ip_list)} IPs")
    return check_ip_abuse_bulk(ip_list)
    
@app.get("/api/check-abuseipdb/{ip_address}")
def check_abuseipdb(ip_address: str, user = Depends(require_opencti_auth)):
    return check_ip_abuse(ip_address)

@app.get("/api/check-opencti/{ip_address}")
def check_opencti(ip_address: str, user = Depends(require_opencti_auth)):
    result = check_ip_in_opencti(ip_address)
    
    result["formatted_comment"] = format_opencti_result_for_comment(result)
    
    return result
 
@app.get("/api/check-opencti/bulk")
def check_opencti_bulk(ips: str, user = Depends(require_opencti_auth)):
    ip_list = ips.split(",")
    results = []
    
    for ip in ip_list:
        result = check_ip_in_opencti(ip.strip())
        result["formatted_comment"] = format_opencti_result_for_comment(result)
        results.append(result)
    
    logger.info(f"OpenCTI bulk check by {user['name']}: {len(ip_list)} IPs")
    return results
 
@app.get("/api/enrich/bulk")
def enrich_ips_bulk(ips: str, user = Depends(require_opencti_auth)) -> List[dict]:
    ip_list = [ip.strip() for ip in ips.split(",") if ip.strip()]
    results = []
    
    for ip in ip_list:
        result = enrich_ip_all_sources(ip, user)
        results.append(result)
    
    return results

@app.get("/api/enrich/{ip_address}")
def enrich_ip_all_sources(ip_address: str, user = Depends(require_opencti_auth)):
    abuse_data = check_ip_abuse(ip_address)
    opencti_data = check_ip_in_opencti(ip_address)
    
    # Build formatted comment with sections
    sections = []
    
    # AbuseIPDB section
    if not abuse_data.get("error"):
        abuse_score = abuse_data.get("abuseConfidenceScore", 0)
        abuse_reports = abuse_data.get("totalReports", 0)
        country = abuse_data.get("countryCode", 'N/A')
        
        if abuse_score > 0 or abuse_reports > 0:
            abuse_lines = [
                "AbuseIPDB:",
                f"  • Confidence: {abuse_score}%",
                f"  • Reports: {abuse_reports}",
                f"  • Country: {country}"
            ]
            sections.append("\n".join(abuse_lines))
    
    # OpenCTI section
    if opencti_data.get("found"):
        opencti_comment = format_opencti_result_for_comment(opencti_data)
        sections.append(opencti_comment)
    
    formatted_comment = "\n\n".join(sections) if sections else "No threat intel found"
    
    logger.info(f"IP enrichment by {user['name']}: {ip_address}")
    
    # Return structure matching what frontend expects
    return {
        "ipAddress": ip_address,
        "abuseipdb": abuse_data,
        "opencti": opencti_data,
        "formatted_comment": formatted_comment
    }