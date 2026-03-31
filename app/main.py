from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.models import CreateEventRequest
from app.services.misp import create_misp_event

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