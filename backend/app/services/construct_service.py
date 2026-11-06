"""
Construct Mapping and Aspect Coverage Validation Service
Module: M1.2 – Construct Mapping

Validates metric coverage across the 21 qualitative OSS health aspects
and 5 health areas defined by Linåker et al. (2026).
Reuses the existing M0.1 Metric Registry without duplicate definitions.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from .metric_registry import metric_registry_service, LinakerArea


# The 21 qualitative OSS health aspects grouped across the 5 Linåker areas
LINAKER_21_ASPECTS: Dict[str, Dict[str, Any]] = {
    # Area 1: Community Productivity
    "social_activity": {
        "name": "Social Activity",
        "area": LinakerArea.COMMUNITY_PRODUCTIVITY,
        "base_metrics": ["M1", "M2", "M3", "M4"],
        "description": "Meetup, chat, forum, and social media community presence.",
    },
    "responsiveness": {
        "name": "Responsiveness",
        "area": LinakerArea.COMMUNITY_PRODUCTIVITY,
        "base_metrics": ["M5", "M6", "M7"],
        "description": "Timeliness and agility in responding to new questions, PRs, and issues.",
    },
    "external_visibility": {
        "name": "External Visibility",
        "area": LinakerArea.COMMUNITY_PRODUCTIVITY,
        "base_metrics": ["M8", "M9"],
        "description": "Project popularity, search rankings, and inbound ecosystem attention.",
    },
    "development_activity": {
        "name": "Development Activity",
        "area": LinakerArea.COMMUNITY_PRODUCTIVITY,
        "base_metrics": ["M10", "M11", "M12", "M13"],
        "description": "Contribution volume across code, reviews, documentation, and issues.",
    },
    "development_efficiency": {
        "name": "Development Efficiency",
        "area": LinakerArea.COMMUNITY_PRODUCTIVITY,
        "base_metrics": ["M14", "M15", "M16", "M17"],
        "description": "Backlog velocity, issue turnover rate, and bug turnaround.",
    },

    # Area 2: Community Stability
    "adoption": {
        "name": "Adoption",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M18", "M19", "M20"],
        "description": "Downstream software dependencies and corporate usage footprint.",
    },
    "organizational_diversity": {
        "name": "Organizational Diversity",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M21", "M22", "M23"],
        "description": "Spread of contributors across independent corporate entities.",
    },
    "demographic_diversity": {
        "name": "Demographic Diversity",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M24", "M25"],
        "description": "Geographic dispersion and inclusive demographic participation.",
    },
    "discussion_climate": {
        "name": "Discussion Climate",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M26", "M27", "M28", "M29"],
        "description": "Tone, sentiment, mentorship, and Code of Conduct enforcement.",
    },
    "knowledge_concentration": {
        "name": "Knowledge Concentration",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M30", "M31", "M32"],
        "description": "Bus factor, component ownership, and maintainer redundancy.",
    },
    "contributor_turnover": {
        "name": "Contributor Turnover",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M33", "M34", "M35"],
        "description": "Newcomer onboarding rate, retention rate, and maintainer attrition.",
    },
    "financial_sustainability": {
        "name": "Financial Sustainability",
        "area": LinakerArea.COMMUNITY_STABILITY,
        "base_metrics": ["M36", "M37"],
        "description": "Foundation governance and independent fiscal sponsorship.",
    },

    # Area 3: Orchestration
    "governance_structure": {
        "name": "Governance Structure",
        "area": LinakerArea.ORCHESTRATION,
        "base_metrics": ["M38", "M39", "M40", "M41"],
        "description": "Decision-making transparency, maintainer election, and bylaws.",
    },
    "openness": {
        "name": "Openness",
        "area": LinakerArea.ORCHESTRATION,
        "base_metrics": ["M42", "M43", "M44"],
        "description": "Receptivity to external volunteer pull requests and public roadmaps.",
    },
    "licenses": {
        "name": "Licenses",
        "area": LinakerArea.ORCHESTRATION,
        "base_metrics": ["M45", "M46", "M47", "M48"],
        "description": "OSI open-source licensing, dual-licensing, and contributor CLAs.",
    },

    # Area 4: Production Process
    "development_process": {
        "name": "Development Process",
        "area": LinakerArea.PRODUCTION_PROCESS,
        "base_metrics": ["M49", "M50", "M51", "M52"],
        "description": "Contribution guidelines, branching models, and review requirements.",
    },
    "release_management": {
        "name": "Release Management",
        "area": LinakerArea.PRODUCTION_PROCESS,
        "base_metrics": ["M53", "M54", "M55", "M56", "M57"],
        "description": "SemVer tagging, changelogs, and release cadence consistency.",
    },
    "security_management": {
        "name": "Security Management",
        "area": LinakerArea.PRODUCTION_PROCESS,
        "base_metrics": ["M58", "M59", "M60", "M61", "M62", "M63"],
        "description": "Vulnerability disclosure policies, SAST scanning, and patch speed.",
    },
    "scaffolding": {
        "name": "Scaffolding",
        "area": LinakerArea.PRODUCTION_PROCESS,
        "base_metrics": ["M64", "M65", "M66"],
        "description": "CI/CD automated testing, test coverage, and linters.",
    },

    # Area 5: Production Output
    "documentation": {
        "name": "Documentation",
        "area": LinakerArea.PRODUCTION_OUTPUT,
        "base_metrics": ["M67", "M68", "M69"],
        "description": "README, installation guides, API reference, and sample code.",
    },
    "technical_quality": {
        "name": "Technical Quality",
        "area": LinakerArea.PRODUCTION_OUTPUT,
        "base_metrics": ["M70", "M71", "M72"],
        "description": "Code complexity, defect density, and backwards compatibility.",
    },
}

# Mapping of M0.1 metric IDs to the specific Linåker aspect key they operationalise
REGISTRY_METRIC_TO_ASPECT_MAP: Dict[str, str] = {
    "A1": "openness",
    "A2": "responsiveness",
    "A3": "responsiveness",
    "A4": "development_efficiency",
    "A5": "development_efficiency",
    "A6": "responsiveness",
    "A7": "development_efficiency",
    "A8R": "development_activity",
    "M45-LICENSE": "licenses",
    "M67-DOCS": "documentation",
    "C1": "development_activity",
    "X1": "external_visibility",
}


class AspectCoverageItem(BaseModel):
    aspect_key: str
    name: str
    area: str
    status: str  # 'covered', 'partially_covered', 'uncovered'
    operational_metrics: List[str]
    description: str


class AspectCoverageSummary(BaseModel):
    total_aspects: int = 21
    covered_aspects_count: int
    coverage_ratio: float
    aspects: List[AspectCoverageItem]
    area_coverage: Dict[str, Dict[str, int]]


class ConstructMappingService:
    """Service to validate construct coverage without duplicating registry storage."""

    def validate_aspect_coverage(self) -> AspectCoverageSummary:
        """
        Validates coverage across the 21 Linåker aspects based on currently registered metrics.
        """
        all_registered = metric_registry_service.get_all_metrics()
        registered_ids = {m.metric_id for m in all_registered}

        aspect_items: List[AspectCoverageItem] = []
        covered_count = 0
        area_stats: Dict[str, Dict[str, int]] = {}

        for key, info in LINAKER_21_ASPECTS.items():
            area_str = (
                info["area"].value
                if isinstance(info["area"], LinakerArea)
                else str(info["area"])
            )
            if area_str not in area_stats:
                area_stats[area_str] = {"total": 0, "covered": 0}
            area_stats[area_str]["total"] += 1

            # Find matching metrics
            matching_ids = [
                mid for mid, akey in REGISTRY_METRIC_TO_ASPECT_MAP.items()
                if akey == key and mid in registered_ids
            ]

            if matching_ids:
                status = "covered"
                covered_count += 1
                area_stats[area_str]["covered"] += 1
            else:
                status = "uncovered"

            aspect_items.append(
                AspectCoverageItem(
                    aspect_key=key,
                    name=info["name"],
                    area=area_str,
                    status=status,
                    operational_metrics=matching_ids,
                    description=info["description"],
                )
            )

        ratio = round(covered_count / len(LINAKER_21_ASPECTS), 4)

        return AspectCoverageSummary(
            total_aspects=len(LINAKER_21_ASPECTS),
            covered_aspects_count=covered_count,
            coverage_ratio=ratio,
            aspects=aspect_items,
            area_coverage=area_stats,
        )


construct_service = ConstructMappingService()

