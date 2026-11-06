"""
Tests for M0.5: Evidence-Grounded LLM Health Report Generation.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import httpx

from backend.app.main import app
from backend.app.services.indicator_service import indicator_service
from backend.app.services.survival_service import survival_service
from backend.app.schemas.survival import SingleRepoSurvivalAssessment
from backend.app.services.report_service import (
    ReportGenerationService,
    report_service,
)


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


@pytest.fixture
def sample_indicators(sample_mined_data):
    return indicator_service.calculate_indicators(sample_mined_data)


@pytest.fixture
def sample_survival(sample_mined_data):
    return survival_service.assess_single_repository(sample_mined_data)


@pytest.mark.asyncio
async def test_deterministic_report_generation(sample_indicators, sample_survival):
    """Verify that deterministic fallback creates a complete, evidence-grounded report."""
    service = ReportGenerationService()
    service.gemini_api_key = ""

    report = await service.generate_report(
        indicators=sample_indicators,
        survival=sample_survival,
    )

    assert report.repository_name == "test-org/sample-repo"
    assert report.provider == "deterministic_fallback"
    assert "test-org/sample-repo" in report.executive_summary
    assert report.health_index_summary["rhi_score"] is not None
    assert report.health_index_summary["rhi_grade"] in ("A", "B", "C", "D", "F")

    # Strengths should be populated from high-performing indicators
    assert len(report.strengths) > 0

    # Adoption recommendation should reflect computed RHI
    assert report.adoption_recommendation.verdict in ["RECOMMENDED", "RECOMMENDED_WITH_CAUTION", "NOT_RECOMMENDED"]
    assert len(report.adoption_recommendation.key_drivers) > 0

    # Survival assessment should reflect active status
    assert "active" in report.survival_sustainability_assessment.lower()
    assert len(report.methodological_limitations) > 0


@pytest.mark.asyncio
async def test_low_coverage_deterministic_report(sample_survival):
    """Verify deterministic fallback handles low coverage gracefully."""
    service = ReportGenerationService()
    service.gemini_api_key = ""

    low_cov_indicators = indicator_service.calculate_indicators({
        "repository": {"name": "sparse-repo", "full_name": "org/sparse-repo"},
        "pull_requests": [],
        "issues": [],
        "commits": [],
        "contributors": [],
    })

    report = await service.generate_report(
        indicators=low_cov_indicators,
        survival=sample_survival,
    )

    assert report.provider == "deterministic_fallback"
    assert report.health_index_summary["rhi_score"] is None
    assert any("coverage" in lim.lower() for lim in report.methodological_limitations)


@pytest.mark.asyncio
async def test_mocked_gemini_api_success(sample_indicators, sample_survival):
    """Verify that valid Gemini API response parses correctly."""
    service = ReportGenerationService()
    service.gemini_api_key = "mock-valid-key"

    gemini_json_payload = {
        "executive_summary": "Mocked Gemini summary for test repo.",
        "strengths": [
            {
                "dimension": "production_process",
                "finding": "High PR acceptance efficiency.",
                "evidence_metric": "A1 = 66.7%",
                "interpretation": "Contributions are integrated rapidly and reliably.",
            }
        ],
        "risks_and_bottlenecks": [
            {
                "dimension": "community_productivity",
                "severity": "medium",
                "finding": "Issue turnaround latency requires monitoring.",
                "evidence_metric": "A6 = 4.0 days",
                "mitigation_advice": "Assign dedicated issue triage rotational shifts.",
            }
        ],
        "survival_sustainability_assessment": "Mocked longitudinal sustainability analysis: active over 2+ years.",
        "adoption_recommendation": {
            "verdict": "RECOMMENDED",
            "summary": "Solid foundation with verified review practices.",
            "key_drivers": ["A1: 66.7%", "A2: 0.75"],
            "target_audience_notes": "Suitable for production use.",
        },
        "methodological_limitations": ["Single snapshot right-censoring applies."],
    }

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "```json\n" + json.dumps(gemini_json_payload) + "\n```"
                        }
                    ]
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_gemini_response
    mock_client.post.return_value = mock_http_response

    report = await service.generate_report(
        indicators=sample_indicators,
        survival=sample_survival,
        client=mock_client,
    )

    assert report.provider == "gemini"
    assert report.executive_summary == "Mocked Gemini summary for test repo."
    assert len(report.strengths) == 1
    assert report.strengths[0].evidence_metric == "A1 = 66.7%"
    assert report.adoption_recommendation.verdict == "RECOMMENDED"


@pytest.mark.asyncio
async def test_gemini_api_failure_triggers_fallback(sample_indicators, sample_survival):
    """Verify that when Gemini API call throws an exception, deterministic fallback is safely returned."""
    service = ReportGenerationService()
    service.gemini_api_key = "mock-key"

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.ConnectError("Network connection failed")

    report = await service.generate_report(
        indicators=sample_indicators,
        survival=sample_survival,
        client=mock_client,
    )

    assert report.provider == "deterministic_fallback"
    assert "test-org/sample-repo" in report.executive_summary


def test_api_generate_report_endpoint(sample_indicators, sample_survival):
    """Test POST /api/report/generate with precomputed payload."""
    client = TestClient(app)

    payload = {
        "indicators": sample_indicators.model_dump(),
        "survival": sample_survival.model_dump(),
    }

    response = client.post("/api/report/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    report_data = data["data"]
    assert report_data["repository_name"] == "test-org/sample-repo"
    assert "executive_summary" in report_data
    assert "adoption_recommendation" in report_data
