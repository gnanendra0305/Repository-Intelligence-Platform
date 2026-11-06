"""
Unit tests for M1.2: Construct Mapping and Aspect Coverage Validation.
"""

from backend.app.services.construct_service import (
    construct_service,
    LINAKER_21_ASPECTS,
)


def test_twenty_one_aspects_inventory():
    """Verify that all 21 qualitative health aspects from Linåker et al. (2026) are present."""
    assert len(LINAKER_21_ASPECTS) == 21
    
    # Verify that all 5 Linåker areas are represented
    areas = {info["area"] for info in LINAKER_21_ASPECTS.values()}
    assert len(areas) == 5

    # Check representative aspects
    assert "responsiveness" in LINAKER_21_ASPECTS
    assert "external_visibility" in LINAKER_21_ASPECTS
    assert "knowledge_concentration" in LINAKER_21_ASPECTS
    assert "licenses" in LINAKER_21_ASPECTS
    assert "documentation" in LINAKER_21_ASPECTS


def test_aspect_coverage_validation():
    """Verify programmatic aspect coverage evaluation against M0.1 Metric Registry."""
    summary = construct_service.validate_aspect_coverage()

    assert summary.total_aspects == 21
    assert summary.covered_aspects_count > 0
    assert 0.0 < summary.coverage_ratio <= 1.0

    # Verify coverage across all 21 aspect items
    assert len(summary.aspects) == 21

    # Verify that responsiveness, licenses, and documentation are covered
    covered_keys = {item.aspect_key for item in summary.aspects if item.status == "covered"}
    assert "responsiveness" in covered_keys
    assert "licenses" in covered_keys
    assert "documentation" in covered_keys
    assert "openness" in covered_keys

    # Check area breakdown
    assert len(summary.area_coverage) == 5
    for area_name, stats in summary.area_coverage.items():
        assert stats["total"] > 0
        assert stats["covered"] >= 0

