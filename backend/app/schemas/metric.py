from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CHAOSSFamily(str, Enum):
    """
    Primary metric classification from the Linux Foundation CHAOSS project.
    Represents the 5 official CHAOSS Working Group Metric Families.
    """
    EVOLUTION = "Evolution"
    RISK = "Risk"
    VALUE = "Value"
    DIVERSITY_EQUITY_INCLUSION = "Diversity, Equity & Inclusion (DEI)"
    COMMON_METRICS = "Common Metrics"


class LinakerArea(str, Enum):
    """
    Secondary research taxonomy from Linåker et al. (2026),
    "Assessing Open Source Software Health in Organizations' Intake Processes".
    Represents the 5 Areas of Health elicited from practitioners.
    """
    COMMUNITY_PRODUCTIVITY = "Community Productivity"
    COMMUNITY_STABILITY = "Community Stability"
    ORCHESTRATION = "Orchestration"
    PRODUCTION_PROCESS = "Production Process"
    PRODUCTION_OUTPUT = "Production Output"


class MetricType(str, Enum):
    """Functional role of the metric in the platform."""
    HEALTH = "health"
    CONTEXT = "context"
    DATA_QUALITY = "data_quality"
    DERIVED = "derived"


class ProvenanceClass(str, Enum):
    """Origin and research justification of the metric formula."""
    DIRECT = "direct"       # Verbatim published equation from literature
    DERIVED = "derived"     # Operationalisation derived from research prose definition
    PROPOSED = "proposed"   # Original project-proposed formula or adaptation


class MetricDirection(str, Enum):
    """Directionality indicating healthier states."""
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"
    CONTEXTUAL = "contextual"
    NOT_APPLICABLE = "not_applicable"


class ImplementationStatus(str, Enum):
    """Lifecycle status of the metric in the implementation roadmap."""
    IMPLEMENTED = "implemented"
    PLANNED = "planned"
    PROVISIONAL = "provisional"
    EXPERIMENTAL = "experimental"


class MetricDefinition(BaseModel):
    """
    Standardized Metric Registry definition schema.
    Satisfies M0.1: OSS Health & Sustainability Concepts; CHAOSS Metric Families.
    """
    model_config = ConfigDict(use_enum_values=True)

    metric_id: str = Field(
        ...,
        description="Unique canonical identifier for the metric (e.g. 'A1', 'A2', 'C1')."
    )
    metric_name: str = Field(
        ...,
        description="Human-readable title of the metric."
    )
    description: str = Field(
        ...,
        description="Comprehensive summary of what this metric measures and why it matters."
    )
    chaoss_family: CHAOSSFamily = Field(
        ...,
        description="Primary classification: CHAOSS Working Group Metric Family."
    )
    linaker_area: LinakerArea = Field(
        ...,
        description="Secondary research mapping: Linåker et al. (2026) 5 Health Areas."
    )
    metric_type: MetricType = Field(
        ...,
        description="Functional role: health indicator, context covariate, data quality, or derived."
    )
    operational_definition: str = Field(
        ...,
        description="Precise operational definition of how the construct is observed."
    )
    formula: Optional[str] = Field(
        None,
        description="Mathematical equation. None if formula is provisional, under revision, or undefined."
    )
    required_data: List[str] = Field(
        default_factory=list,
        description="Descriptive list of data entities required (e.g. 'Pull Request creation timestamps')."
    )
    data_source: str = Field(
        ...,
        description="Origin of the data (e.g. 'GitHub REST API', 'Ingestion Pipeline Metadata')."
    )
    required_api_endpoints: List[str] = Field(
        default_factory=list,
        description="GitHub API endpoints used to collect inputs (e.g. '/repos/{owner}/{repo}/pulls')."
    )
    required_payload_fields: List[str] = Field(
        default_factory=list,
        description="Specific fields extracted from raw payloads (e.g. ['created_at', 'merged_at', 'state'])."
    )
    unit: Optional[str] = Field(
        None,
        description="Measurement unit (e.g. 'ratio [0,1]', 'days', 'count', 'dimensionless')."
    )
    direction: MetricDirection = Field(
        default=MetricDirection.NOT_APPLICABLE,
        description="Directionality of health interpretation."
    )
    provenance_class: ProvenanceClass = Field(
        ...,
        description="Research provenance class: direct, derived, or proposed."
    )
    research_reference: str = Field(
        ...,
        description="Academic citation and specific section/table reference."
    )
    implementation_status: ImplementationStatus = Field(
        default=ImplementationStatus.PLANNED,
        description="Status: implemented, planned, provisional, or experimental."
    )
    validation_notes: Optional[str] = Field(
        None,
        description="Methodological limitations, edge cases, or validation requirements."
    )


class MetricListResponse(BaseModel):
    """API Response model for metric registry listings."""
    success: bool = True
    count: int = Field(..., description="Number of metrics returned in this response.")
    total_registered: int = Field(..., description="Total count of metrics in the registry.")
    chaoss_family_filter: Optional[str] = None
    linaker_area_filter: Optional[str] = None
    metric_type_filter: Optional[str] = None
    data: List[MetricDefinition]


class MetricDetailResponse(BaseModel):
    """API Response model for single metric retrieval."""
    success: bool = True
    data: MetricDefinition

