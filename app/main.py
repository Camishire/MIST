from fastapi import FastAPI
from app.config import settings
from app.routers import misp

app = FastAPI(
    title="MISP Enrichment API",
    description="API for simplified MISP event creation and enrichment",
    version="1.0.0"
)

# Include routers
app.include_router(misp.router)

@app.get("/")
async def root():
    return {
        "message": "MISP Enrichment API is running!",
        "status": "ok",
        "config_check": {
            "misp_connected": settings.misp_url is not None,
            "opencti_connected": settings.opencti_url is not None,
            "elastic_connected": settings.elastic_url is not None
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}