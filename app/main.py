from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic.v1 import BaseModel
from app.models import CreateEventRequest
from app.services.misp import create_misp_event
from app.constants import get_all_tags, get_all_galaxies
from app.constants import get_all_categories, get_types_for_category
from app.services.misp_parser import parse_bulk_upload

app = FastAPI(title="MIST API")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    return {"message": "Healthy as can be!"}

@app.get("/events={event_id}")
def get_event(event_id: int):
    return {"message": f"Event {event_id} details would be here."}

@app.post("/events")
def create_event(request: CreateEventRequest):
    result = create_misp_event(
        title=request.title,
        ips=request.ips,
        distribution=request.distribution,
        threat_level_id=request.threat_level_id,
        analysis=request.analysis
    )
    return {
        "message": f"Event created!. <a href='https://ziurke.vilniustech.lt/events/view/{result['Event']['id']}' target='_blank'>View Event</a>",
        "event_id": result['Event']['id'],
        "title": request.title
    }

@app.get("/api/tags/categories")  # ← Pakeistas URL
def list_tags():  # ← SKIRTINGAS vardas!
    return get_all_tags()  # ← Kviečia iš constants

@app.get("/api/galaxies/categories")  # ← Pakeistas URL
def list_galaxies():  # ← SKIRTINGAS vardas!
    return get_all_galaxies()  # ← Kviečia iš constants

@app.get("/api/categories")
def get_categories():
    """Gauti visas attribute kategorijas"""
    return {"categories": get_all_categories()}

@app.get("/api/categories/{category}/types")
def get_category_types(category: str):
    """Gauti types konkrečiai kategorijai"""
    types = get_types_for_category(category)
    return {"category": category, "types": types}

class BulkUploadRequest(BaseModel):
    ips: list[str]

@app.post("/api/bulk-upload")
def bulk_upload(request: BulkUploadRequest):
    print(f"Received bulk upload: {request.ips}")  # Debug print
    """Priima bulk duomenis ir grąžina parsed attributes"""
    if not request.ips:
        raise HTTPException(status_code=400, detail="No data provided")
    
    result = parse_bulk_upload(request.ips)
    print(f"Parsed attributes: {result}")  # Debug print
    return result