"""
Pydantic schemas for M0.2: GitHub Repository Mining (REST API Collection Pipeline).
Defines structured records for repository metadata, pull requests, issues, commits, contributors,
and collection metadata/diagnostics.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

from .repository import RepositoryInfo


class PullRequestRecord(BaseModel):
    """Normalized pull request record collected from GitHub REST API."""
    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="GitHub internal PR ID")
    number: int = Field(..., description="Repository pull request number (#)")
    title: str = Field(..., description="PR title")
    state: str = Field(..., description="State: 'open' or 'closed'")
    is_merged: bool = Field(False, description="Whether the PR has been merged")
    created_at: str = Field(..., description="Creation ISO-8601 timestamp")
    updated_at: Optional[str] = Field(None, description="Last updated ISO-8601 timestamp")
    closed_at: Optional[str] = Field(None, description="Closure ISO-8601 timestamp if closed")
    merged_at: Optional[str] = Field(None, description="Merge ISO-8601 timestamp if merged")
    author_login: Optional[str] = Field(None, description="GitHub username of PR author")
    draft: bool = Field(False, description="Whether PR is marked as draft")
    html_url: Optional[str] = Field(None, description="Web URL to PR on GitHub")
    comments_count: Optional[int] = Field(None, description="Comment count if present on the payload")


class IssueRecord(BaseModel):
    """
    Normalized issue record collected from GitHub REST API.
    Guaranteed to represent genuine issues, excluding pull requests.
    """
    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="GitHub internal issue ID")
    number: int = Field(..., description="Repository issue number (#)")
    title: str = Field(..., description="Issue title")
    state: str = Field(..., description="State: 'open' or 'closed'")
    created_at: str = Field(..., description="Creation ISO-8601 timestamp")
    updated_at: Optional[str] = Field(None, description="Last updated ISO-8601 timestamp")
    closed_at: Optional[str] = Field(None, description="Closure ISO-8601 timestamp if closed")
    author_login: Optional[str] = Field(None, description="GitHub username of issue creator")
    comments_count: int = Field(default=0, description="Count of comments on this issue")
    labels: List[str] = Field(default_factory=list, description="List of issue label names")
    html_url: Optional[str] = Field(None, description="Web URL to issue on GitHub")


class CommitRecord(BaseModel):
    """Normalized commit record collected from GitHub REST API."""
    model_config = ConfigDict(extra="ignore")

    sha: str = Field(..., description="Full 40-character commit SHA hash")
    message: str = Field(..., description="Commit message header/summary")
    author_name: Optional[str] = Field(None, description="Git author name")
    author_email: Optional[str] = Field(None, description="Git author email")
    author_date: Optional[str] = Field(None, description="Author timestamp ISO-8601")
    author_login: Optional[str] = Field(None, description="GitHub username if linked")
    committer_date: Optional[str] = Field(None, description="Committer timestamp ISO-8601")
    html_url: Optional[str] = Field(None, description="Web URL to commit on GitHub")


class ContributorRecord(BaseModel):
    """Normalized contributor record collected from GitHub REST API."""
    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., description="GitHub user ID")
    login: str = Field(..., description="GitHub username")
    avatar_url: Optional[str] = Field(None, description="User avatar image URL")
    contributions_count: int = Field(..., description="Total committed contributions count")
    html_url: Optional[str] = Field(None, description="Web URL to contributor profile")
    user_type: str = Field(default="User", description="Account type: 'User' or 'Bot'")


class CategoryCollectionStats(BaseModel):
    """Detailed statistics for each collected category."""
    records_count: int = Field(0, description="Total unique records collected")
    pages_fetched: int = Field(0, description="Total API pages requested")
    has_more: bool = Field(False, description="Whether additional uncollected pages remain")
    status: str = Field("success", description="Status: 'success', 'partial', 'skipped', or 'error'")
    error_message: Optional[str] = Field(None, description="Error detail if collection failed")


class RateLimitInfo(BaseModel):
    """GitHub REST API rate limit status snapshot. Never includes credentials."""
    remaining: Optional[int] = Field(None, description="Remaining API requests in current window")
    limit: Optional[int] = Field(None, description="Total hourly quota")
    reset_timestamp: Optional[int] = Field(None, description="Epoch timestamp of quota reset")
    reset_time_utc: Optional[str] = Field(None, description="Formatted UTC reset time string")
    used: Optional[int] = Field(None, description="Requests consumed in current window")
    retry_after_seconds: Optional[int] = Field(None, description="Retry-After value from the last throttled response")
    authenticated: bool = Field(
        False,
        description="True if a GitHub token was configured for this process. The token itself is never returned.",
    )


class MetricFieldCoverage(BaseModel):
    """Whether M0.1 registered payload fields are present in this REST collection (no metric computation)."""
    metric_id: str
    metric_name: str
    raw_data_available: bool = Field(
        ...,
        description="True when every required_payload_field can be sourced from this REST collection pipeline.",
    )
    missing_payload_fields: List[str] = Field(default_factory=list)
    missing_api_endpoints: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class CollectionMetadata(BaseModel):
    """Comprehensive diagnostic and audit metadata for the mining operation."""
    repository_full_name: str = Field(..., description="Target repository identifier (owner/repo)")
    collection_timestamp: str = Field(..., description="UTC ISO-8601 execution timestamp")
    status: str = Field(..., description="Overall status: 'complete', 'partial', or 'failed'")
    is_complete: bool = Field(
        ...,
        description="True only if all requested categories finished without cutoff, errors, or rate-limit interruption.",
    )
    categories: Dict[str, CategoryCollectionStats] = Field(
        default_factory=dict,
        description="Per-category collection statistics",
    )
    total_records_collected: int = Field(0, description="Grand total of unique collected records")
    pages_fetched_total: int = Field(0, description="Sum of pages fetched across categories")
    rate_limit: RateLimitInfo = Field(
        default_factory=RateLimitInfo,
        description="Rate-limit status at termination of collection",
    )
    errors: List[str] = Field(default_factory=list, description="Fatal or category-level error messages")
    warnings: List[str] = Field(default_factory=list, description="Diagnostic warnings")
    metric_coverage: List[MetricFieldCoverage] = Field(
        default_factory=list,
        description="M0.1 metric raw-data coverage for this collection (formulas are not computed).",
    )


class RepositoryMiningData(BaseModel):
    """Container for all structured records mined from GitHub."""
    repository: Optional[RepositoryInfo] = Field(
        None,
        description="Core repository metadata from GET /repos/{owner}/{repo}",
    )
    pull_requests: List[PullRequestRecord] = Field(default_factory=list)
    issues: List[IssueRecord] = Field(default_factory=list, description="Genuine issues only (PRs excluded)")
    commits: List[CommitRecord] = Field(default_factory=list)
    contributors: List[ContributorRecord] = Field(default_factory=list)


class RepositoryMiningRequest(BaseModel):
    """Payload schema for repository mining requests."""
    url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g. https://github.com/fastapi/fastapi) or owner/repo shorthand.",
    )
    max_pages_per_category: int = Field(
        default=3,
        ge=1,
        le=50,
        description="Maximum pagination pages to collect per category. Collection is partial if more pages remain.",
    )
    per_page: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Number of records requested per page (GitHub max: 100).",
    )
    categories: Optional[List[str]] = Field(
        default=None,
        description=(
            "Subset of categories to collect: "
            "['metadata', 'pull_requests', 'issues', 'commits', 'contributors']. None collects all."
        ),
    )


class RepositoryMiningResponse(BaseModel):
    """Top-level response schema for repository mining API."""
    success: bool = True
    message: str = "Repository mining completed successfully."
    metadata: CollectionMetadata
    data: RepositoryMiningData
