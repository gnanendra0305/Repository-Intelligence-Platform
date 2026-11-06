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
from .schemas.metric import (
    MetricDefinition,
    MetricListResponse,
    MetricDetailResponse,
    CHAOSSFamily,
    LinakerArea,
    MetricType,
)
from .schemas.mining import (
    RepositoryMiningRequest,
    RepositoryMiningResponse,
)
from .schemas.graphql_mining import (
    GraphQLMiningRequest,
    GraphQLMiningResponse,
)
from .schemas.archive import (
    GHArchiveIngestionRequest,
    GHArchiveIngestionResponse,
)
from .schemas.indicators import (
    CalculateIndicatorsRequest,
    CalculateIndicatorsResponse,
    HealthIndexResult,
)
from .schemas.survival import (
    SurvivalObservation,
    SurvivalEstimateRequest,
    SurvivalAnalysisReport,
    SingleRepoSurvivalAssessment,
)
from .schemas.report import (
    GenerateReportRequest,
    GenerateReportResponse,
    RepositoryHealthReport,
)
from .services.github_service import (
    github_service,
    GitHubAPIException,
    RepositoryNotFoundError,
    RateLimitExceededError,
)
from .services.metric_registry import metric_registry_service
from .services.mining_service import mining_service
from .services.indicator_service import indicator_service
from .services.survival_service import survival_service
from .services.report_service import report_service
from .services.graphql_service import graphql_service
from .services.archive_service import archive_service

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


@app.get(
    f"{settings.API_V1_PREFIX}/metrics",
    response_model=MetricListResponse,
    tags=["Metric Registry (M0.1)"]
)
async def get_metrics(
    chaoss_family: Optional[str] = Query(None, description="Filter by CHAOSS Metric Family (e.g. 'Evolution', 'Risk', 'Value', 'Common Metrics')"),
    linaker_area: Optional[str] = Query(None, description="Filter by Linåker et al. (2026) Health Area (e.g. 'Community Productivity', 'Production Process')"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type ('health', 'context', 'data_quality', 'derived')")
):
    """
    M0.1: Retrieve repository health and sustainability metrics from the canonical Metric Registry.
    Supports primary filtering by CHAOSS Working Group Family and secondary filtering by Linåker Health Area.
    """
    metrics = metric_registry_service.get_all_metrics()
    total = len(metrics)

    if chaoss_family:
        metrics = [m for m in metrics if m.chaoss_family.lower() == chaoss_family.strip().lower()]
    if linaker_area:
        metrics = [m for m in metrics if m.linaker_area.lower() == linaker_area.strip().lower()]
    if metric_type:
        metrics = [m for m in metrics if m.metric_type.lower() == metric_type.strip().lower()]

    return MetricListResponse(
        success=True,
        count=len(metrics),
        total_registered=total,
        chaoss_family_filter=chaoss_family,
        linaker_area_filter=linaker_area,
        metric_type_filter=metric_type,
        data=metrics
    )


@app.get(
    f"{settings.API_V1_PREFIX}/metrics/{{metric_id}}",
    response_model=MetricDetailResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Metric not found in registry"}
    },
    tags=["Metric Registry (M0.1)"]
)
async def get_metric_by_id(metric_id: str):
    """
    M0.1: Retrieve detailed metadata, formula, payload dependencies, and research provenance for a single metric.
    """
    metric = metric_registry_service.get_metric_by_id(metric_id)
    if not metric:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                success=False,
                error_code="METRIC_NOT_FOUND",
                message=f"Metric '{metric_id}' was not found in the Metric Registry.",
                details="Use GET /api/metrics to view all registered canonical metric IDs."
            ).model_dump()
        )
    return MetricDetailResponse(success=True, data=metric)


@app.post(
    f"{settings.API_V1_PREFIX}/repository/mine",
    response_model=RepositoryMiningResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository URL or identifier"},
        404: {"model": ErrorResponse, "description": "Repository not found on GitHub"},
        429: {"model": ErrorResponse, "description": "GitHub API rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server or API error"},
    },
    tags=["Repository Mining (M0.2)"]
)
async def mine_repository_post(payload: RepositoryMiningRequest):
    """
    M0.2: Structured repository data collection pipeline.
    Collects repository metadata, pull requests, issues (excluding PRs),
    commits, and contributors with multi-page pagination and rate-limit tracking.
    """
    logger.info("Received mining request for URL: %s", payload.url)
    try:
        result = await mining_service.mine_repository(payload)
        return result
    except ValueError as ve:
        logger.warning("Validation error for mining '%s': %s", payload.url, str(ve))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_REPOSITORY_URL",
                message=str(ve),
                details="Please provide a valid GitHub repository URL (e.g. https://github.com/fastapi/fastapi) or owner/repo."
            ).model_dump()
        )
    except RepositoryNotFoundError as rnfe:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                success=False,
                error_code="REPOSITORY_NOT_FOUND",
                message=rnfe.message,
                details=rnfe.details
            ).model_dump()
        )
    except RateLimitExceededError as rle:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ErrorResponse(
                success=False,
                error_code="RATE_LIMIT_EXCEEDED",
                message=rle.message,
                details=rle.details
            ).model_dump()
        )
    except GitHubAPIException as ge:
        logger.error("GitHub API error during mining: %s (status %d)", ge.message, ge.status_code)
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
        logger.exception("Unexpected server error mining '%s': %s", payload.url, str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred during repository mining.",
                details=str(e)
            ).model_dump()
        )


