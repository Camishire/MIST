from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.models import CreateEventRequest, CreateEventFullRequest
from app.services.misp import create_misp_event, create_misp_event_simple
from app.constants import (
    get_all_tags, get_all_galaxies, get_all_categories, get_types_for_category,
    DISTRIBUTION_OPTIONS, THREAT_LEVEL_OPTIONS, ANALYSIS_OPTIONS
)
from app.services.misp_parser import parse_bulk_upload

app = FastAPI(title="MIST API")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    return {"message": "Healthy as can be!"}

# ============================================
# METADATA OPTIONS
# ============================================

@app.get("/api/distribution")
def get_distribution():
    """Grąžina distribution options"""
    return {"options": DISTRIBUTION_OPTIONS}

@app.get("/api/threat-level")
def get_threat_level():
    """Grąžina threat level options"""
    return {"options": THREAT_LEVEL_OPTIONS}

@app.get("/api/analysis")
def get_analysis():
    """Grąžina analysis options"""
    return {"options": ANALYSIS_OPTIONS}

# ============================================
# TAGS & GALAXIES
# ============================================

@app.get("/api/tags/categories")
def list_tags():
    """Grąžina tags pagal kategorijas"""
    return get_all_tags()

@app.get("/api/galaxies/categories")
def list_galaxies():
    """Grąžina galaxies pagal kategorijas"""
    return get_all_galaxies()

# ============================================
# CATEGORIES & TYPES
# ============================================

@app.get("/api/categories")
def get_categories():
    """Gauti visas attribute kategorijas"""
    return {"categories": get_all_categories()}

@app.get("/api/categories/{category}/types")
def get_category_types(category: str):
    """Gauti types konkrečiai kategorijai"""
    types = get_types_for_category(category)
    return {"category": category, "types": types}

# ============================================
# BULK UPLOAD
# ============================================

class BulkUploadRequest(BaseModel):
    ips: list[str]

@app.post("/api/bulk-upload")
def bulk_upload(request: BulkUploadRequest):
    """Priima bulk duomenis ir grąžina parsed attributes"""
    if not request.ips:
        raise HTTPException(status_code=400, detail="No data provided")
    
    result = parse_bulk_upload(request.ips)
    return result

# ============================================
# EVENT CREATION
# ============================================

@app.post("/events")
def create_event(request: CreateEventRequest):
    """Simple event creation (backwards compatibility)"""
    result = create_misp_event_simple(
        title=request.title,
        ips=request.ips,
        distribution=request.distribution,
        threat_level_id=request.threat_level_id,
        analysis=request.analysis
    )
    return {
        "message": "Event created!",
        "event_id": result['Event']['id'],
        "url": f"https://ziurke.vilniustech.lt/events/view/{result['Event']['id']}"
    }

@app.post("/events/create")
def create_event_full(request: CreateEventFullRequest):
    """Create MISP event with tags, galaxies, and attributes"""
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