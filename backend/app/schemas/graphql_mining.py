"""
Pydantic Schemas for M0.2: GitHub GraphQL Mining Pipeline.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .mining import (
    RepositoryMiningData,
    RateLimitInfo,
)


class GraphQLRateLimit(BaseModel):
    """GitHub GraphQL API rate limit information."""
    model_config = ConfigDict(extra="ignore")

    limit: int = Field(5000, description="Total hourly point limit")
    cost: int = Field(1, description="Point cost of the executed query")
    remaining: int = Field(5000, description="Remaining point quota")
    reset_at: Optional[str] = Field(None, description="ISO-8601 reset timestamp")


class GraphQLMiningRequest(BaseModel):
    """Request payload for GraphQL-based repository mining."""
    url: str = Field(
        ...,
        description="GitHub repository URL (e.g. https://github.com/fastapi/fastapi) or owner/repo shorthand."
    )
    max_prs: int = Field(
        default=100, ge=1, le=500, description="Max pull requests to collect via cursor pagination"
    )
    max_issues: int = Field(
        default=100, ge=1, le=500, description="Max issues to collect via cursor pagination"
    )
    max_commits: int = Field(
        default=100, ge=1, le=500, description="Max commits to collect via cursor pagination"
    )


class GraphQLMiningMetadata(BaseModel):
    """Audit and diagnostic metadata for GraphQL mining operation."""
    model_config = ConfigDict(extra="ignore")

    repository_full_name: str
    collection_timestamp: str
    status: str  # 'complete', 'partial', 'failed'
    rate_limit: GraphQLRateLimit
    pages_fetched: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class GraphQLMiningResponse(BaseModel):
    """Top-level response schema for GraphQL repository mining API."""
    success: bool = True
    message: str = "GraphQL repository mining completed successfully."
    metadata: GraphQLMiningMetadata
    data: RepositoryMiningData

