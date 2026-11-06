"""
Unit tests for M1.4: Ground-Truth Repository Labelling Service.
"""

from backend.app.schemas.ground_truth import (
    DormancyStatus,
    AbandonmentStatus,
    FoundationGraduationStatus,
)
from backend.app.services.ground_truth_service import (
    ground_truth_service,
    VERIFIED_FOUNDATION_KNOWN_GROUPS,
)


def test_ground_truth_right_censoring():
    """Verify right-censoring when follow-up window is less than 365 days."""
    repo_data = {
        "repository": {"name": "recent-repo", "full_name": "org/recent-repo", "is_archived": False},
        "commits": [],
        "pull_requests": [],
        "issues": [],
    }

    # Observation date t is only 100 days before evaluation
    record = ground_truth_service.label_repository(
        repository_data=repo_data,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2024-04-10T00:00:00Z",  # 100 days elapsed
    )

    assert record.dormancy_status == DormancyStatus.CENSORED_INSUFFICIENT_FOLLOWUP
    assert record.abandonment_status == AbandonmentStatus.CENSORED_INSUFFICIENT_FOLLOWUP
    assert record.confidence == 0.50
    assert record.censoring_reason is not None
    assert "right-censored" in record.censoring_reason


def test_ground_truth_active_maintenance():
    """Verify active status when commits/merges occur during follow-up window."""
    repo_data = {
        "repository": {"name": "active-repo", "full_name": "org/active-repo", "is_archived": False},
        "commits": [
            {"sha": "c1", "author_date": "2024-06-01T12:00:00Z"},  # Inside [2024-01-01, 2025-01-01]
        ],
        "pull_requests": [
            {"id": 1, "is_merged": True, "merged_at": "2024-07-01T12:00:00Z"},
        ],
        "issues": [],
    }

    record = ground_truth_service.label_repository(
        repository_data=repo_data,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2025-01-15T00:00:00Z",  # > 365 days
    )

    assert record.dormancy_status == DormancyStatus.ACTIVE
    assert record.abandonment_status == AbandonmentStatus.SUSTAINED
    assert record.confidence >= 0.90
    assert record.evidence_metrics["commits_in_window"] == 1
    assert record.evidence_metrics["prs_merged_in_window"] == 1


def test_ground_truth_dormancy_and_abandonment():
    """Verify dormant & abandoned status when zero maintenance occurs and backlog is neglected."""
    repo_data = {
        "repository": {"name": "dead-repo", "full_name": "org/dead-repo", "is_archived": False},
        "commits": [
            {"sha": "c0", "author_date": "2023-01-01T00:00:00Z"},  # Before observation date t
        ],
        "pull_requests": [],
        "issues": [
            # Open unresolved issue during window
            {"id": 10, "state": "open", "created_at": "2024-03-01T00:00:00Z", "closed_at": None},
        ],
    }

    record = ground_truth_service.label_repository(
        repository_data=repo_data,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2025-01-05T00:00:00Z",
    )

    assert record.dormancy_status == DormancyStatus.DORMANT
    assert record.abandonment_status == AbandonmentStatus.ABANDONED
    assert record.is_archived is False  # Explicitly kept separate from archiving
    assert record.confidence >= 0.85
    assert record.evidence_metrics["commits_in_window"] == 0
    assert record.evidence_metrics["open_issues_unresolved"] == 1


def test_ground_truth_archived_separation():
    """Verify archived status is recorded strictly from metadata without conflating dormancy."""
    repo_data = {
        "repository": {"name": "archived-repo", "full_name": "org/archived-repo", "is_archived": True},
        "commits": [],
        "pull_requests": [],
        "issues": [],
    }

    record = ground_truth_service.label_repository(
        repository_data=repo_data,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2025-01-10T00:00:00Z",
    )

    assert record.is_archived is True
    assert record.dormancy_status == DormancyStatus.DORMANT
    assert record.abandonment_status == AbandonmentStatus.ABANDONED


def test_ground_truth_known_group_classifications():
    """Verify Apache known-group benchmarks (Spark -> Graduated, Wave -> Retired)."""
    # 1. Graduated project
    repo_spark = {
        "repository": {"name": "spark", "full_name": "apache/spark"},
        "commits": [],
        "pull_requests": [],
        "issues": [],
    }
    rec_spark = ground_truth_service.label_repository(
        repository_data=repo_spark,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2024-06-01T00:00:00Z",
    )
    assert rec_spark.foundation_status == FoundationGraduationStatus.GRADUATED

    # 2. Retired project
    repo_wave = {
        "repository": {"name": "wave", "full_name": "apache/wave"},
        "commits": [],
        "pull_requests": [],
        "issues": [],
    }
    rec_wave = ground_truth_service.label_repository(
        repository_data=repo_wave,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2024-06-01T00:00:00Z",
    )
    assert rec_wave.foundation_status == FoundationGraduationStatus.RETIRED

    # 3. Unaffiliated project
    repo_generic = {
        "repository": {"name": "generic", "full_name": "user/generic"},
        "commits": [],
        "pull_requests": [],
        "issues": [],
    }
    rec_gen = ground_truth_service.label_repository(
        repository_data=repo_generic,
        observation_date_t="2024-01-01T00:00:00Z",
        evaluation_date="2024-06-01T00:00:00Z",
    )
    assert rec_gen.foundation_status == FoundationGraduationStatus.NOT_APPLICABLE

