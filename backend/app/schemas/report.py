"""
Pydantic Schemas for M0.5: Evidence-Grounded LLM Health Report Generation.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .indicators import HealthIndexResult
from .survival import SingleRepoSurvivalAssessment


class ReportStrength(BaseModel):
    """An empirical strength identified from computed metrics."""
    model_config = ConfigDict(extra="ignore")

    dimension: str = Field(..., description="Relevant health dimension")
    finding: str = Field(..., description="Observed positive pattern")
    evidence_metric: str = Field(..., description="Grounded metric proof (e.g. 'A1 PRAR = 85.0%')")
    interpretation: str = Field(..., description="Why this benefits prospective adopters or maintainers")


class ReportRisk(BaseModel):
    """A risk factor, bottleneck, or deterioration warning identified from evidence."""
    model_config = ConfigDict(extra="ignore")

    dimension: str = Field(..., description="Relevant health dimension")
    severity: str = Field(..., description="'high', 'medium', or 'low'")
    finding: str = Field(..., description="Specific concern or bottleneck")
    evidence_metric: str = Field(..., description="Grounded metric proof (e.g. 'A6 Issue Latency = 45 days')")
    mitigation_advice: str = Field(..., description="Actionable recommendation to address the risk")


class AdoptionRecommendation(BaseModel):
    """Decision-support adoption recommendation."""
    model_config = ConfigDict(extra="ignore")

    verdict: str = Field(..., description="'RECOMMENDED', 'RECOMMENDED_WITH_CAUTION', or 'NOT_RECOMMENDED'")
    summary: str = Field(..., description="High-level decision recommendation")
    key_drivers: List[str] = Field(default_factory=list, description="Primary metrics driving the verdict")
    target_audience_notes: str = Field(..., description="Contextual guidance for enterprise vs experimental use")


class RepositoryHealthReport(BaseModel):
    """Comprehensive, evidence-grounded repository intelligence report."""
    model_config = ConfigDict(extra="ignore")

    repository_name: str = Field(..., description="Repository full name")
    generated_at: str = Field(..., description="UTC ISO-8601 generation timestamp")
    provider: str = Field(..., description="'gemini' or 'deterministic_fallback'")
    executive_summary: str = Field(..., description="Synthesized executive summary")
    health_index_summary: Dict[str, Any] = Field(
        ..., description="RHI score, grade, and coverage summary"
    )
    strengths: List[ReportStrength] = Field(
        default_factory=list, description="Identified empirical strengths"
    )
    risks_and_bottlenecks: List[ReportRisk] = Field(
        default_factory=list, description="Identified risks and bottlenecks"
    )
    survival_sustainability_assessment: str = Field(
        ..., description="Lifespan and longitudinal sustainability analysis"
    )
    adoption_recommendation: AdoptionRecommendation = Field(
        ..., description="Decision-support adoption guidance"
    )
    methodological_limitations: List[str] = Field(
        default_factory=list, description="Explicit data, coverage, and sampling limitations"
    )


class GenerateReportRequest(BaseModel):
    """Payload to trigger report generation."""
    url: Optional[str] = Field(None, description="Repository URL or owner/repo to mine and analyze end-to-end")
    indicators: Optional[HealthIndexResult] = Field(None, description="Pre-computed M0.3 indicators")
    survival: Optional[SingleRepoSurvivalAssessment] = Field(None, description="Pre-computed M0.4 survival assessment")
    model_name: Optional[str] = Field("gemini-1.5-flash", description="Gemini model identifier")


class GenerateReportResponse(BaseModel):
    """API response for report generation."""
    success: bool = True
    message: str = "Repository health report generated successfully."
    data: RepositoryHealthReport

