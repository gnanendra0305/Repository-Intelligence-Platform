"""
Pydantic Schemas for M0.2: GH Archive Historical Event Ingestion.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class HistoricalEventType(str, Enum):
    """Supported GH Archive event types relevant to OSS health and survival."""
    PUSH = "PushEvent"
    PULL_REQUEST = "PullRequestEvent"
    ISSUES = "IssuesEvent"
    ISSUE_COMMENT = "IssueCommentEvent"
    PULL_REQUEST_REVIEW = "PullRequestReviewEvent"
    WATCH = "WatchEvent"


class HistoricalEventRecord(BaseModel):
    """Normalized, deduplicated historical event record from GH Archive or BigQuery."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Unique GH Archive event ID")
    type: HistoricalEventType = Field(..., description="GitHub event type")
    repository_name: str = Field(..., description="Repository full name (owner/repo)")
    actor_login: str = Field(..., description="GitHub username of the event actor")
    created_at: str = Field(..., description="Event ISO-8601 timestamp")
    action: Optional[str] = Field(None, description="Action subtype (opened, closed, merged, created, etc.)")
    payload_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Key extracted payload fields (e.g. pr_number, commit_count)"
    )


class HistoricalTimelineSummary(BaseModel):
    """Longitudinal aggregation of historical events supporting M0.3 indicators and M0.4 survival."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str
    first_event_at: Optional[str]
    last_event_at: Optional[str]
    total_events: int
    event_type_counts: Dict[str, int]
    unique_actors_count: int
    monthly_activity_distribution: Dict[str, int]
    is_dormant_last_12m: bool = Field(
        ..., description="True if no push or PR merge events observed in the final 12 months of timeline"
    )


class GHArchiveIngestionRequest(BaseModel):
    """Payload to trigger historical event ingestion."""
    repository_name: str = Field(
        ..., description="Target repository name to filter (owner/repo)"
    )
    start_date: Optional[str] = Field(
        None, description="Start date filter (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None, description="End date filter (YYYY-MM-DD)"
    )
    raw_events_jsonl: Optional[str] = Field(
        None, description="Raw newline-delimited JSON string of GH Archive or BigQuery events"
    )
    hourly_archive_urls: Optional[List[str]] = Field(
        None, description="Explicit list of data.gharchive.org URLs to fetch and parse"
    )


class GHArchiveIngestionResponse(BaseModel):
    """API response for historical event ingestion."""
    success: bool = True
    message: str = "GH Archive events ingested successfully."
    repository_name: str
    records_ingested: int
    unique_records_retained: int
    duplicate_records_dropped: int
    timeline_summary: HistoricalTimelineSummary
    events: List[HistoricalEventRecord] = Field(
        default_factory=list, description="Normalized event records"
    )
    warnings: List[str] = Field(default_factory=list)

