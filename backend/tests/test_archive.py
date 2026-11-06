"""
Unit and integration tests for M0.2: GH Archive Historical Event Ingestion.
"""

import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.archive import (
    HistoricalEventType,
    GHArchiveIngestionRequest,
)
from backend.app.services.archive_service import archive_service

client = TestClient(app)


@pytest.fixture
def sample_jsonl_events():
    events = [
        # PushEvent
        {
            "id": "ev-101",
            "type": "PushEvent",
            "actor": {"login": "dev1"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-01-15T10:00:00Z",
            "payload": {"size": 2, "head": "sha123"},
        },
        # PullRequestEvent (opened)
        {
            "id": "ev-102",
            "type": "PullRequestEvent",
            "actor": {"login": "dev2"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-02-10T11:00:00Z",
            "payload": {"action": "opened", "pull_request": {"number": 1, "merged": False, "state": "open"}},
        },
        # PullRequestEvent (merged)
        {
            "id": "ev-103",
            "type": "PullRequestEvent",
            "actor": {"login": "lead"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-02-12T14:00:00Z",
            "payload": {"action": "closed", "pull_request": {"number": 1, "merged": True, "state": "closed"}},
        },
        # IssuesEvent
        {
            "id": "ev-104",
            "type": "IssuesEvent",
            "actor": {"login": "userA"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-03-01T09:00:00Z",
            "payload": {"action": "opened", "issue": {"number": 5, "state": "open"}},
        },
        # IssueCommentEvent
        {
            "id": "ev-105",
            "type": "IssueCommentEvent",
            "actor": {"login": "lead"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-03-02T10:00:00Z",
            "payload": {"action": "created", "comment": {"id": 999}},
        },
        # WatchEvent
        {
            "id": "ev-106",
            "type": "WatchEvent",
            "actor": {"login": "stargazer1"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-04-01T12:00:00Z",
            "payload": {"action": "started"},
        },
        # Duplicate of ev-101
        {
            "id": "ev-101",
            "type": "PushEvent",
            "actor": {"login": "dev1"},
            "repo": {"name": "test-org/history-repo"},
            "created_at": "2023-01-15T10:00:00Z",
            "payload": {"size": 2},
        },
        # Event from a different repository (should be filtered out)
        {
            "id": "ev-999",
            "type": "PushEvent",
            "actor": {"login": "other"},
            "repo": {"name": "other-org/other-repo"},
            "created_at": "2023-01-15T10:00:00Z",
            "payload": {"size": 1},
        },
    ]
    return "\n".join(json.dumps(e) for e in events)


@pytest.mark.asyncio
async def test_gh_archive_ingestion_and_normalization(sample_jsonl_events):
    """Verify event normalization, filtering, and deduplication from GH Archive JSONL."""
    req = GHArchiveIngestionRequest(
        repository_name="test-org/history-repo",
        raw_events_jsonl=sample_jsonl_events,
    )

    resp = await archive_service.ingest_events(req)

    assert resp.success is True
    assert resp.repository_name == "test-org/history-repo"
    assert resp.records_ingested == 8
    assert resp.unique_records_retained == 6
    assert resp.duplicate_records_dropped == 1

    # Verify event types processed
    types_found = {ev.type for ev in resp.events}
    assert HistoricalEventType.PUSH in types_found
    assert HistoricalEventType.PULL_REQUEST in types_found
    assert HistoricalEventType.ISSUES in types_found
    assert HistoricalEventType.ISSUE_COMMENT in types_found
    assert HistoricalEventType.WATCH in types_found

    # Verify timeline summary
    summary = resp.timeline_summary
    assert summary.total_events == 6
    assert summary.unique_actors_count >= 4
    assert summary.first_event_at == "2023-01-15T10:00:00Z"
    assert summary.last_event_at == "2023-04-01T12:00:00Z"
    assert "2023-01" in summary.monthly_activity_distribution


@pytest.mark.asyncio
async def test_date_range_filtering(sample_jsonl_events):
    """Verify date range filtering bounds event retention."""
    req = GHArchiveIngestionRequest(
        repository_name="test-org/history-repo",
        raw_events_jsonl=sample_jsonl_events,
        start_date="2023-02-01",
        end_date="2023-03-15",
    )

    resp = await archive_service.ingest_events(req)
    # Only February & March events should be included (ev-102, ev-103, ev-104, ev-105)
    assert resp.unique_records_retained == 4
    for ev in resp.events:
        assert "2023-02" in ev.created_at or "2023-03" in ev.created_at


@pytest.mark.asyncio
async def test_archive_conversion_to_mining_data_and_indicators(sample_jsonl_events):
    """Verify that GH Archive events convert directly into M0.3-compatible mining data."""
    from backend.app.services.indicator_service import indicator_service
    from backend.app.services.survival_service import survival_service

    req = GHArchiveIngestionRequest(
        repository_name="test-org/history-repo",
        raw_events_jsonl=sample_jsonl_events,
    )
    resp = await archive_service.ingest_events(req)
    mining_data = archive_service.to_mining_data(resp)

    assert mining_data.repository is not None
    assert mining_data.repository.full_name == "test-org/history-repo"
    assert len(mining_data.pull_requests) >= 1
    assert len(mining_data.issues) >= 1
    assert len(mining_data.commits) >= 1

    # Pass directly to M0.3 Indicator Service
    ind_res = indicator_service.calculate_indicators(mining_data.model_dump())
    assert ind_res.repository_name == "test-org/history-repo"
    assert "A1" in ind_res.metrics

    # Pass to M0.4 Survival Service
    surv_res = survival_service.assess_single_repository(mining_data.repository.model_dump())
    assert surv_res.repository_name == "test-org/history-repo"
    assert surv_res.observed_lifespan_days >= 0



def test_api_archive_ingest_endpoint(sample_jsonl_events):
    """Test POST /api/archive/ingest endpoint."""
    payload = {
        "repository_name": "test-org/history-repo",
        "raw_events_jsonl": sample_jsonl_events,
    }

    response = client.post("/api/archive/ingest", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["unique_records_retained"] == 6
    assert "timeline_summary" in body
    assert body["timeline_summary"]["total_events"] == 6

