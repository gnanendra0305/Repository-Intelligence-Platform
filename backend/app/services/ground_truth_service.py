"""
Ground-Truth Repository Labelling Service
Module: M1.4 – Ground-Truth Labels

Implements reproducible ground-truth repository labelling:
1. Dormancy at t + 12 months (zero commits, PR merges, closed issues in 365-day follow-up).
2. GitHub archived status (administrative metadata, separate from operational dormancy).
3. Apache / Eclipse known-group validation benchmark (graduated vs. retired).
4. Handles right-censoring, missing observations, and confidence scoring.
"""

import datetime
from typing import Dict, Any, Optional, List
from ..schemas.ground_truth import (
    DormancyStatus,
    AbandonmentStatus,
    FoundationGraduationStatus,
    RepositoryGroundTruthRecord,
)


# Verified historical known-group records for Apache Incubator projects
# Sources: Apache Software Foundation Incubator & Apache Attic official public archives
VERIFIED_FOUNDATION_KNOWN_GROUPS: Dict[str, FoundationGraduationStatus] = {
    # Graduated projects (Top-Level Projects)
    "apache/spark": FoundationGraduationStatus.GRADUATED,
    "apache/kafka": FoundationGraduationStatus.GRADUATED,
    "apache/arrow": FoundationGraduationStatus.GRADUATED,
    "apache/airflow": FoundationGraduationStatus.GRADUATED,
    "apache/flink": FoundationGraduationStatus.GRADUATED,
    "apache/dubbo": FoundationGraduationStatus.GRADUATED,
    "apache/druid": FoundationGraduationStatus.GRADUATED,
    
    # Retired / Terminated projects (Retired to Apache Attic or closed in Incubator)
    "apache/wave": FoundationGraduationStatus.RETIRED,
    "apache/climate": FoundationGraduationStatus.RETIRED,
    "apache/sirona": FoundationGraduationStatus.RETIRED,
    "apache/corinthia": FoundationGraduationStatus.RETIRED,
    "apache/blur": FoundationGraduationStatus.RETIRED,
    "apache/vxquery": FoundationGraduationStatus.RETIRED,
    "apache/hama": FoundationGraduationStatus.RETIRED,
}


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
    """Parses ISO timestamp string to UTC timezone-aware datetime."""
    if not dt_str:
        return None
    try:
        # Standardize Z to +00:00
        clean_str = dt_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


