from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import (
    ProjectAnalysisRequest, 
    AnalysisResponse, 
    GitRollScanRequest, 
    GitRollScanResponse
)
from app.services.analysis_service import AnalysisService
from app.services.gitroll_service import GitRollService
from typing import Dict, Any
import asyncio

router = APIRouter(prefix="/analysis", tags=["Project Analysis"])

# Initialize services
analysis_service = AnalysisService()
gitroll_service = GitRollService()

@router.post("/project", response_model=AnalysisResponse)
async def analyze_project(request: ProjectAnalysisRequest):
    """
    Analyze a project deck and find founders information
    """
    try:
        # Validate input
        if not request.deck_file:
            raise HTTPException(status_code=400, detail="Deck file is required")
        
        # Perform analysis
        project_summary = await analysis_service.analyze_project(
            deck_file=request.deck_file,
            project_name=request.project_name
        )
        
        return AnalysisResponse(
            success=True,
            message="Project analysis completed successfully",
            data=project_summary
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/gitroll/scan", response_model=GitRollScanResponse)
async def initiate_gitroll_scan(request: GitRollScanRequest):
    """
    Initiate a GitRoll scan for a GitHub user
    """
    try:
        if not request.user:
            raise HTTPException(status_code=400, detail="GitHub username is required")
        
        result = await gitroll_service.initiate_scan(request.user)
        
        return GitRollScanResponse(
            success=result.success,
            scan_id=result.scan_id,
            profile_url=result.profile_url,
            message=result.message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitRoll scan failed: {str(e)}")

@router.get("/gitroll/status/{scan_id}")
async def check_gitroll_status(scan_id: str):
    """
    Check the status of a GitRoll scan
    """
    try:
        status = await gitroll_service.check_scan_status(scan_id)
        
        if status.get("success"):
            return {
                "success": True,
                "scan_id": scan_id,
                "status": status.get("status", "unknown"),
                "score": status.get("score"),
                "og_image_score": status.get("og_image_score"),
                "profile_url": status.get("profile_url")
            }
        else:
            return {
                "success": False,
                "scan_id": scan_id,
                "message": status.get("message", "Unknown error")
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking scan status: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "analysis"}

@router.get("/")
async def root():
    """
    Root endpoint for analysis router
    """
    return {
        "message": "Project Analysis API",
        "endpoints": {
            "analyze_project": "POST /analysis/project",
            "gitroll_scan": "POST /analysis/gitroll/scan",
            "gitroll_status": "GET /analysis/gitroll/status/{scan_id}",
            "health": "GET /analysis/health"
        }
    } 