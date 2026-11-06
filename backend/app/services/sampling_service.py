"""
Stratified Repository Sampling Pipeline Service
Module: M1.5 – Sampling Strategy

Implements reproducible sampling across three justified OSS ecosystems:
1. Python (PyPI)
2. JavaScript / TypeScript (npm)
3. Rust (crates.io)

Stratifies by repository age and size/activity, explicitly includes
inactive/dead/archived projects to eliminate survivorship bias,
and enforces auditable inclusion/exclusion criteria.
"""

import datetime
from typing import Dict, Any, List, Optional
from ..schemas.sampling import (
    Ecosystem,
    AgeStratum,
    SizeStratum,
    InclusionCriteriaResult,
    SampledRepositoryRecord,
    StratifiedSamplingCohortSummary,
)


# Language ecosystem mapping
ECOSYSTEM_LANGUAGE_MAP: Dict[Ecosystem, List[str]] = {
    Ecosystem.PYTHON_PYPI: ["python"],
    Ecosystem.JAVASCRIPT_NPM: ["javascript", "typescript"],
    Ecosystem.RUST_CRATES: ["rust"],
}


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
    if not dt_str:
        return None
    try:
        clean_str = dt_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


class SamplingStrategyService:
    """Service to evaluate inclusion criteria, assign strata, and manage study cohorts."""

    def evaluate_inclusion(
        self,
        repo_data: Dict[str, Any],
        ecosystem: Ecosystem,
        reference_date: Optional[datetime.datetime] = None,
    ) -> InclusionCriteriaResult:
        """
        Evaluates pre-registered inclusion and exclusion criteria for a repository.

        Inclusion rules:
        1. Non-fork repository (is_fork == False).
        2. Declared open-source license (has license info).
        3. Primary programming language matches target ecosystem.
        4. Not an empty repository (commit count > 0 or size > 0).
        5. Minimum repository age of 365 days (to allow baseline assessment).
        """
        now = reference_date or datetime.datetime.now(datetime.timezone.utc)
        checks: Dict[str, bool] = {}
        exclusion_reasons: List[str] = []

        # 1. Non-fork check
        is_fork = bool(repo_data.get("fork", False) or repo_data.get("is_fork", False))
        checks["is_non_fork"] = not is_fork
        if is_fork:
            exclusion_reasons.append("Repository is a fork; non-canonical forks are excluded.")

        # 2. License check
        has_license = bool(
            repo_data.get("license")
            or repo_data.get("license_name")
            or repo_data.get("license_spdx_id")
        )
        checks["has_declared_license"] = has_license
        if not has_license:
            exclusion_reasons.append("No open-source license declared in repository metadata.")

        # 3. Ecosystem language match
        primary_lang = (repo_data.get("language") or "").strip().lower()
        allowed_langs = ECOSYSTEM_LANGUAGE_MAP.get(ecosystem, [])
        lang_matches = primary_lang in allowed_langs
        checks["language_matches_ecosystem"] = lang_matches
        if not lang_matches:
            exclusion_reasons.append(
                f"Primary language '{primary_lang}' does not match ecosystem '{ecosystem.value}'."
            )

        # 4. Not empty repository
        commits_count = len(repo_data.get("commits", []))
        size_kb = repo_data.get("size_kb") or repo_data.get("size", 0)
        is_not_empty = commits_count > 0 or size_kb > 0
        checks["is_not_empty"] = is_not_empty
        if not is_not_empty:
            exclusion_reasons.append("Repository has zero commits and zero disk size.")

        # 5. Minimum age check (>= 365 days)
        created_dt = parse_iso_datetime(repo_data.get("created_at"))
        if created_dt:
            age_days = (now - created_dt).total_seconds() / 86400.0
            is_sufficient_age = age_days >= 365.0
            checks["meets_minimum_age_365d"] = is_sufficient_age
            if not is_sufficient_age:
                exclusion_reasons.append(
                    f"Repository age ({age_days:.1f} days) is less than the 365-day threshold."
                )
        else:
            checks["meets_minimum_age_365d"] = False
            exclusion_reasons.append("Missing valid repository 'created_at' timestamp.")

        is_eligible = all(checks.values())
        return InclusionCriteriaResult(
            is_eligible=is_eligible,
            checks=checks,
            exclusion_reasons=exclusion_reasons,
        )

    def assign_age_stratum(self, age_days: float) -> AgeStratum:
        """
        Assigns age stratum:
        - Emerging: < 2 years (< 730 days)
        - Established: 2 - 5 years (730 - 1825 days)
        - Mature: > 5 years (> 1825 days)
        """
        if age_days < 730.0:
            return AgeStratum.EMERGING
        elif age_days <= 1825.0:
            return AgeStratum.ESTABLISHED
        else:
            return AgeStratum.MATURE

    def assign_size_stratum(self, commit_count: int) -> SizeStratum:
        """
        Assigns size stratum:
        - Small: < 100 commits
        - Medium: 100 - 1,000 commits
        - Large: > 1,000 commits
        """
        if commit_count < 100:
            return SizeStratum.SMALL
        elif commit_count <= 1000:
            return SizeStratum.MEDIUM
        else:
            return SizeStratum.LARGE

    def create_sampling_record(
        self,
        mined_data: Dict[str, Any],
        ecosystem: Ecosystem,
        sampling_date: Optional[str] = None,
    ) -> SampledRepositoryRecord:
        """
        Creates an auditable SampledRepositoryRecord from mined repository data.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        sample_dt = parse_iso_datetime(sampling_date) or now

        repo_meta = mined_data.get("repository", {})
        repo_name = repo_meta.get("full_name") or repo_meta.get("name") or "unknown/repo"
        is_archived = bool(repo_meta.get("is_archived") or repo_meta.get("archived", False))

        # Check inclusion
        inclusion_res = self.evaluate_inclusion(
            repo_data=repo_meta,
            ecosystem=ecosystem,
            reference_date=sample_dt,
        )

        # Calculate age
        created_dt = parse_iso_datetime(repo_meta.get("created_at")) or sample_dt
        age_days = max(0.0, (sample_dt - created_dt).total_seconds() / 86400.0)
        age_stratum = self.assign_age_stratum(age_days)

        # Calculate commit size
        commits = mined_data.get("commits", [])
        commit_count = len(commits)
        size_stratum = self.assign_size_stratum(commit_count)

        # Check activity at sampling (anti-survivorship bias check)
        is_active = not is_archived

        # Label availability
        label_availability = {
            "has_12m_followup_potential": age_days >= 365.0,
            "is_archived_label_known": True,
            "has_pr_data": len(mined_data.get("pull_requests", [])) > 0,
            "has_issue_data": len(mined_data.get("issues", [])) > 0,
        }

        return SampledRepositoryRecord(
            repository_name=repo_name,
            ecosystem=ecosystem,
            age_stratum=age_stratum,
            size_stratum=size_stratum,
            observed_age_days=round(age_days, 1),
            observed_commit_count=commit_count,
            is_active_at_sampling=is_active,
            is_archived=is_archived,
            sampling_date=sample_dt.isoformat(),
            label_availability=label_availability,
            inclusion_result=inclusion_res,
        )

    def summarize_cohort(
        self, records: List[SampledRepositoryRecord]
    ) -> StratifiedSamplingCohortSummary:
        """
        Summarizes cohort distribution across ecosystems, age strata, size strata,
        and verifies inclusion of inactive/dead repositories to mitigate survivorship bias.
        """
        total = len(records)
        ecosystem_counts: Dict[str, int] = {e.value: 0 for e in Ecosystem}
        age_counts: Dict[str, int] = {a.value: 0 for a in AgeStratum}
        size_counts: Dict[str, int] = {s.value: 0 for s in SizeStratum}

        inactive_or_dead = 0

        for r in records:
            ecosystem_counts[r.ecosystem.value] = (
                ecosystem_counts.get(r.ecosystem.value, 0) + 1
            )
            age_counts[r.age_stratum.value] = (
                age_counts.get(r.age_stratum.value, 0) + 1
            )
            size_counts[r.size_stratum.value] = (
                size_counts.get(r.size_stratum.value, 0) + 1
            )
            if not r.is_active_at_sampling or r.is_archived:
                inactive_or_dead += 1

        inactive_ratio = (inactive_or_dead / total) if total > 0 else 0.0

        # Balanced design check: all strata have representation
        all_eco_covered = all(c > 0 for c in ecosystem_counts.values()) if total >= len(Ecosystem) else False
        all_age_covered = all(c > 0 for c in age_counts.values()) if total >= len(AgeStratum) else False
        has_inactive_rep = inactive_or_dead > 0 if total >= 5 else True

        is_balanced = all_eco_covered and all_age_covered and has_inactive_rep

        return StratifiedSamplingCohortSummary(
            total_sampled=total,
            ecosystem_breakdown=ecosystem_counts,
            age_stratum_breakdown=age_counts,
            size_stratum_breakdown=size_counts,
            inactive_or_dead_count=inactive_or_dead,
            inactive_proportion=round(inactive_ratio, 4),
            is_balanced_design=is_balanced,
        )


sampling_service = SamplingStrategyService()

