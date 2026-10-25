import logging
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .schemas.repository import (
    RepositoryAnalyzeRequest,
    RepositoryAnalyzeResponse,
    ErrorResponse,
)
from .services.github_service import github_service, GitHubAPIException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("rip-backend")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        "Backend API for AI-Assisted Developer Decision Support and Repository Intelligence Platform. "
        "Phase 1: GitHub Repository Data Collection."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS so the React frontend can seamlessly connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev frontends (Vite on 5173, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint to verify backend service status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "phase": "Phase 1: GitHub Repository Data Collection"
    }


@app.post(
    f"{settings.API_V1_PREFIX}/repository/analyze",
    response_model=RepositoryAnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository URL or identifier"},
        404: {"model": ErrorResponse, "description": "Repository not found on GitHub"},
        429: {"model": ErrorResponse, "description": "GitHub API rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server or API error"},
    },
    tags=["Repository Data Collection"]
)
async def analyze_repository_post(payload: RepositoryAnalyzeRequest):
    """
    Step 1 & Step 2: Accept a repository URL, validate it, and fetch metadata via GitHub REST API.
    """
    logger.info("Received analyze request for URL: %s", payload.url)
    try:
        repo_info, meta = await github_service.fetch_repository(payload.url)
        return RepositoryAnalyzeResponse(
            success=True,
            message="Repository information collected successfully.",
            data=repo_info,
            rate_limit_remaining=meta.get("remaining"),
            rate_limit_reset=meta.get("reset")
        )
    except ValueError as ve:
        logger.warning("Validation error for '%s': %s", payload.url, str(ve))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_REPOSITORY_URL",
                message=str(ve),
                details="Please provide a valid GitHub repository URL (e.g., https://github.com/fastapi/fastapi) or shorthand (owner/repo)."
            ).model_dump()
        )
    except GitHubAPIException as ge:
        logger.error("GitHub API error: %s (status %d)", ge.message, ge.status_code)
        return JSONResponse(
            status_code=ge.status_code,
            content=ErrorResponse(
                success=False,
                error_code=f"GITHUB_API_ERROR_{ge.status_code}",
                message=ge.message,
                details=ge.details
            ).model_dump()
        )
    except Exception as e:
        logger.exception("Unexpected server error processing '%s': %s", payload.url, str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred while retrieving repository information.",
                details=str(e)
            ).model_dump()
        )


@app.get(
    f"{settings.API_V1_PREFIX}/repository",
    response_model=RepositoryAnalyzeResponse,
    tags=["Repository Data Collection"]
)
async def analyze_repository_get(url: str = Query(..., description="GitHub repository URL or owner/repo")):
    """
    GET endpoint for repository analysis to allow easy browser or cURL testing.
    """
    req = RepositoryAnalyzeRequest(url=url)
    return await analyze_repository_post(req)