class GroundTruthLabellingService:
    """Service to evaluate and assign auditable ground-truth labels."""

    def label_repository(
        self,
        repository_data: Dict[str, Any],
        observation_date_t: str,
        evaluation_date: Optional[str] = None,
        manual_foundation_status: Optional[FoundationGraduationStatus] = None,
    ) -> RepositoryGroundTruthRecord:
        """
        Assigns reproducible ground-truth labels for a repository.

        Args:
            repository_data: Mined repository dictionary containing 'repository',
                             'commits', 'pull_requests', and 'issues'.
            observation_date_t: Baseline observation ISO timestamp t.
            evaluation_date: Optional evaluation timestamp (defaults to current UTC).
            manual_foundation_status: Optional explicit foundation known-group status.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        t_dt = parse_iso_datetime(observation_date_t)
        if not t_dt:
            raise ValueError(f"Invalid observation date t: {observation_date_t}")

        eval_dt = parse_iso_datetime(evaluation_date) or now
        t_plus_12 = t_dt + datetime.timedelta(days=365)
        t_plus_12_iso = t_plus_12.isoformat()

        repo_meta = repository_data.get("repository", {})
        repo_name = repo_meta.get("full_name") or repo_meta.get("name") or "unknown/repository"
        is_archived = bool(repo_meta.get("is_archived") or repo_meta.get("archived", False))

        evidence_sources = ["GitHub REST API repository metadata"]
        evidence_metrics: Dict[str, Any] = {}

        # Check follow-up window duration
        elapsed_days = (eval_dt - t_dt).total_seconds() / 86400.0
        evidence_metrics["elapsed_followup_days"] = round(elapsed_days, 1)

        # 1. Handle Right-Censoring: If less than 365 days elapsed since t
        if elapsed_days < 365.0:
            return RepositoryGroundTruthRecord(
                repository_name=repo_name,
                observation_date_t=observation_date_t,
                followup_date_t_plus_12=t_plus_12_iso,
                is_archived=is_archived,
                dormancy_status=DormancyStatus.CENSORED_INSUFFICIENT_FOLLOWUP,
                abandonment_status=AbandonmentStatus.CENSORED_INSUFFICIENT_FOLLOWUP,
                foundation_status=self._determine_foundation_status(repo_name, manual_foundation_status),
                confidence=0.50,
                evidence_sources=evidence_sources,
                evidence_metrics=evidence_metrics,
                censoring_reason=(
                    f"Only {elapsed_days:.1f} days elapsed since observation date t (365 days required). "
                    "Record is right-censored; 12-month dormancy cannot be determined."
                ),
                labelled_at=now.isoformat(),
            )

        # 2. Filter events occurring within the 365-day follow-up window [t, t + 365d]
        commits = repository_data.get("commits", [])
        prs = repository_data.get("pull_requests", [])
        issues = repository_data.get("issues", [])

        commits_in_window = self._count_commits_in_window(commits, t_dt, t_plus_12)
        prs_merged_in_window = self._count_prs_merged_in_window(prs, t_dt, t_plus_12)
        issues_closed_in_window = self._count_issues_closed_in_window(issues, t_dt, t_plus_12)
        open_issues_at_end = self._count_open_issues_unresolved(issues, t_plus_12)

        evidence_metrics.update({
            "commits_in_window": commits_in_window,
            "prs_merged_in_window": prs_merged_in_window,
            "issues_closed_in_window": issues_closed_in_window,
            "open_issues_unresolved": open_issues_at_end,
        })
        evidence_sources.extend([
            "Commit history event timestamps",
            "Pull request merge timestamps",
            "Issue state change logs",
        ])

        total_maintenance_actions = (
            commits_in_window + prs_merged_in_window + issues_closed_in_window
        )

        # 3. Determine Dormancy Label
        if total_maintenance_actions == 0:
            dormancy_status = DormancyStatus.DORMANT
            
            # 4. Determine Abandonment Label (Dormant + unattended maintenance burden)
            if is_archived:
                abandonment_status = AbandonmentStatus.ABANDONED
                confidence = 0.98
            elif open_issues_at_end > 0:
                # Open issues left unaddressed during 12 months of zero activity
                abandonment_status = AbandonmentStatus.ABANDONED
                confidence = 0.90
            else:
                # No open issues and no commits; project might be feature-complete and dormant
                abandonment_status = AbandonmentStatus.AMBIGUOUS
                confidence = 0.75
        else:
            dormancy_status = DormancyStatus.ACTIVE
            abandonment_status = AbandonmentStatus.SUSTAINED
            confidence = 0.95

        foundation_status = self._determine_foundation_status(repo_name, manual_foundation_status)

        return RepositoryGroundTruthRecord(
            repository_name=repo_name,
            observation_date_t=observation_date_t,
            followup_date_t_plus_12=t_plus_12_iso,
            is_archived=is_archived,
            dormancy_status=dormancy_status,
            abandonment_status=abandonment_status,
            foundation_status=foundation_status,
            confidence=confidence,
            evidence_sources=evidence_sources,
            evidence_metrics=evidence_metrics,
            censoring_reason=None,
            labelled_at=now.isoformat(),
        )

    def _determine_foundation_status(
        self,
        repo_name: str,
        manual_status: Optional[FoundationGraduationStatus],
    ) -> FoundationGraduationStatus:
        """Determines Apache / Eclipse known-group validation label from registry or override."""
        if manual_status is not None:
            return manual_status
        clean_name = repo_name.strip().lower()
        return VERIFIED_FOUNDATION_KNOWN_GROUPS.get(
            clean_name, FoundationGraduationStatus.NOT_APPLICABLE
        )

    def _count_commits_in_window(
        self, commits: List[Dict[str, Any]], start: datetime.datetime, end: datetime.datetime
    ) -> int:
        count = 0
        for c in commits:
            dt = parse_iso_datetime(c.get("author_date") or c.get("created_at"))
            if dt and start <= dt <= end:
                count += 1
        return count

    def _count_prs_merged_in_window(
        self, prs: List[Dict[str, Any]], start: datetime.datetime, end: datetime.datetime
    ) -> int:
        count = 0
        for p in prs:
            if p.get("is_merged") or p.get("merged_at"):
                dt = parse_iso_datetime(p.get("merged_at"))
                if dt and start <= dt <= end:
                    count += 1
        return count

    def _count_issues_closed_in_window(
        self, issues: List[Dict[str, Any]], start: datetime.datetime, end: datetime.datetime
    ) -> int:
        count = 0
        for i in issues:
            if i.get("state") == "closed":
                dt = parse_iso_datetime(i.get("closed_at"))
                if dt and start <= dt <= end:
                    count += 1
        return count

    def _count_open_issues_unresolved(
        self, issues: List[Dict[str, Any]], cutoff: datetime.datetime
    ) -> int:
        count = 0
        for i in issues:
            created_dt = parse_iso_datetime(i.get("created_at"))
            closed_dt = parse_iso_datetime(i.get("closed_at"))
            if created_dt and created_dt <= cutoff:
                if not closed_dt or closed_dt > cutoff:
                    count += 1
        return count


ground_truth_service = GroundTruthLabellingService()

