"""
Pydantic Schemas for M0.3: Composite Indicators & Repository Health Index (RHI).
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MetricValue(BaseModel):
    """Calculated value and metadata for an individual metric."""
    model_config = ConfigDict(extra="ignore")

    metric_id: str = Field(..., description="Canonical metric ID (e.g. A1, A2, C1)")
    metric_name: str = Field(..., description="Human-readable title")
    raw_value: Optional[float] = Field(None, description="Computed raw numeric value")
    formatted_value: str = Field(..., description="Human-friendly string representation")
    unit: Optional[str] = Field(None, description="Measurement unit")
    direction: str = Field(..., description="higher_is_better, lower_is_better, or contextual")
    normalized_score: Optional[float] = Field(
        None, description="Scale-normalized score bounded in [0.0, 1.0], 1.0 is healthiest"
    )
    weight: float = Field(default=0.0, description="Assigned weight in composite health index")
    chaoss_family: str = Field(..., description="CHAOSS Metric Family")
    linaker_area: str = Field(..., description="Linåker et al. (2026) Health Area")
    status: str = Field("calculated", description="'calculated', 'missing_data', 'provisional', 'not_applicable'")
    notes: Optional[str] = Field(None, description="Contextual, validation, or truncation caveats")


class DimensionScore(BaseModel):
    """Aggregate score for a health dimension."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Dimension title")
    score: Optional[float] = Field(None, description="Aggregated dimension score in [0.0, 100.0]")
    metrics_available: int = Field(..., description="Count of calculated metrics in this dimension")
    metrics_total: int = Field(..., description="Total defined metrics in this dimension")
    metrics: List[MetricValue] = Field(default_factory=list, description="Child metrics")


class HealthIndexResult(BaseModel):
    """Complete result of composite health index calculation."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str = Field(..., description="Repository full name (owner/repo)")
    rhi_score: Optional[float] = Field(
        None, description="Repository Health Index score [0.0, 100.0], or None if coverage is insufficient"
    )
    rhi_grade: str = Field(
        ..., description="Qualitative grade ('A', 'B', 'C', 'D', 'F', or 'Insufficient Data')"
    )
    coverage_ratio: float = Field(
        ..., description="Proportion of weighted health metrics with sufficient data [0.0, 1.0]"
    )
    coverage_sufficient: bool = Field(
        ..., description="True if coverage_ratio meets minimum threshold (>= 0.40)"
    )
    metrics: Dict[str, MetricValue] = Field(
        default_factory=dict, description="Core health metrics contributing to RHI"
    )
    context_variables: Dict[str, MetricValue] = Field(
        default_factory=dict, description="Contextual covariates (e.g. Age, Popularity) separated from RHI"
    )
    data_quality_indicators: Dict[str, MetricValue] = Field(
        default_factory=dict, description="Data collection diagnostic metrics (e.g. Capture Rate)"
    )
    dimensions: Dict[str, DimensionScore] = Field(
        default_factory=dict, description="Dimension-level breakdown scores"
    )
    missing_metrics: List[str] = Field(
        default_factory=list, description="IDs of metrics that could not be computed due to absent data"
    )
    calculation_timestamp: str = Field(..., description="UTC ISO-8601 calculation timestamp")


class CalculateIndicatorsRequest(BaseModel):
    """Payload to trigger indicator calculation."""
    url: Optional[str] = Field(None, description="Repository URL or shorthand to mine and calculate")
    mining_data: Optional[Dict[str, Any]] = Field(None, description="Pre-collected M0.2 mining data")


class CalculateIndicatorsResponse(BaseModel):
    """API response for indicator calculation."""
    success: bool = True
    message: str = "Composite indicators calculated successfully."
    data: HealthIndexResult

