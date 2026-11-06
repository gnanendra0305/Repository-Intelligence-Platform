"""
Pydantic Schemas for M1.5: Stratified Repository Sampling Pipeline.
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class Ecosystem(str, Enum):
    """The three justified target OSS ecosystems."""
    PYTHON_PYPI = "python_pypi"
    JAVASCRIPT_NPM = "javascript_npm"
    RUST_CRATES = "rust_crates"


class AgeStratum(str, Enum):
    """Repository age stratification strata."""
    EMERGING = "emerging"       # < 2 years (< 730 days)
    ESTABLISHED = "established" # 2 - 5 years (730 - 1825 days)
    MATURE = "mature"           # > 5 years (> 1825 days)


class SizeStratum(str, Enum):
    """Repository size and activity stratification strata."""
    SMALL = "small"   # < 100 commits
    MEDIUM = "medium" # 100 - 1,000 commits
    LARGE = "large"   # > 1,000 commits


class InclusionCriteriaResult(BaseModel):
    """Verification results against pre-registered inclusion/exclusion rules."""
    model_config = ConfigDict(extra="ignore")

    is_eligible: bool = Field(..., description="True if repository satisfies all inclusion criteria")
    checks: Dict[str, bool] = Field(..., description="Individual rule evaluation results")
    exclusion_reasons: List[str] = Field(default_factory=list, description="Explicit failure reasons")


class SampledRepositoryRecord(BaseModel):
    """Auditable record of a sampled repository in the empirical study cohort."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str = Field(..., description="Full repository name (owner/repo)")
    ecosystem: Ecosystem = Field(..., description="Ecosystem stratum")
    age_stratum: AgeStratum = Field(..., description="Age classification stratum")
    size_stratum: SizeStratum = Field(..., description="Size classification stratum")
    observed_age_days: float = Field(..., description="Repository age in calendar days at sampling")
    observed_commit_count: int = Field(..., description="Total commit volume")
    is_active_at_sampling: bool = Field(..., description="False if repo was dormant/archived at sampling")
    is_archived: bool = Field(..., description="GitHub administrative archived state")
    sampling_date: str = Field(..., description="ISO 8601 sampling timestamp")
    label_availability: Dict[str, bool] = Field(
        ..., description="Availability of downstream ground-truth labels"
    )
    inclusion_result: InclusionCriteriaResult = Field(
        ..., description="Pre-registered criteria verification result"
    )


class StratifiedSamplingCohortSummary(BaseModel):
    """Aggregate distribution diagnostics of a sampled research cohort."""
    model_config = ConfigDict(extra="ignore")

    total_sampled: int = Field(..., description="Total number of eligible repositories in cohort")
    ecosystem_breakdown: Dict[str, int] = Field(..., description="Count per ecosystem")
    age_stratum_breakdown: Dict[str, int] = Field(..., description="Count per age stratum")
    size_stratum_breakdown: Dict[str, int] = Field(..., description="Count per size stratum")
    inactive_or_dead_count: int = Field(
        ..., description="Number of dormant/archived repositories included to counter survivorship bias"
    )
    inactive_proportion: float = Field(
        ..., ge=0.0, le=1.0, description="Proportion of sample representing inactive/dead projects"
    )
    is_balanced_design: bool = Field(
        ..., description="True if all strata contain representation meeting study quota"
    )

