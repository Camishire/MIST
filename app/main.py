from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.models import CreateEventRequest, CreateEventFullRequest
from app.services.misp import create_misp_event, create_misp_event_simple
from app.constants import (
    get_all_tags, get_all_galaxies, get_all_categories, get_types_for_category,
    DISTRIBUTION_OPTIONS, THREAT_LEVEL_OPTIONS, ANALYSIS_OPTIONS
)
from app.services.misp_parser import parse_bulk_upload
from app.config import settings

# ============================================
# API KEY AUTHENTICATION
# ============================================

api_key_header = APIKeyHeader(name=settings.api_key_name, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for protected endpoints"""
    if api_key != settings.api_key_value:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API Key. Please provide a valid X-API-Key header."
        )
    return api_key

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="MIST API",
    description="MISP Intelligence Submission Tool - Create MISP events with ease",
    version="2.0"
)

@app.middleware("http")
async def disable_cache(request, call_next):
    """Disable caching for static files during development"""
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================
# PUBLIC ENDPOINTS
# ============================================

@app.get("/")
def root():
    """Serve the main HTML interface"""
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MIST API", "version": "2.0"}

# ============================================
# METADATA OPTIONS (Public - for UI rendering)
# ============================================

@app.get("/api/distribution")
def get_distribution():
    """Get distribution level options"""
    return {"options": DISTRIBUTION_OPTIONS}

@app.get("/api/threat-level")
def get_threat_level():
    """Get threat level options"""
    return {"options": THREAT_LEVEL_OPTIONS}

@app.get("/api/analysis")
def get_analysis():
    """Get analysis status options"""
    return {"options": ANALYSIS_OPTIONS}

@app.get("/api/tags/categories")
def list_tags():
    """Get all available tags by category"""
    return get_all_tags()

@app.get("/api/galaxies/categories")
def list_galaxies():
    """Get all available galaxies by category"""
    return get_all_galaxies()

@app.get("/api/categories")
def get_categories():
    """Get all attribute categories"""
    return {"categories": get_all_categories()}

@app.get("/api/categories/{category}/types")
def get_category_types(category: str):
    """Get valid types for a specific category"""
    types = get_types_for_category(category)
    return {"category": category, "types": types}

# ============================================
# PROTECTED ENDPOINTS (Require API Key)
# ============================================

class BulkUploadRequest(BaseModel):
    ips: list[str]

@app.post("/api/bulk-upload")
def bulk_upload(
    request: BulkUploadRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Parse bulk input data and auto-detect attribute types
    
    Requires: X-API-Key header
    """
    if not request.ips:
        raise HTTPException(status_code=400, detail="No data provided")
    
    result = parse_bulk_upload(request.ips)
    return result

@app.post("/events")
def create_event(
    request: CreateEventRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Simple event creation (backwards compatibility)
    
    Requires: X-API-Key header
    """
    result = create_misp_event_simple(
        title=request.title,
        ips=request.ips,
        distribution=request.distribution,
        threat_level_id=request.threat_level_id,
        analysis=request.analysis
    )
    return {
        "success": True,
        "message": "Event created!",
        "event_id": result['Event']['id'],
        "url": f"https://ziurke.vilniustech.lt/events/view/{result['Event']['id']}"
    }

@app.post("/events/create")
def create_event_full(
    request: CreateEventFullRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Create MISP event with full metadata (tags, galaxies, attributes)
    
    Requires: X-API-Key header
    """
    attributes = [attr.dict() for attr in request.attributes]
    
    try:
        result = create_misp_event(
            date=request.date,
            distribution=request.distribution,
            threat_level_id=request.threat_level_id,
            analysis=request.analysis,
            info=request.info,
            tags=request.tags,
            galaxies=request.galaxies,
            attributes=attributes
        )
        
        return {
            "success": True,
            "message": "Event created successfully!",
            "event_id": result['Event']['id'],
            "url": f"https://ziurke.vilniustech.lt/events/view/{result['Event']['id']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))