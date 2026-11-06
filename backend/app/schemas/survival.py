"""
Pydantic Schemas for M0.4: Repository Survival Analysis.
Supports Kaplan-Meier estimation, Cox Proportional Hazards regression,
and single-repository lifespan diagnostics.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SurvivalObservation(BaseModel):
    """Individual survival observation for a repository or event."""
    model_config = ConfigDict(extra="ignore")

    subject_id: str = Field(..., description="Repository identifier (e.g. 'owner/repo')")
    duration: float = Field(..., gt=0, description="Observed lifespan/duration in days (strictly > 0)")
    event: int = Field(
        ..., ge=0, le=1, description="Event occurrence indicator: 1 = event (deprecated/archived/inactive), 0 = censored"
    )
    covariates: Dict[str, float] = Field(
        default_factory=dict, description="Predictor covariates (e.g. stars, prar, commits_per_month)"
    )


class KaplanMeierPoint(BaseModel):
    """Estimated survival point at a distinct timeline event."""
    model_config = ConfigDict(extra="ignore")

    timeline: float = Field(..., description="Timeline point (days)")
    n_at_risk: int = Field(..., description="Count of subjects at risk prior to this point")
    n_events: int = Field(..., description="Count of terminal events at this point")
    n_censored: int = Field(..., description="Count of censored observations between this and next point")
    survival_probability: float = Field(..., ge=0.0, le=1.0, description="Estimated survival probability S(t)")
    confidence_lower: Optional[float] = Field(None, ge=0.0, le=1.0, description="95% CI lower bound (Greenwood)")
    confidence_upper: Optional[float] = Field(None, ge=0.0, le=1.0, description="95% CI upper bound (Greenwood)")


class KaplanMeierResult(BaseModel):
    """Output of Kaplan-Meier non-parametric survival analysis."""
    model_config = ConfigDict(extra="ignore")

    timeline: List[float] = Field(default_factory=list, description="Array of event timeline points (days)")
    survival_table: List[KaplanMeierPoint] = Field(
        default_factory=list, description="Stepwise life table with survival probabilities"
    )
    median_survival_time: Optional[float] = Field(
        None, description="Median survival time in days (time where S(t) <= 0.50), or None if not reached"
    )
    sample_size: int = Field(..., description="Total sample size N")
    event_count: int = Field(..., description="Total terminal events observed (E)")
    censored_count: int = Field(..., description="Total right-censored subjects (C)")


class CoxCovariateResult(BaseModel):
    """Regression coefficient and hazard ratio for a single covariate."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Covariate name")
    coef: float = Field(..., description="Log-hazard ratio coefficient (beta)")
    hazard_ratio: float = Field(..., description="Hazard ratio exp(beta)")
    std_err: float = Field(..., description="Standard error of coefficient")
    z_score: float = Field(..., description="Wald test statistic (z)")
    p_value: float = Field(..., description="Two-tailed p-value")
    ci_lower: float = Field(..., description="95% CI lower bound of hazard ratio")
    ci_upper: float = Field(..., description="95% CI upper bound of hazard ratio")


class CoxRegressionResult(BaseModel):
    """Output of Cox Proportional Hazards regression model."""
    model_config = ConfigDict(extra="ignore")

    is_fitted: bool = Field(..., description="True if optimization converged successfully")
    log_likelihood: Optional[float] = Field(None, description="Log partial likelihood at convergence")
    log_likelihood_null: Optional[float] = Field(None, description="Log partial likelihood of null model")
    concordance_index: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Harrell's concordance index (C-index) for model discrimination"
    )
    covariates: List[CoxCovariateResult] = Field(default_factory=list, description="Estimated coefficients")
    notes: Optional[str] = Field(None, description="Model diagnostics and assumption warnings")


class SurvivalAnalysisReport(BaseModel):
    """Comprehensive survival analysis result on a cohort of repositories."""
    model_config = ConfigDict(extra="ignore")

    dataset_type: str = Field(
        ..., description="'synthetic_benchmark', 'cross_sectional_cohort', or 'single_repo_snapshot'"
    )
    sample_size: int = Field(..., description="Number of observed repositories in cohort")
    event_count: int = Field(..., description="Number of inactive/deprecated repositories")
    censored_count: int = Field(..., description="Number of active/censored repositories")
    censoring_rate: float = Field(..., description="Proportion of sample that is right-censored [0.0, 1.0]")
    kaplan_meier: KaplanMeierResult = Field(..., description="Kaplan-Meier survival estimation")
    cox_regression: Optional[CoxRegressionResult] = Field(None, description="Cox Proportional Hazards model")
    data_limitations: List[str] = Field(default_factory=list, description="Methodological limitations")
    future_data_requirements: List[str] = Field(default_factory=list, description="Unmet historical data needs")


class SingleRepoSurvivalAssessment(BaseModel):
    """Lifespan diagnosis for an individual repository snapshot."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str = Field(..., description="Repository full name")
    observed_lifespan_days: float = Field(..., description="Elapsed days from creation to current date")
    observed_lifespan_years: float = Field(..., description="Elapsed years from creation to current date")
    censoring_status: str = Field(
        ..., description="'right_censored' (active project) or 'event_observed' (archived/deprecated)"
    )
    is_censored: bool = Field(..., description="True if project is still alive and actively maintained")
    is_archived: bool = Field(..., description="True if marked archived on GitHub")
    eligible_for_standalone_km: bool = Field(
        False, description="Always False: a single snapshot cannot generate a Kaplan-Meier survival curve"
    )
    benchmark_cohort_comparison: Optional[Dict[str, Any]] = Field(
        None, description="Position relative to benchmark survival curve if comparable"
    )
    methodological_caveats: List[str] = Field(
        default_factory=list, description="Scientific limitations regarding snapshot vs historical survival"
    )


class SurvivalEstimateRequest(BaseModel):
    """Request payload for custom survival dataset estimation."""
    observations: List[SurvivalObservation] = Field(
        ..., min_length=2, description="Cohort of repository survival observations"
    )
    include_cox: bool = Field(True, description="Whether to fit Cox Proportional Hazards model")

