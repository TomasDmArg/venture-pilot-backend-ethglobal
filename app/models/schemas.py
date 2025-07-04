from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectAnalysisRequest(BaseModel):
    deck_file: str = Field(..., description="Base64 encoded deck file")
    project_name: Optional[str] = Field(None, description="Name of the project")
    
class FounderInfo(BaseModel):
    name: str
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    github_username: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

class GitRollScan(BaseModel):
    username: str
    scan_id: Optional[str] = None
    profile_url: Optional[str] = None
    score: Optional[float] = None
    og_image_score: Optional[float] = None
    status: str = "pending"

class ProjectSummary(BaseModel):
    project_name: str
    description: str
    problem_statement: str
    solution: str
    target_market: str
    business_model: str
    team_info: List[FounderInfo]
    github_repos: List[str]
    gitroll_scans: List[GitRollScan]
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ProjectSummary] = None
    error: Optional[str] = None

class GitRollScanRequest(BaseModel):
    user: str = Field(..., description="GitHub username (case sensitive)")

class GitRollScanResponse(BaseModel):
    success: bool
    scan_id: Optional[str] = None
    profile_url: Optional[str] = None
    user_id: Optional[str] = None
    message: str 