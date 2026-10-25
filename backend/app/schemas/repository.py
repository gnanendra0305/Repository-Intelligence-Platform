from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class RepositoryAnalyzeRequest(BaseModel):
    """Request model for repository analysis/collection."""
    url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g. https://github.com/fastapi/fastapi) or shorthand (owner/repo).",
        examples=["https://github.com/fastapi/fastapi", "pallets/flask"]
    )

class RepositoryInfo(BaseModel):
    """
    Standardized Repository Information schema.
    Directly satisfies Phase 1: GitHub Repository Data Collection requirements.
    """
    # Core Phase 1 Required Fields
    name: str = Field(..., description="Repository name, e.g. 'fastapi'")
    full_name: str = Field(..., description="Full repository name including owner, e.g. 'fastapi/fastapi'")
    description: Optional[str] = Field(None, description="Repository description")
    stars: int = Field(..., description="Count of stargazers (stargazers_count)")
    forks: int = Field(..., description="Count of forks (forks_count)")
    language: Optional[str] = Field(None, description="Primary programming language")
    created_at: str = Field(..., description="Creation timestamp in ISO-8601 format")
    last_updated_at: str = Field(..., description="Last updated timestamp in ISO-8601 format")
    open_issues_count: int = Field(..., description="Count of open issues and pull requests")
    default_branch: str = Field(..., description="Default git branch name (e.g. 'main', 'master')")
    is_archived: bool = Field(..., description="Whether the repository is archived on GitHub")
    
    # Contextual and UI Enrichment Fields
    owner: str = Field(..., description="Repository owner username or organization")
    owner_avatar_url: Optional[str] = Field(None, description="Avatar image URL of repository owner")
    html_url: str = Field(..., description="Web URL to repository on GitHub")
    license_name: Optional[str] = Field(None, description="SPDX ID or name of repository license")
    topics: List[str] = Field(default_factory=list, description="Repository topic tags")
    watchers_count: int = Field(default=0, description="Count of repository watchers/subscribers")
    size_kb: int = Field(default=0, description="Repository size in kilobytes")
    network_count: Optional[int] = Field(None, description="Network count if available")
    subscribers_count: Optional[int] = Field(None, description="Subscriber count if available")
    
    # Metadata
    fetched_at: str = Field(..., description="Timestamp when data was retrieved from GitHub API")

class RepositoryAnalyzeResponse(BaseModel):
    """API Response wrapper model."""
    success: bool = True
    message: str = "Repository data fetched successfully."
    data: RepositoryInfo
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standardized error response model."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[str] = None
