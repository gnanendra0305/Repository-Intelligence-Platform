"""
Unit and integration tests for M0.4: Repository Survival Analysis.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.survival import SurvivalObservation
from backend.app.schemas.repository import RepositoryInfo
from backend.app.services.survival_service import survival_service

client = TestClient(app)


def test_kaplan_meier_estimation():
    """Verify non-parametric Kaplan-Meier survival curve fitting and Greenwood SE."""
    observations = [
        SurvivalObservation(subject_id="r1", duration=100.0, event=1),
        SurvivalObservation(subject_id="r2", duration=200.0, event=1),
        SurvivalObservation(subject_id="r3", duration=300.0, event=0),  # censored
        SurvivalObservation(subject_id="r4", duration=400.0, event=1),
        SurvivalObservation(subject_id="r5", duration=500.0, event=0),  # censored
        SurvivalObservation(subject_id="r6", duration=600.0, event=1),
    ]

    res = survival_service.fit_kaplan_meier(observations)

    assert res.sample_size == 6
    assert res.event_count == 4
    assert res.censored_count == 2
    assert len(res.survival_table) > 0

    # Baseline time 0 must have S(0) = 1.0
    assert res.survival_table[0].timeline == 0.0
    assert res.survival_table[0].survival_probability == 1.0

    # Curve must be monotonically decreasing
    probs = [pt.survival_probability for pt in res.survival_table]
    for i in range(1, len(probs)):
        assert probs[i] <= probs[i - 1], f"Survival probabilities must be non-increasing: {probs}"

    # Median survival time should be observed
    assert res.median_survival_time is not None
    assert res.median_survival_time > 0


def test_cox_proportional_hazards():
    """Verify Cox Proportional Hazards regression and hazard ratios."""
    # Cohort with 30 observations and clear hazard separation
    cohort = survival_service.generate_synthetic_benchmark_cohort(sample_size=40, seed=123)
    res = survival_service.fit_cox_ph(cohort)

    assert res is not None
    assert res.is_fitted is True
    assert len(res.covariates) > 0
    assert res.concordance_index is not None
    assert 0.0 <= res.concordance_index <= 1.0

    # Verify covariate fields
    cov_names = [c.name for c in res.covariates]
    assert "stars" in cov_names
    assert "prar" in cov_names

    for c in res.covariates:
        assert c.hazard_ratio > 0.0
        assert c.std_err >= 0.0


def test_single_repository_survival_assessment():
    """Verify single repository assessment correctly diagnoses right-censoring."""
    repo_meta = {
        "full_name": "sample-org/active-project",
        "created_at": "2020-01-01T00:00:00Z",
        "is_archived": False,
    }

    diag = survival_service.assess_single_repository(repo_meta)

    assert diag.repository_name == "sample-org/active-project"
    assert diag.is_censored is True
    assert diag.censoring_status == "right_censored"
    assert diag.is_archived is False
    assert diag.eligible_for_standalone_km is False
    assert diag.observed_lifespan_days > 1000
    assert len(diag.methodological_caveats) >= 3


def test_api_survival_benchmark_endpoint():
    """Test GET /api/survival/benchmark API endpoint."""
    resp = client.get("/api/survival/benchmark")
    assert resp.status_code == 200
    body = resp.json()
    assert body["dataset_type"] == "synthetic_benchmark"
    assert body["sample_size"] == 150
    assert body["kaplan_meier"]["median_survival_time"] is not None
    assert body["cox_regression"]["is_fitted"] is True


def test_api_survival_estimate_endpoint():
    """Test POST /api/survival/estimate API endpoint."""
    payload = {
        "observations": [
            {"subject_id": f"repo_{i}", "duration": float(100 * (i + 1)), "event": i % 2, "covariates": {"x": float(i)}}
            for i in range(12)
        ],
        "include_cox": True,
    }
    resp = client.post("/api/survival/estimate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["sample_size"] == 12
    assert body["event_count"] == 6
    assert body["censored_count"] == 6


@pytest.mark.asyncio
async def test_api_survival_repository_endpoint():
    """Test GET /api/survival/repository with mocked GitHub metadata."""
    mock_info = RepositoryInfo(
        name="test-repo",
        full_name="test-owner/test-repo",
        description="Test repo",
        stars=100,
        forks=20,
        language="Python",
        created_at="2022-01-01T00:00:00Z",
        last_updated_at="2024-01-01T00:00:00Z",
        open_issues_count=5,
        default_branch="main",
        is_archived=False,
        owner="test-owner",
        html_url="https://github.com/test-owner/test-repo",
        fetched_at="2024-01-01T00:00:00Z",
    )

    with patch("backend.app.main.github_service.fetch_repository", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = (mock_info, {})
        resp = client.get("/api/survival/repository?url=test-owner/test-repo")
        assert resp.status_code == 200
        body = resp.json()
        assert body["repository_name"] == "test-owner/test-repo"
        assert body["is_censored"] is True
        assert body["censoring_status"] == "right_censored"
        assert body["eligible_for_standalone_km"] is False