@app.get(
    f"{settings.API_V1_PREFIX}/repository/mine",
    response_model=RepositoryMiningResponse,
    tags=["Repository Mining (M0.2)"]
)
async def mine_repository_get(
    url: str = Query(..., description="GitHub repository URL or owner/repo"),
    max_pages: int = Query(3, ge=1, le=50, description="Max pagination pages per category"),
    per_page: int = Query(100, ge=1, le=100, description="Items per page")
):
    """
    GET endpoint for repository mining pipeline to allow easy browser or cURL testing.
    """
    req = RepositoryMiningRequest(url=url, max_pages_per_category=max_pages, per_page=per_page)
    return await mine_repository_post(req)


@app.post(
    f"{settings.API_V1_PREFIX}/repository/mine/graphql",
    response_model=GraphQLMiningResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository input"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        429: {"model": ErrorResponse, "description": "GraphQL rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "GraphQL server error"},
    },
    tags=["Repository Mining (M0.2 GraphQL)"]
)
async def mine_repository_graphql_post(payload: GraphQLMiningRequest):
    """
    M0.2: GitHub GraphQL API repository mining pipeline.
    Collects repository metadata, pull requests (with reviews), issues, commits,
    and mentionable contributors in a single batched query with cursor pagination.
    """
    try:
        return await graphql_service.mine_repository(payload)
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_REPOSITORY_URL",
                message=str(ve),
            ).model_dump()
        )
    except RuntimeError as re:
        err_msg = str(re)
        if "rate limit" in err_msg.lower():
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ErrorResponse(
                    success=False,
                    error_code="GRAPHQL_RATE_LIMIT_EXCEEDED",
                    message=err_msg,
                ).model_dump()
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="GRAPHQL_QUERY_ERROR",
                message=err_msg,
            ).model_dump()
        )
    except Exception as e:
        logger.exception("Unexpected error in GraphQL mining: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="INTERNAL_SERVER_ERROR",
                message=str(e),
            ).model_dump()
        )


@app.post(
    f"{settings.API_V1_PREFIX}/archive/ingest",
    response_model=GHArchiveIngestionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid archive ingestion request"},
        500: {"model": ErrorResponse, "description": "Archive processing error"},
    },
    tags=["GH Archive Historical Events (M0.2)"]
)
async def ingest_gh_archive_events(payload: GHArchiveIngestionRequest):
    """
    M0.2: Ingests and normalizes historical GitHub event streams from GH Archive / BigQuery.
    Processes PushEvent, PullRequestEvent, IssuesEvent, IssueCommentEvent, PullRequestReviewEvent, and WatchEvent.
    """
    try:
        return await archive_service.ingest_events(payload)
    except Exception as e:
        logger.exception("Error ingesting GH Archive events: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="ARCHIVE_INGESTION_ERROR",
                message=str(e),
            ).model_dump()
        )



# =============================================================================
# M0.3: Composite Indicators & Repository Health Index Endpoints
# =============================================================================

@app.post(
    f"{settings.API_V1_PREFIX}/indicators/calculate",
    response_model=CalculateIndicatorsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid payload or repository URL"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        500: {"model": ErrorResponse, "description": "Calculation error"},
    },
    tags=["Composite Indicators (M0.3)"]
)
async def calculate_indicators_post(payload: CalculateIndicatorsRequest):
    """
    M0.3: Calculates M0.1 registered metrics, normalizes values, evaluates dimensions,
    and computes the Repository Health Index (RHI) using M0.2 mined data or by mining a URL.
    """
    try:
        mined_data = payload.mining_data
        if not mined_data and payload.url:
            mining_res = await mining_service.mine_repository(RepositoryMiningRequest(url=payload.url))
            mined_data = mining_res.data

        if not mined_data:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    success=False,
                    error_code="MISSING_DATA",
                    message="Either 'mining_data' or a valid repository 'url' must be provided.",
                    details="Provide M0.2 mined repository data or a repository URL to collect and calculate."
                ).model_dump()
            )

        result = indicator_service.calculate_indicators(mined_data)
        return CalculateIndicatorsResponse(
            success=True,
            message="Indicators and Repository Health Index calculated successfully.",
            data=result
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_REPOSITORY_INPUT",
                message=str(ve),
            ).model_dump()
        )
    except Exception as e:
        logger.exception("Error calculating indicators: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="CALCULATION_ERROR",
                message=f"Failed to calculate indicators: {str(e)}",
            ).model_dump()
        )


@app.get(
    f"{settings.API_V1_PREFIX}/indicators",
    response_model=CalculateIndicatorsResponse,
    tags=["Composite Indicators (M0.3)"]
)
async def calculate_indicators_get(url: str = Query(..., description="Repository URL or owner/repo")):
    """GET convenience endpoint to mine a repository and calculate its health indicators."""
    req = CalculateIndicatorsRequest(url=url)
    return await calculate_indicators_post(req)


