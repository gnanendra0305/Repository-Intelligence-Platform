"""
Unit and integration tests for M0.1: Metric Registry and CHAOSS/Linåker taxonomy.
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.metric import (
    MetricDefinition,
    CHAOSSFamily,
    LinakerArea,
    MetricType,
    ProvenanceClass,
    MetricDirection,
    ImplementationStatus,
)
from backend.app.services.metric_registry import (
    metric_registry_service,
    MetricRegistryService,
    INITIAL_METRIC_DEFINITIONS,
)

client = TestClient(app)


def test_successful_registry_loading():
    """Verify default metric registry loads with all expected canonical metrics."""
    metrics = metric_registry_service.get_all_metrics()
    assert len(metrics) >= 12, "Registry should contain all canonical prototype & foundational metrics"
    
    # Verify core IDs are present
    metric_ids = {m.metric_id for m in metrics}
    expected_ids = {"A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A8R", "C1", "C2", "X1"}
    assert expected_ids.issubset(metric_ids), f"Missing core metric IDs: {expected_ids - metric_ids}"


def test_unique_metric_ids():
    """Verify that every registered metric has a strictly unique case-insensitive identifier."""
    metrics = metric_registry_service.get_all_metrics()
    seen = set()
    for m in metrics:
        norm_id = m.metric_id.strip().lower()
        assert norm_id not in seen, f"Duplicate metric ID detected: {m.metric_id}"
        seen.add(norm_id)


def test_pydantic_schema_validation():
    """Verify Pydantic enforces required fields and valid Enum values."""
    # Valid creation
    valid_metric = MetricDefinition(
        metric_id="TEST-01",
        metric_name="Test Metric",
        description="A test metric description",
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition="Operational definition for test",
        formula="test_a / test_b",
        required_data=["Test data field"],
        data_source="Test API",
        required_api_endpoints=["/test"],
        required_payload_fields=["field_a"],
        unit="ratio",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference="Test Paper (2026)",
        implementation_status=ImplementationStatus.EXPERIMENTAL,
    )
    assert valid_metric.metric_id == "TEST-01"

    # Missing required field (e.g. chaoss_family)
    with pytest.raises(ValidationError):
        MetricDefinition(
            metric_id="TEST-INVALID",
            metric_name="Invalid Metric",
            description="Missing fields",
            # chaoss_family missing
            linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
            metric_type=MetricType.HEALTH,
            operational_definition="Desc",
            data_source="API",
            provenance_class=ProvenanceClass.PROPOSED,
            research_reference="Ref",
        )

    # Invalid enum value
    with pytest.raises(ValidationError):
        MetricDefinition(
            metric_id="TEST-INVALID-ENUM",
            metric_name="Invalid Enum Metric",
            description="Invalid enum",
            chaoss_family="NotAValidCHAOSSFamily",  # Invalid
            linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
            metric_type=MetricType.HEALTH,
            operational_definition="Desc",
            data_source="API",
            provenance_class=ProvenanceClass.PROPOSED,
            research_reference="Ref",
        )


def test_metric_lookup_by_id():
    """Verify retrieval by metric ID, case-insensitivity, and nonexistent handling."""
    # Exact case
    m_a1 = metric_registry_service.get_metric_by_id("A1")
    assert m_a1 is not None
    assert m_a1.metric_id == "A1"
    assert "Acceptance Rate" in m_a1.metric_name

    # Case-insensitive
    m_a1_lower = metric_registry_service.get_metric_by_id("a1")
    assert m_a1_lower is not None
    assert m_a1_lower.metric_id == "A1"

    # Nonexistent ID
    m_none = metric_registry_service.get_metric_by_id("NONEXISTENT_XYZ")
    assert m_none is None


def test_chaoss_family_filtering():
    """Verify filtering by Linux Foundation CHAOSS Metric Families."""
    # Filter by Enum
    evolution_metrics = metric_registry_service.filter_by_chaoss_family(CHAOSSFamily.EVOLUTION)
    assert len(evolution_metrics) > 0
    assert all(m.chaoss_family == CHAOSSFamily.EVOLUTION.value for m in evolution_metrics)
    evo_ids = {m.metric_id for m in evolution_metrics}
    assert "A1" in evo_ids
    assert "A2" in evo_ids

    # Filter by string
    common_metrics = metric_registry_service.filter_by_chaoss_family("Common Metrics")
    assert len(common_metrics) > 0
    assert all(m.chaoss_family == CHAOSSFamily.COMMON_METRICS.value for m in common_metrics)
    common_ids = {m.metric_id for m in common_metrics}
    assert "C1" in common_ids
    assert "C2" in common_ids

    # Value family
    value_metrics = metric_registry_service.filter_by_chaoss_family(CHAOSSFamily.VALUE)
    assert len(value_metrics) > 0
    assert any(m.metric_id == "X1" for m in value_metrics)


def test_linaker_area_filtering():
    """Verify secondary research mapping filtering by Linåker et al. (2026) 5 Areas."""
    # Community Productivity
    prod_metrics = metric_registry_service.filter_by_linaker_area(LinakerArea.COMMUNITY_PRODUCTIVITY)
    assert len(prod_metrics) > 0
    assert all(m.linaker_area == LinakerArea.COMMUNITY_PRODUCTIVITY.value for m in prod_metrics)
    prod_ids = {m.metric_id for m in prod_metrics}
    assert "A1" in prod_ids
    assert "A2" in prod_ids
    assert "A3" in prod_ids

    # Production Process
    process_metrics = metric_registry_service.filter_by_linaker_area(LinakerArea.PRODUCTION_PROCESS)
    assert len(process_metrics) > 0
    assert any(m.metric_id == "C1" for m in process_metrics)
    assert any(m.metric_id == "A4" for m in process_metrics)


def test_metric_type_filtering():
    """Verify filtering by metric type (health, context, data_quality, derived)."""
    # Health metrics
    health_metrics = metric_registry_service.filter_by_metric_type(MetricType.HEALTH)
    assert len(health_metrics) > 0
    assert all(m.metric_type == MetricType.HEALTH.value for m in health_metrics)
    health_ids = {m.metric_id for m in health_metrics}
    assert "A1" in health_ids
    assert "A2" in health_ids

    # Context metrics
    context_metrics = metric_registry_service.filter_by_metric_type(MetricType.CONTEXT)
    assert len(context_metrics) > 0
    context_ids = {m.metric_id for m in context_metrics}
    assert "C1" in context_ids  # Repository Age
    assert "X1" in context_ids  # Popularity

    # Data quality metrics
    dq_metrics = metric_registry_service.filter_by_metric_type(MetricType.DATA_QUALITY)
    assert len(dq_metrics) > 0
    dq_ids = {m.metric_id for m in dq_metrics}
    assert "C2" in dq_ids  # Capture Rate


def test_provisional_and_experimental_formulas():
    """
    Verify handling of provisional, experimental, and undefined formulas
    according to user provenance decisions.
    """
    # A4 marked provisional
    a4 = metric_registry_service.get_metric_by_id("A4")
    assert a4 is not None
    assert a4.implementation_status == ImplementationStatus.PROVISIONAL.value
    assert a4.provenance_class == ProvenanceClass.PROPOSED.value

    # A7 marked provisional proxy
    a7 = metric_registry_service.get_metric_by_id("A7")
    assert a7 is not None
    assert a7.implementation_status == ImplementationStatus.PROVISIONAL.value

    # A8 marked provisional with undefined formula due to telescoping-sum issue
    a8 = metric_registry_service.get_metric_by_id("A8")
    assert a8 is not None
    assert a8.formula is None, "A8 formula should be None (not adopted unchanged due to telescoping-sum flaw)"
    assert a8.implementation_status == ImplementationStatus.PROVISIONAL.value
    assert "telescoping" in a8.validation_notes.lower()

    # A8R marked experimental project proposal
    a8r = metric_registry_service.get_metric_by_id("A8R")
    assert a8r is not None
    assert a8r.implementation_status == ImplementationStatus.EXPERIMENTAL.value
    assert a8r.provenance_class == ProvenanceClass.PROPOSED.value


def test_required_data_fields_retrieval():
    """Verify get_required_data_fields returns correct field lists."""
    fields_a2 = metric_registry_service.get_required_data_fields("A2")
    assert "created_at" in fields_a2
    assert "merged_at" in fields_a2
    assert "closed_at" in fields_a2
    assert "state" in fields_a2

    # Nonexistent metric returns empty list
    assert metric_registry_service.get_required_data_fields("DOES_NOT_EXIST") == []


def test_api_get_metrics_endpoint():
    """Verify GET /api/metrics returns full list of registered metrics."""
    res = client.get("/api/metrics")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["count"] >= 12
    assert body["total_registered"] >= 12
    assert len(body["data"]) == body["count"]
    
    # Verify shape of first item
    first = body["data"][0]
    assert "metric_id" in first
    assert "metric_name" in first
    assert "chaoss_family" in first
    assert "linaker_area" in first
    assert "provenance_class" in first


def test_api_get_metrics_with_filters():
    """Verify GET /api/metrics with query filters."""
    # Filter by CHAOSS Evolution
    res_evo = client.get("/api/metrics?chaoss_family=Evolution")
    assert res_evo.status_code == 200
    body_evo = res_evo.json()
    assert body_evo["chaoss_family_filter"] == "Evolution"
    assert all(m["chaoss_family"] == "Evolution" for m in body_evo["data"])

    # Filter by Linåker area
    res_area = client.get("/api/metrics?linaker_area=Community%20Productivity")
    assert res_area.status_code == 200
    body_area = res_area.json()
    assert body_area["linaker_area_filter"] == "Community Productivity"
    assert all(m["linaker_area"] == "Community Productivity" for m in body_area["data"])

    # Filter by metric_type
    res_ctx = client.get("/api/metrics?metric_type=context")
    assert res_ctx.status_code == 200
    body_ctx = res_ctx.json()
    assert body_ctx["metric_type_filter"] == "context"
    assert all(m["metric_type"] == "context" for m in body_ctx["data"])


def test_api_get_metric_by_id_endpoint():
    """Verify GET /api/metrics/{metric_id} retrieval and 404 handling."""
    # Valid metric
    res = client.get("/api/metrics/A1")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["metric_id"] == "A1"
    assert body["data"]["chaoss_family"] == "Evolution"

    # Nonexistent metric returns 404
    res_404 = client.get("/api/metrics/UNKNOWN_METRIC_999")
    assert res_404.status_code == 404
    body_404 = res_404.json()
    assert body_404["success"] is False
    assert body_404["error_code"] == "METRIC_NOT_FOUND"


def test_extensibility():
    """Verify that custom verified metrics can be registered and unregistered dynamically."""
    custom_metric = MetricDefinition(
        metric_id="EXT-01",
        metric_name="Code Review Comment Density",
        description="Average number of review comments per pull request.",
        chaoss_family=CHAOSSFamily.EVOLUTION,
        linaker_area=LinakerArea.COMMUNITY_PRODUCTIVITY,
        metric_type=MetricType.HEALTH,
        operational_definition="Count of review comments divided by total merged pull requests.",
        formula="total_comments / total_merged_prs",
        required_data=["PR review comments"],
        data_source="GitHub REST API",
        required_api_endpoints=["/repos/{owner}/{repo}/pulls/{pull_number}/comments"],
        required_payload_fields=["id", "body"],
        unit="comments/PR",
        direction=MetricDirection.HIGHER_IS_BETTER,
        provenance_class=ProvenanceClass.DIRECT,
        research_reference="Linåker et al. (2026) M60 (PR Checks).",
        implementation_status=ImplementationStatus.PLANNED,
    )
    metric_registry_service.register_metric(custom_metric)
    
    retrieved = metric_registry_service.get_metric_by_id("EXT-01")
    assert retrieved is not None
    assert retrieved.metric_name == "Code Review Comment Density"

    # Clean up
    removed = metric_registry_service.unregister_metric("EXT-01")
    assert removed is True
    assert metric_registry_service.get_metric_by_id("EXT-01") is None

