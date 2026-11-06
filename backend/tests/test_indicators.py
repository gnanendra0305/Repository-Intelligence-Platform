"""
Unit and integration tests for M0.3: Composite Indicators & Repository Health Index.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.indicator_service import indicator_service
from backend.app.schemas.mining import RepositoryMiningData, PullRequestRecord, IssueRecord, CommitRecord, ContributorRecord

client = TestClient(app)


@pytest.fixture
def sample_mined_data():
    return {
        "repository": {
            "name": "sample-repo",
            "full_name": "test-org/sample-repo",
            "stars": 1500,
            "forks": 320,
            "created_at": "2023-01-01T00:00:00Z",
            "license_name": "MIT",
            "description": "A well-documented sample open-source project.",
            "size_kb": 4500,
        },
        "pull_requests": [
            {
                "id": 1,
                "number": 10,
                "title": "Feature 1",
                "state": "closed",
                "is_merged": True,
                "created_at": "2024-01-01T10:00:00Z",
                "closed_at": "2024-01-02T10:00:00Z",
                "merged_at": "2024-01-02T10:00:00Z",
            },
            {
                "id": 2,
                "number": 9,
                "title": "Feature 2",
                "state": "closed",
                "is_merged": True,
                "created_at": "2024-01-05T10:00:00Z",
                "closed_at": "2024-01-08T10:00:00Z",
                "merged_at": "2024-01-08T10:00:00Z",
            },
            {
                "id": 3,
                "number": 8,
                "title": "Feature 3",
                "state": "closed",
                "is_merged": False,
                "created_at": "2024-01-10T10:00:00Z",
                "closed_at": "2024-01-11T10:00:00Z",
                "merged_at": None,
            },
            {
                "id": 4,
                "number": 7,
                "title": "Feature 4",
                "state": "open",
                "is_merged": False,
                "created_at": "2024-01-15T10:00:00Z",
                "closed_at": None,
                "merged_at": None,
            },
        ],
        "issues": [
            {
                "id": 101,
                "number": 20,
                "title": "Bug report 1",
                "state": "closed",
                "created_at": "2024-01-01T00:00:00Z",
                "closed_at": "2024-01-05T00:00:00Z",
            },
            {
                "id": 102,
                "number": 21,
                "title": "Bug report 2",
                "state": "open",
                "created_at": "2024-01-10T00:00:00Z",
                "closed_at": None,
            },
        ],
        "commits": [
            {"sha": "c1", "message": "Initial commit", "author_date": "2023-01-01T00:00:00Z"}
        ],
        "contributors": [
            {"id": 1, "login": "alice", "contributions_count": 50}
        ],
    }


def test_indicator_calculation_full_data(sample_mined_data):
    """Verify calculation of metrics and RHI with complete sample mined data."""
    res = indicator_service.calculate_indicators(sample_mined_data)

    assert res.repository_name == "test-org/sample-repo"
    assert res.coverage_sufficient is True
    assert res.rhi_score is not None
    assert 0.0 <= res.rhi_score <= 100.0
    assert res.rhi_grade in ("A", "B", "C", "D", "F")

    # A1: PRAR (2 merged out of 3 decided = 66.7%)
    assert "A1" in res.metrics
    m_a1 = res.metrics["A1"]
    assert m_a1.raw_value == pytest.approx(0.6667, abs=1e-3)
    assert m_a1.normalized_score == pytest.approx(0.6667, abs=1e-3)

    # A3: PRL Median (latencies: 1.0 day, 3.0 days, 1.0 day -> median = 1.0 day)
    assert "A3" in res.metrics
    m_a3 = res.metrics["A3"]
    assert m_a3.raw_value == pytest.approx(1.0, abs=0.1)
    assert m_a3.normalized_score is not None and m_a3.normalized_score > 0.6

    # A4: PBR (1 open out of 4 total = 25% -> normalized = 75%)
    assert "A4" in res.metrics
    m_a4 = res.metrics["A4"]
    assert m_a4.raw_value == pytest.approx(0.25, abs=1e-3)
    assert m_a4.normalized_score == pytest.approx(0.75, abs=1e-3)

    # A5: IRR (1 closed out of 2 total = 50%)
    assert "A5" in res.metrics
    m_a5 = res.metrics["A5"]
    assert m_a5.raw_value == pytest.approx(0.50, abs=1e-3)

    # A6: IRL (1 closed issue: duration 4.0 days)
    assert "A6" in res.metrics
    m_a6 = res.metrics["A6"]
    assert m_a6.raw_value == pytest.approx(4.0, abs=0.1)

    # M45-LICENSE & M67-DOCS
    assert res.metrics["M45-LICENSE"].normalized_score == 1.0
    assert res.metrics["M67-DOCS"].normalized_score == 1.0

    # Verify context variables separated from RHI
    assert "C1" in res.context_variables
    assert res.context_variables["C1"].weight == 0.0
    assert "X1" in res.context_variables
    assert res.context_variables["X1"].weight == 0.0
    assert res.context_variables["X1"].raw_value == 1820.0  # 1500 stars + 320 forks

    # Verify data quality
    assert "C2" in res.data_quality_indicators
    assert res.data_quality_indicators["C2"].weight == 0.0


def test_indicator_calculation_empty_data():
    """Verify graceful handling when no PRs or issues exist."""
    empty_data = {
        "repository": {"name": "empty-repo", "full_name": "test-org/empty-repo"},
        "pull_requests": [],
        "issues": [],
        "commits": [],
        "contributors": [],
    }
    res = indicator_service.calculate_indicators(empty_data)

    assert res.repository_name == "test-org/empty-repo"
    assert res.coverage_sufficient is False
    assert res.rhi_score is None
    assert res.rhi_grade == "Insufficient Data"
    assert "A1" in res.missing_metrics
    assert "A5" in res.missing_metrics
    assert res.metrics["A1"].status == "missing_data"


def test_api_indicators_calculate_endpoint(sample_mined_data):
    """Test POST /api/indicators/calculate API endpoint with mining_data payload."""
    resp = client.post("/api/indicators/calculate", json={"mining_data": sample_mined_data})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["repository_name"] == "test-org/sample-repo"
    assert data["coverage_sufficient"] is True
    assert "A1" in data["metrics"]
    assert "code_review_pr_efficiency" in data["dimensions"]


def test_api_indicators_missing_input():
    """Test POST /api/indicators/calculate with neither url nor mining_data."""
    resp = client.post("/api/indicators/calculate", json={})
    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error_code"] == "MISSING_DATA"

