from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis_router
from app.core.config import settings

app = FastAPI(
    title="MoneyMule MultiAgent API",
    description="API for analyzing project decks and finding founders",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "MoneyMule MultiAgent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 