# =============================================================================
# M0.4: Survival Analysis Endpoints
# =============================================================================

@app.post(
    f"{settings.API_V1_PREFIX}/survival/estimate",
    response_model=SurvivalAnalysisReport,
    tags=["Survival Analysis (M0.4)"]
)
async def estimate_survival_cohort(payload: SurvivalEstimateRequest):
    """
    M0.4: Fits non-parametric Kaplan-Meier survival curves and optional Cox Proportional
    Hazards regression on a cohort of repository survival observations.
    """
    km_res = survival_service.fit_kaplan_meier(payload.observations)
    cox_res = None
    if payload.include_cox:
        cox_res = survival_service.fit_cox_ph(payload.observations)

    censored_rate = round(km_res.censored_count / km_res.sample_size, 4) if km_res.sample_size > 0 else 0.0

    return SurvivalAnalysisReport(
        dataset_type="cross_sectional_cohort",
        sample_size=km_res.sample_size,
        event_count=km_res.event_count,
        censored_count=km_res.censored_count,
        censoring_rate=censored_rate,
        kaplan_meier=km_res,
        cox_regression=cox_res,
        data_limitations=[
            "Survival estimation requires cross-sectional cohort observations with verified failure/censoring timestamps.",
            "Results valid only under proportional hazards and uninformative censoring assumptions."
        ],
        future_data_requirements=[
            "Longitudinal repository event logs from GH Archive / BigQuery for larger cohorts."
        ]
    )


@app.get(
    f"{settings.API_V1_PREFIX}/survival/benchmark",
    response_model=SurvivalAnalysisReport,
    tags=["Survival Analysis (M0.4)"]
)
async def get_survival_benchmark():
    """
    M0.4: Retrieves Kaplan-Meier survival curve and Cox regression results on the
    standard calibrated synthetic open-source repository benchmark cohort (N=150).
    """
    return survival_service.run_benchmark_analysis()


@app.get(
    f"{settings.API_V1_PREFIX}/survival/repository",
    response_model=SingleRepoSurvivalAssessment,
    tags=["Survival Analysis (M0.4)"]
)
async def assess_single_repository_survival(url: str = Query(..., description="Repository URL or owner/repo")):
    """
    M0.4: Assesses survival status, elapsed lifespan, and right-censoring diagnostics
    for an individual live repository snapshot, explaining snapshot data limitations.
    """
    try:
        repo_info, _ = await github_service.fetch_repository(url)
        return survival_service.assess_single_repository(repo_info.model_dump())
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_REPOSITORY_URL",
                message=str(ve),
            ).model_dump()
        )
    except RepositoryNotFoundError as rnfe:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                success=False,
                error_code="REPOSITORY_NOT_FOUND",
                message=rnfe.message,
            ).model_dump()
        )


# =============================================================================
# M0.5: Evidence-Grounded LLM Report Generation Endpoints
# =============================================================================

@app.post(
    f"{settings.API_V1_PREFIX}/report/generate",
    response_model=GenerateReportResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository input"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        500: {"model": ErrorResponse, "description": "Report generation error"},
    },
    tags=["LLM Report Generation (M0.5)"]
)
async def generate_report_post(payload: GenerateReportRequest):
    """
    M0.5: Generates a comprehensive, evidence-grounded repository intelligence report
    synthesized from M0.3 composite indicators and M0.4 survival analysis.
    Uses Gemini API if configured, with deterministic empirical fallback.
    """
    try:
        indicators = payload.indicators
        survival = payload.survival

        # If indicators not directly passed, compute from URL
        if not indicators:
            if not payload.url:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=ErrorResponse(
                        success=False,
                        error_code="MISSING_INPUT",
                        message="Either pre-calculated 'indicators' or a repository 'url' must be provided."
                    ).model_dump()
                )
            
            # Mine and compute indicators
            mining_res = await mining_service.mine_repository(RepositoryMiningRequest(url=payload.url))
            indicators = indicator_service.calculate_indicators(mining_res.data)
            survival = survival_service.assess_single_repository(mining_res.data.repository)

        if not survival:
            survival = survival_service.assess_single_repository({"full_name": indicators.repository_name})

        report = await report_service.generate_report(
            indicators=indicators,
            survival=survival,
            model_name=payload.model_name
        )

        return GenerateReportResponse(
            success=True,
            message="Repository health report generated successfully.",
            data=report
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_code="INVALID_INPUT",
                message=str(ve),
            ).model_dump()
        )
    except Exception as e:
        logger.exception("Error generating health report: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error_code="REPORT_GENERATION_ERROR",
                message=f"Failed to generate report: {str(e)}",
            ).model_dump()
        )


@app.get(
    f"{settings.API_V1_PREFIX}/report",
    response_model=GenerateReportResponse,
    tags=["LLM Report Generation (M0.5)"]
)
async def generate_report_get(url: str = Query(..., description="Repository URL or owner/repo")):
    """GET convenience endpoint to generate full health report for a repository URL."""
    req = GenerateReportRequest(url=url)
    return await generate_report_post(req)



