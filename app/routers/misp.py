from fastapi import APIRouter, HTTPException, Header, Depends
from app.models import CreateEventRequest, AddAttributeRequest, EventResponse
from app.services.misp_service import misp_service
from app.config import settings

router = APIRouter(prefix="/api/misp", tags=["MISP"])

# API Key validation
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@router.post("/events", response_model=EventResponse, dependencies=[Depends(verify_api_key)])
async def create_event(request: CreateEventRequest):
    """
    Sukurti naują MISP event su automatiniais tag'ais
    """
    try:
        # 1. Sukurti event
        event = misp_service.create_event(
            title=request.title,
            info=request.title
        )
        
        event_id = event['id']
        
        # 2. Pridėti default tag'us
        default_tags = ["Lithuania", "Higher Education", "tlp:amber"]
        for tag in default_tags:
            try:
                misp_service.add_tag(event_id, tag)
            except Exception as e:
                print(f"Warning: Could not add tag {tag}: {e}")
        
        # 3. Pridėti IP adresus
        for ip in request.ips:
            misp_service.add_attribute(
                event_id=event_id,
                attr_type="ip-dst",
                value=ip,
                comment="Added via API"
            )
        
        return EventResponse(
            event_id=str(event_id),
            info=event['info'],
            status="created",
            message=f"Event created successfully with {len(request.ips)} IPs"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", dependencies=[Depends(verify_api_key)])
async def get_event(event_id: str):
    """
    Gauti MISP event pagal ID
    """
    try:
        event = misp_service.get_event(event_id)
        return event
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Event not found: {e}")