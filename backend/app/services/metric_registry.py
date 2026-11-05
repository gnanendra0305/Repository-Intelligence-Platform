"""
Metric Registry Service
Module: M0.1 – OSS Health and Sustainability Concepts; CHAOSS Metric Families – Metric Registry

Central registry for repository health metrics, contextual variables, and data-quality indicators.
Implements primary classification via Linux Foundation CHAOSS Metric Families,
and secondary research mapping via Linåker et al. (2026) 5 Areas of OSS Health.
"""

from typing import List, Optional, Dict, Any, Union
from ..schemas.metric import (
    MetricDefinition,
    CHAOSSFamily,
    LinakerArea,
    MetricType,
    ProvenanceClass,
    MetricDirection,
    ImplementationStatus,
)


# Canonical registry catalogue
INITIAL_METRIC_DEFINITIONS: List[MetricDefinition] = [
    MetricDefinition(
        metric_id="A1",
        metric_name="Pull Request Acceptance Rate (PRAR)",
        description=(
            "The proportion of decided pull requests that were reviewed and successfully merged "
            "into the repository codebase. Operationalises maintainer openness to external contributions."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Proportion of decided (closed or merged) pull requests whose terminal state is merged."
        ),
        formula="|{p in PR: state(p) == 'merged'}| / |{p in PR: state(p) in {'merged', 'closed'}}|",
        required_data=["Pull request state and resolution outcome"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["state", "merged_at", "closed_at"],
        unit="ratio [0,1]",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Named ratio metric in Kaushik & Chahal (2025) §5.2.1.1; "
            "operationalises Linåker et al. (2026) M42 (External Openness) & M15 (Issue Turnover)."
        ),
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Literature-derived operationalisation, not an exact published equation. "
            "Denominator excludes open PRs to prevent right-censoring bias. "
            "Not applicable to projects that conduct reviews via mailing lists (e.g. Linux, Git, Apache HTTPD)."
        )
    ),
    MetricDefinition(
        metric_id="A2",
        metric_name="Pull Request Resolution Efficiency (PRE)",
        description=(
            "Mean elapsed calendar time from pull request creation until disposition (merge or closure). "
            "Reflects the operational throughput of the maintainer review process."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Arithmetic mean of days elapsed from PR creation to merge or closure across decided PRs."
        ),
        formula=(
            "sum_{p in Decided_PR} (end(p) - created_at(p)) / |Decided_PR|, "
            "where end(p) = merged_at(p) if merged else closed_at(p)"
        ),
        required_data=["Pull request creation timestamp", "Pull request merged or closed timestamp"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["created_at", "merged_at", "closed_at", "state"],
        unit="days",
        direction=MetricDirection.LOWER_IS_BETTER,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference="Alami, Pardo, Linåker (2024), Table 4, Metric TEC-2 (Efficiency).",
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Direct published formula from Alami et al. (2024). "
            "As an arithmetic mean, it is fragile on heavy-tailed pull request latency distributions "
            "(outliers skew the mean significantly above the median). Requires pairing with A3 (median)."
        )
    ),
    MetricDefinition(
        metric_id="A3",
        metric_name="Pull Request Resolution Latency (PRL Median)",
        description=(
            "Median elapsed calendar time from pull request creation until disposition (merge or closure). "
            "Provides a robust, non-parametric alternative to A2 that resists extreme single-PR outliers."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Median elapsed duration in days from creation to decision across all decided pull requests."
        ),
        formula="median({end(p) - created_at(p) : p in Decided_PR})",
        required_data=["Pull request creation timestamp", "Pull request decision timestamp"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["created_at", "merged_at", "closed_at", "state"],
        unit="days",
        direction=MetricDirection.LOWER_IS_BETTER,
        provenance_class=ProvenanceClass.PROPOSED,
        research_reference=(
            "Operationalises Linåker et al. (2026) M5 construct (General Responsiveness). "
            "Median operationalisation is a project-proposed robust counterpart to Alami et al. TEC-2."
        ),
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Project-proposed operationalisation. Robust against long-tail delays. "
            "Suppressed if bootstrap 95% confidence interval width exceeds stability threshold."
        )
    ),
    MetricDefinition(
        metric_id="A4",
        metric_name="Pull Request Backlog Ratio (PBR)",
        description=(
            "Proportion of all submitted pull requests that remain open and unresolved. "
            "Indicates potential maintainer overload when contributions accumulate unaddressed."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.PRODUCTION_PROCESS,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Ratio of currently open pull requests to total submitted pull requests observed."
        ),
        formula="|{p in PR: state(p) == 'open'}| / |PR|",
        required_data=["Count of open pull requests", "Total count of pull requests"],
        data_source="GitHub REST API",
        required_api_endpoints=[
            "/repos/{owner}/{repo}/pulls?state=all",
            "/repos/{owner}/{repo}"
        ],
        required_payload_fields=["state", "open_issues_count"],
        unit="ratio [0,1]",
        direction=MetricDirection.LOWER_IS_BETTER,
        provenance_class=ProvenanceClass.PROPOSED,
        research_reference=(
            "Adapted from Linåker et al. (2026) M14 (Issue Load construct: size and evolution of backlog). "
            "Application of backlog ratio specifically to pull requests is a project proposal."
        ),
        implementation_status=ImplementationStatus.PROVISIONAL,
        validation_notes=(
            "Marked PROVISIONAL and requiring reassessment. "
            "Severely distorted by recency truncation in paginated samples. "
            "Empirical inspection showed near-zero variance across mature active repositories, "
            "contributing minimal discrimination."
        )
    ),
    MetricDefinition(
        metric_id="A5",
        metric_name="Issue Resolution Rate (IRR)",
        description=(
            "Proportion of tracked issues that have reached closure. "
            "Measures project efficiency in addressing defect reports and feature discussions."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition="Proportion of observed issues whose state is closed.",
        formula="|{i in Issues: state(i) == 'closed'}| / |Issues|",
        required_data=["Issue state history"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/issues?state=all"],
        required_payload_fields=["state"],
        unit="ratio [0,1]",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Named ratio metric in Kaushik & Chahal (2025) §5.2.1.1; "
            "operationalises Linåker et al. (2026) M15 (Issue Turnover)."
        ),
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Literature-derived operationalisation. Subject to right-censoring "
            "(recently submitted issues have had less time to reach resolution). "
            "Undefined (NaN) for repositories that disable GitHub Issues."
        )
    ),
    MetricDefinition(
        metric_id="A6",
        metric_name="Issue Resolution Latency (IRL Median)",
        description=(
            "Median duration in days from issue creation to closure among resolved issues. "
            "Measures responsiveness and defect turnaround cadence."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition="Median duration in days from issue creation to issue closure.",
        formula="median({closed_at(i) - created_at(i) : i in Issues, state(i) == 'closed'})",
        required_data=["Issue creation timestamp", "Issue closure timestamp"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/issues?state=closed"],
        required_payload_fields=["created_at", "closed_at", "state"],
        unit="days",
        direction=MetricDirection.LOWER_IS_BETTER,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Operationalises Linåker et al. (2026) M5 (General Responsiveness: timeliness of responses) "
            "and M15 (Issue Turnover)."
        ),
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Derived operationalisation using non-parametric median. "
            "Excludes unclosed issues and sentinel values (-1). "
            "Correlates with IRR (Spearman rho ~ 0.65), requiring block aggregation to prevent signal double-counting."
        )
    ),
    MetricDefinition(
        metric_id="A7",
        metric_name="Review Throughput (RTP)",
        description=(
            "Volume of pull request events submitted within fixed recency observation windows "
            "(45, 90, and 365 days). Serves as a proxy for recent development intake volume."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Count of pull request creations occurring within w days prior to snapshot instant S."
        ),
        formula="|{p in PR: created_at(p) >= S - w days}| for w in {45, 90, 365}",
        required_data=["Pull request creation timestamps"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["created_at"],
        unit="count",
        direction=MetricDirection.CONTEXTUAL,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Derived from Linåker et al. (2026) M11 (Review Throughput: activity in code-reviews and merging PRs) "
            "combined with M10 observation windows (45, 90, 365 days)."
        ),
        implementation_status=ImplementationStatus.PROVISIONAL,
        validation_notes=(
            "Marked PROVISIONAL as a proxy requiring validation. "
            "Measures inbound PR arrivals rather than actual review actions or merged code. "
            "In capped samples, 365-day count artificially equals the total sample cap. "
            "Invalid as a raw count for cross-repository comparison without normalization."
        )
    ),
    MetricDefinition(
        metric_id="A8",
        metric_name="Development Activity Trend (DAT)",
        description=(
            "Cumulative net change in pull request submission volume across consecutive 12-week intervals. "
            "Intended to capture project velocity shifts over time."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Net change in PR volume across 12-week (84-day) intervals over repository history."
        ),
        formula=None,  # Not adopted unchanged due to telescoping-sum issue
        required_data=["Pull request creation timestamps"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["created_at"],
        unit="count",
        direction=MetricDirection.CONTEXTUAL,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference="Alami, Pardo, Linåker (2024), Table 4, Metric STA-4.",
        implementation_status=ImplementationStatus.PROVISIONAL,
        validation_notes=(
            "FORMULA NOT ADOPTED UNCHANGED due to the telescoping-sum flaw: "
            "sum_{k=1}^{n-1} (|PR_{k+1}| - |PR_k|) algebraically collapses to |PR_n| - |PR_1|, "
            "completely ignoring trajectory between start and end. "
            "Marked PROVISIONAL and superseded by A8R (relative OLS slope)."
        )
    ),
    MetricDefinition(
        metric_id="A8R",
        metric_name="Relative Development Trend (DAT Relative Slope)",
        description=(
            "Dimensionless rate of change in PR submission volume, calculated as the ordinary least squares (OLS) "
            "linear regression slope across consecutive 12-week intervals divided by mean interval volume."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition=(
            "Normalized linear trend slope of PR submissions per 12-week interval, "
            "scaled by mean interval volume to eliminate project-size confounding."
        ),
        formula="OLS_slope(k -> |PR_k|) / mean_k(|PR_k|)",
        required_data=["Pull request creation timestamps grouped into 84-day intervals"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls?state=all"],
        required_payload_fields=["created_at"],
        unit="ratio (rate per interval)",
        direction=MetricDirection.CONTEXTUAL,
        provenance_class=ProvenanceClass.PROPOSED,
        research_reference=(
            "Experimental project proposal (Amendment 1.3 in measurement design). "
            "Replaces Alami et al. STA-4 to prevent telescoping and remove repository size bias."
        ),
        implementation_status=ImplementationStatus.EXPERIMENTAL,
        validation_notes=(
            "Marked EXPERIMENTAL. Overcomes the telescoping flaw of A8 and project-size bias, "
            "but the logistic calibration scale (e.g. 0.05) lacks empirical validation from external corpora. "
            "Declining trend in mature repositories can reflect feature completion rather than distress."
        )
    ),
    MetricDefinition(
        metric_id="C1",
        metric_name="Repository Chronological Age",
        description=(
            "Total elapsed calendar time from repository creation on GitHub to snapshot assessment instant. "
            "A structural moderator used to contextualize maturity and interpret other metrics."
        ),
        chaoss_family=CHAOSSFamily.COMMON_METRICS,
        linaker_area=LinakerArea.PRODUCTION_PROCESS,
        metric_type=MetricType.CONTEXT,
        operational_definition="Elapsed duration in days from repository creation to snapshot instant.",
        formula="(S - created_at).days",
        required_data=["Repository creation timestamp"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}"],
        required_payload_fields=["created_at"],
        unit="days",
        direction=MetricDirection.NOT_APPLICABLE,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference=(
            "Alami, Pardo, Linåker (2024), Table 4, Metric STA-1; "
            "Linåker et al. (2026) p. 9 classifies life-cycle stage as a moderating trait, not a health aspect."
        ),
        implementation_status=ImplementationStatus.IMPLEMENTED,
        validation_notes=(
            "Retained strictly as a CONTEXTUAL covariate. "
            "Age is not a health score (age is not quality; older projects may be stable or obsolete). "
            "Used for stratification and baseline comparison."
        )
    ),
    MetricDefinition(
        metric_id="C2",
        metric_name="Pull Request Capture Rate",
        description=(
            "Diagnostic ratio of captured PR rows to the maximum observed PR sequence number. "
            "Identifies whether dataset truncation or GitHub API pagination limits occurred."
        ),
        chaoss_family=CHAOSSFamily.COMMON_METRICS,
        linaker_area=LinakerArea.PRODUCTION_PROCESS,
        metric_type=MetricType.DATA_QUALITY,
        operational_definition="Count of captured pull requests divided by maximum observed pull request number.",
        formula="|PR| / max({number(p) : p in PR})",
        required_data=["Sequential pull request numbers"],
        data_source="Ingestion Pipeline Metadata",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls"],
        required_payload_fields=["number"],
        unit="ratio [0,1]",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.PROPOSED,
        research_reference="Project-proposed ingestion diagnostic for API pagination boundaries.",
        implementation_status=ImplementationStatus.PROVISIONAL,
        validation_notes=(
            "Classified strictly as a DATA QUALITY variable, not a health metric. "
            "Crucial for suppressing A4, A7, and A8 when capture rate is low (<5%), "
            "preventing truncated samples from being misread as project health signals."
        )
    ),
    MetricDefinition(
        metric_id="X1",
        metric_name="Repository External Popularity (Stars + Forks)",
        description=(
            "Composite visibility and adoption signal based on total stargazers and forks. "
            "Reflects external community awareness and potential downstream adoption."
        ),
        chaoss_family=CHAOSSFamily.VALUE,
        linaker_area=LinakerArea.COMMUNITY_STABILITY,
        metric_type=MetricType.CONTEXT,
        operational_definition="Sum of repository stargazers and fork counts at snapshot instant.",
        formula="stargazers_count + forks_count",
        required_data=["Stargazers count", "Forks count"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}"],
        required_payload_fields=["stargazers_count", "forks_count"],
        unit="count",
        direction=MetricDirection.CONTEXTUAL,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Modified from Alami et al. (2024) Table 4, POP-1 (|F| + |S| + |W|); "
            "Linåker et al. (2026) M9 & M20 (Project Popularity)."
        ),
        implementation_status=ImplementationStatus.IMPLEMENTED,
        validation_notes=(
            "Retained as an ADOPTION / CONTEXTUAL variable only. "
            "Excluded from RHI scoring because raw popularity is a snapshot co-signal and confounder, "
            "not a direct indicator of maintainability or operational health. "
            "S2 POP-1 includes Watchers; this formulation drops watchers when unavailable."
        )
    ),
    MetricDefinition(
        metric_id="M45-LICENSE",
        metric_name="Declared Software License",
        description=(
            "Detection of an approved open source software license in the repository. "
            "A legal precondition for software adoption that can act as an adoption veto."
        ),
        chaoss_family=CHAOSSFamily.RISK,
        linaker_area=LinakerArea.ORCHESTRATION,
        metric_type=MetricType.HEALTH,
        operational_definition="SPDX license identifier detected in repository root.",
        formula="license != null and license.spdx_id != 'NOASSERTION'",
        required_data=["Repository license metadata"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}"],
        required_payload_fields=["license"],
        unit="boolean / string",
        direction=MetricDirection.CONTEXTUAL,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference="Linåker et al. (2026) M45 (License Type); CHAOSS Risk Working Group (License Risk).",
        implementation_status=ImplementationStatus.IMPLEMENTED,
        validation_notes=(
            "Direct metadata check. An unlicensed repository presents an absolute adoption barrier "
            "regardless of technical health score."
        )
    ),
    MetricDefinition(
        metric_id="M67-DOCS",
        metric_name="Technical Documentation Presence",
        description=(
            "Presence of foundational repository onboarding documentation (e.g. README, CONTRIBUTING). "
            "Primary determinant of developer adoption cost."
        ),
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.PRODUCTION_OUTPUT,
        metric_type=MetricType.HEALTH,
        operational_definition="Presence and non-empty byte length of README file in root directory.",
        formula="readme_bytes > 0",
        required_data=["Repository documentation file presence"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/readme"],
        required_payload_fields=["name", "size"],
        unit="boolean",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.DERIVED,
        research_reference=(
            "Linåker et al. (2026) M67 (Tech Docs: technical documentation of deliverables); "
            "CHAOSS Evolution / Community Onboarding."
        ),
        implementation_status=ImplementationStatus.PLANNED,
        validation_notes=(
            "Derived check. Basic presence test; future extensions will evaluate documentation completeness."
        )
    )
]


class MetricRegistryService:
    """
    Service managing the metric registry.
    Provides querying, filtering, schema extraction, and extensible metric registration.
    """

    def __init__(self, initial_metrics: Optional[List[MetricDefinition]] = None):
        self._registry: Dict[str, MetricDefinition] = {}
        for m in (initial_metrics or INITIAL_METRIC_DEFINITIONS):
            self.register_metric(m)

    def register_metric(self, metric: MetricDefinition) -> None:
        """
        Registers or updates a metric definition in the registry.
        Extensible: permits adding additional verified metrics dynamically.
        """
        self._registry[metric.metric_id] = metric

    def unregister_metric(self, metric_id: str) -> bool:
        """Removes a metric from the registry. Returns True if removed."""
        if metric_id in self._registry:
            del self._registry[metric_id]
            return True
        return False

    def reset_to_defaults(self) -> None:
        """Resets the registry to initial default metrics."""
        self._registry.clear()
        for m in INITIAL_METRIC_DEFINITIONS:
            self._registry[m.metric_id] = m

    def get_all_metrics(self) -> List[MetricDefinition]:
        """Returns all registered metrics in canonical order."""
        return list(self._registry.values())

    def get_metric_by_id(self, metric_id: str) -> Optional[MetricDefinition]:
        """Retrieves a single metric definition by case-insensitive ID."""
        cleaned_id = metric_id.strip()
        for mid, m in self._registry.items():
            if mid.lower() == cleaned_id.lower():
                return m
        return None

    def filter_by_chaoss_family(self, family: Union[CHAOSSFamily, str]) -> List[MetricDefinition]:
        """Filters metrics by primary CHAOSS Working Group Family."""
        target_val = family.value if isinstance(family, CHAOSSFamily) else str(family).strip()
        return [
            m for m in self._registry.values()
            if m.chaoss_family.lower() == target_val.lower()
        ]

    def filter_by_linaker_area(self, area: Union[LinakerArea, str]) -> List[MetricDefinition]:
        """Filters metrics by secondary Linåker et al. (2026) 5 Health Areas."""
        target_val = area.value if isinstance(area, LinakerArea) else str(area).strip()
        return [
            m for m in self._registry.values()
            if m.linaker_area.lower() == target_val.lower()
        ]

    def filter_by_metric_type(self, metric_type: Union[MetricType, str]) -> List[MetricDefinition]:
        """Filters metrics by functional role: health, context, data_quality, or derived."""
        target_val = metric_type.value if isinstance(metric_type, MetricType) else str(metric_type).strip()
        return [
            m for m in self._registry.values()
            if m.metric_type.lower() == target_val.lower()
        ]

    def get_required_data_fields(self, metric_id: str) -> List[str]:
        """Returns the list of required payload fields for a specific metric."""
        metric = self.get_metric_by_id(metric_id)
        if not metric:
            return []
        return list(metric.required_payload_fields)


# Global singleton instance
metric_registry_service = MetricRegistryService()

