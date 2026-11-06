"""
Pydantic Schemas for M1.4: Reproducible Ground-Truth Repository Labelling.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DormancyStatus(str, Enum):
    """12-month operational dormancy status."""
    ACTIVE = "active"
    DORMANT = "dormant"
    CENSORED_INSUFFICIENT_FOLLOWUP = "censored_insufficient_followup"
    UNKNOWN = "unknown"


class AbandonmentStatus(str, Enum):
    """12-month longitudinal abandonment status."""
    SUSTAINED = "sustained"
    ABANDONED = "abandoned"
    CENSORED_INSUFFICIENT_FOLLOWUP = "censored_insufficient_followup"
    AMBIGUOUS = "ambiguous"


class FoundationGraduationStatus(str, Enum):
    """Known-group validation classification (Apache / Eclipse Foundation)."""
    GRADUATED = "graduated"
    RETIRED = "retired"
    NOT_APPLICABLE = "not_applicable"


class RepositoryGroundTruthRecord(BaseModel):
    """Comprehensive ground-truth record for a repository."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str = Field(..., description="Full repository name (owner/repo)")
    observation_date_t: str = Field(..., description="Baseline observation date t (ISO 8601)")
    followup_date_t_plus_12: Optional[str] = Field(
        None, description="End of 12-month follow-up window (ISO 8601, t + 365 days)"
    )
    is_archived: bool = Field(
        False, description="Explicit GitHub archived status; kept strictly separate from dormancy"
    )
    dormancy_status: DormancyStatus = Field(
        ..., description="Dormancy label at t + 12 months (zero commits, PR merges, closed issues)"
    )
    abandonment_status: AbandonmentStatus = Field(
        ..., description="Abandonment label at t + 12 months (dormancy + neglected backlog)"
    )
    foundation_status: FoundationGraduationStatus = Field(
        FoundationGraduationStatus.NOT_APPLICABLE,
        description="Independent known-group benchmark classification (e.g. Apache/Eclipse)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in ground-truth assignment based on data completeness"
    )
    evidence_sources: List[str] = Field(
        default_factory=list, description="Auditable empirical sources supporting the assigned labels"
    )
    evidence_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Raw event counts observed within the follow-up window"
    )
    censoring_reason: Optional[str] = Field(
        None, description="Explanation if label is right-censored or ambiguous"
    )
    labelled_at: str = Field(..., description="Timestamp when label was evaluated (ISO 8601)")

