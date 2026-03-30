from fastapi import FastAPI

app = FastAPI(
    title="MISP Enrichment API",
    description="API for simplified MISP event creation and enrichment",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "MISP Enrichment API is running!",
        "status": "ok"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}