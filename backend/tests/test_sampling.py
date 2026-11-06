"""
Unit tests for M1.5: Stratified Repository Sampling Pipeline Service.
"""

import datetime
from backend.app.schemas.sampling import (
    Ecosystem,
    AgeStratum,
    SizeStratum,
)
from backend.app.services.sampling_service import sampling_service


def test_sampling_inclusion_criteria():
    """Verify pre-registered inclusion/exclusion rules."""
    now = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

    # 1. Valid Python repository
    valid_py = {
        "name": "valid-py",
        "full_name": "org/valid-py",
        "fork": False,
        "license_name": "MIT",
        "language": "Python",
        "size_kb": 1200,
        "created_at": "2023-01-01T00:00:00Z",  # 2 years old
        "commits": [{"sha": "c1"}],
    }
    res_valid = sampling_service.evaluate_inclusion(valid_py, Ecosystem.PYTHON_PYPI, reference_date=now)
    assert res_valid.is_eligible is True
    assert len(res_valid.exclusion_reasons) == 0

    # 2. Fork repository (should be excluded)
    fork_repo = dict(valid_py, fork=True)
    res_fork = sampling_service.evaluate_inclusion(fork_repo, Ecosystem.PYTHON_PYPI, reference_date=now)
    assert res_fork.is_eligible is False
    assert any("fork" in r.lower() for r in res_fork.exclusion_reasons)

    # 3. Missing license (should be excluded)
    no_lic_repo = dict(valid_py, license_name=None, license=None)
    res_no_lic = sampling_service.evaluate_inclusion(no_lic_repo, Ecosystem.PYTHON_PYPI, reference_date=now)
    assert res_no_lic.is_eligible is False
    assert any("license" in r.lower() for r in res_no_lic.exclusion_reasons)

    # 4. Language mismatch (Rust file in Python ecosystem)
    rust_in_py = dict(valid_py, language="Rust")
    res_mismatch = sampling_service.evaluate_inclusion(rust_in_py, Ecosystem.PYTHON_PYPI, reference_date=now)
    assert res_mismatch.is_eligible is False
    assert any("language" in r.lower() for r in res_mismatch.exclusion_reasons)

    # 5. Under-age repository (< 365 days)
    young_repo = dict(valid_py, created_at="2024-10-01T00:00:00Z")  # ~90 days old
    res_young = sampling_service.evaluate_inclusion(young_repo, Ecosystem.PYTHON_PYPI, reference_date=now)
    assert res_young.is_eligible is False
    assert any("365-day threshold" in r.lower() for r in res_young.exclusion_reasons)


def test_strata_assignment():
    """Verify age and size stratification binning logic."""
    # Age: emerging (< 2y / 730d), established (2-5y / 730-1825d), mature (> 5y / 1825d)
    assert sampling_service.assign_age_stratum(400.0) == AgeStratum.EMERGING
    assert sampling_service.assign_age_stratum(1000.0) == AgeStratum.ESTABLISHED
    assert sampling_service.assign_age_stratum(2500.0) == AgeStratum.MATURE

    # Size: small (< 100 commits), medium (100 - 1000), large (> 1000)
    assert sampling_service.assign_size_stratum(45) == SizeStratum.SMALL
    assert sampling_service.assign_size_stratum(500) == SizeStratum.MEDIUM
    assert sampling_service.assign_size_stratum(2500) == SizeStratum.LARGE


def test_create_sampling_record():
    """Verify end-to-end SampledRepositoryRecord creation."""
    mined_data = {
        "repository": {
            "name": "fast-tool",
            "full_name": "rust-org/fast-tool",
            "fork": False,
            "license_name": "Apache-2.0",
            "language": "Rust",
            "size_kb": 3500,
            "created_at": "2021-01-01T00:00:00Z",
            "is_archived": False,
        },
        "commits": [{"sha": f"c{i}"} for i in range(150)],
        "pull_requests": [{"id": 1}],
        "issues": [{"id": 10}],
    }

    record = sampling_service.create_sampling_record(
        mined_data=mined_data,
        ecosystem=Ecosystem.RUST_CRATES,
        sampling_date="2025-01-01T00:00:00Z",
    )

    assert record.repository_name == "rust-org/fast-tool"
    assert record.ecosystem == Ecosystem.RUST_CRATES
    assert record.age_stratum == AgeStratum.ESTABLISHED  # ~4 years old
    assert record.size_stratum == SizeStratum.MEDIUM    # 150 commits
    assert record.inclusion_result.is_eligible is True
    assert record.is_active_at_sampling is True
    assert record.label_availability["has_12m_followup_potential"] is True


def test_cohort_summary_and_survivorship_bias_mitigation():
    """Verify cohort summary calculates distributions and verifies inactive/dead inclusion."""
    cohort = []

    # 1. Active Python repos
    for i in range(3):
        cohort.append(
            sampling_service.create_sampling_record(
                mined_data={
                    "repository": {
                        "name": f"py-{i}", "full_name": f"org/py-{i}",
                        "license_name": "MIT", "language": "Python",
                        "created_at": "2020-01-01T00:00:00Z", "is_archived": False,
                    },
                    "commits": [{"sha": "c1"}] * 50,
                },
                ecosystem=Ecosystem.PYTHON_PYPI,
                sampling_date="2025-01-01T00:00:00Z",
            )
        )

    # 2. Inactive/Archived JS repo (to mitigate survivorship bias)
    cohort.append(
        sampling_service.create_sampling_record(
            mined_data={
                "repository": {
                    "name": "js-dead", "full_name": "org/js-dead",
                    "license_name": "MIT", "language": "JavaScript",
                    "created_at": "2019-01-01T00:00:00Z", "is_archived": True,
                },
                "commits": [{"sha": "c1"}] * 300,
            },
            ecosystem=Ecosystem.JAVASCRIPT_NPM,
            sampling_date="2025-01-01T00:00:00Z",
        )
    )

    # 3. Mature Rust repo
    cohort.append(
        sampling_service.create_sampling_record(
            mined_data={
                "repository": {
                    "name": "rust-mat", "full_name": "org/rust-mat",
                    "license_name": "MIT", "language": "Rust",
                    "created_at": "2017-01-01T00:00:00Z", "is_archived": False,
                },
                "commits": [{"sha": "c1"}] * 1500,
            },
            ecosystem=Ecosystem.RUST_CRATES,
            sampling_date="2025-01-01T00:00:00Z",
        )
    )

    summary = sampling_service.summarize_cohort(cohort)
    assert summary.total_sampled == 5
    assert summary.inactive_or_dead_count == 1
    assert summary.inactive_proportion == 0.20
    assert summary.ecosystem_breakdown[Ecosystem.PYTHON_PYPI.value] == 3
    assert summary.ecosystem_breakdown[Ecosystem.JAVASCRIPT_NPM.value] == 1
    assert summary.ecosystem_breakdown[Ecosystem.RUST_CRATES.value] == 1

