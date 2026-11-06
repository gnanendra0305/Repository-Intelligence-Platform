"""
GH Archive Historical Event Ingestion Service
Module: M0.2 – GH Archive & Longitudinal Event Processing

Ingests and normalizes historical GitHub event streams from:
1. GH Archive hourly gzip JSON dumps (https://data.gharchive.org/{date}-{hour}.json.gz)
2. BigQuery public dataset exports (JSON lines format)

Processes:
- PushEvent
- PullRequestEvent
- IssuesEvent
- IssueCommentEvent
- PullRequestReviewEvent
- WatchEvent

Normalizes events, deduplicates by ID, filters by repo and date range,
and generates longitudinal timeline summaries to support M0.3 indicators
and M0.4 survival analysis without survivorship bias.
"""

import gzip
import io
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
import httpx

from ..schemas.archive import (
    HistoricalEventType,
    HistoricalEventRecord,
    HistoricalTimelineSummary,
    GHArchiveIngestionRequest,
    GHArchiveIngestionResponse,
)
from ..schemas.mining import (
    RepositoryMiningData,
    PullRequestRecord,
    IssueRecord,
    CommitRecord,
    ContributorRecord,
)
from ..schemas.repository import RepositoryInfo

logger = logging.getLogger("rip-archive")

SUPPORTED_EVENT_TYPES: Set[str] = {e.value for e in HistoricalEventType}


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
    if not dt_str:
        return None
    try:
        clean = dt_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


class GHArchiveService:
    """Service to ingest, filter, and normalize historical event streams."""

    def __init__(self):
        self.timeout = 30.0

    async def ingest_events(
        self,
        request: GHArchiveIngestionRequest,
        client: Optional[httpx.AsyncClient] = None,
    ) -> GHArchiveIngestionResponse:
        """
        Ingests events from provided JSON lines or fetches from GH Archive URLs.
        Filters by repository and date range, deduplicates by ID, and produces timeline metrics.
        """
        target_repo = request.repository_name.strip().lower()
        start_dt = parse_iso_datetime(request.start_date)
        end_dt = parse_iso_datetime(request.end_date)

        raw_records: List[Dict[str, Any]] = []
        warnings: List[str] = []

        # 1. Parse directly supplied JSONL (e.g. from BigQuery export or local file)
        if request.raw_events_jsonl:
            lines = request.raw_events_jsonl.splitlines()
            for line_idx, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    raw_records.append(obj)
                except Exception as e:
                    if len(warnings) < 5:
                        warnings.append(f"Line {line_idx+1} malformed JSON: {str(e)[:100]}")

        # 2. Fetch from hourly GH Archive URLs if specified
        if request.hourly_archive_urls:
            should_close = False
            if client is None:
                client = httpx.AsyncClient(timeout=self.timeout)
                should_close = True
            try:
                for url in request.hourly_archive_urls:
                    try:
                        fetched = await self._fetch_and_decompress(url, client)
                        raw_records.extend(fetched)
                    except Exception as fe:
                        warnings.append(f"Failed to fetch archive URL '{url}': {str(fe)}")
            finally:
                if should_close:
                    await client.aclose()

        # 3. Filter, normalize and deduplicate
        seen_ids: Set[str] = set()
        normalized_events: List[HistoricalEventRecord] = []
        duplicates_dropped = 0

        for raw in raw_records:
            # Check repository name
            repo_val = (
                raw.get("repo", {}).get("name")
                or raw.get("repository", {}).get("full_name")
                or raw.get("repository", {}).get("name")
                or ""
            ).strip().lower()

            if target_repo and repo_val != target_repo:
                continue

            # Check event type
            ev_type_str = raw.get("type", "")
            if ev_type_str not in SUPPORTED_EVENT_TYPES:
                continue

            # Check timestamp and date bounds
            created_str = raw.get("created_at", "")
            created_dt = parse_iso_datetime(created_str)
            if not created_dt:
                continue

            if start_dt and created_dt < start_dt:
                continue
            if end_dt and created_dt > end_dt:
                continue

            # Check duplicate ID
            ev_id = str(raw.get("id", f"{repo_val}_{created_str}_{ev_type_str}"))
            if ev_id in seen_ids:
                duplicates_dropped += 1
                continue
            seen_ids.add(ev_id)

            # Normalize event record
            normalized_record = self._normalize_event(raw, ev_type_str, repo_val, created_str)
            normalized_events.append(normalized_record)

        # Sort chronologically
        normalized_events.sort(key=lambda x: x.created_at)

        # 4. Generate longitudinal timeline summary
        timeline_summary = self._generate_timeline_summary(request.repository_name, normalized_events)

        return GHArchiveIngestionResponse(
            success=True,
            message="GH Archive historical events ingested and normalized successfully.",
            repository_name=request.repository_name,
            records_ingested=len(raw_records),
            unique_records_retained=len(normalized_events),
            duplicate_records_dropped=duplicates_dropped,
            timeline_summary=timeline_summary,
            events=normalized_events,
            warnings=warnings,
        )

    async def _fetch_and_decompress(self, url: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Fetches and gunzips hourly archive stream."""
        resp = await client.get(url)
        if resp.status_code == 404:
            raise RuntimeError("GH Archive hourly dump not found (HTTP 404).")
        if resp.status_code != 200:
            raise RuntimeError(f"GH Archive download returned HTTP {resp.status_code}.")

        content = resp.content
        # Check if gzipped
        if url.endswith(".gz") or content[:2] == b"\x1f\x8b":
            with gzip.GzipFile(fileobj=io.BytesIO(content)) as gz:
                decompressed = gz.read().decode("utf-8", errors="replace")
        else:
            decompressed = content.decode("utf-8", errors="replace")

        records: List[Dict[str, Any]] = []
        for line in decompressed.splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
        return records

    def _normalize_event(
        self, raw: Dict[str, Any], ev_type_str: str, repo_name: str, created_at: str
    ) -> HistoricalEventRecord:
        actor = raw.get("actor", {}).get("login") or raw.get("actor_attributes", {}).get("login") or "unknown"
        payload = raw.get("payload", {})
        action = payload.get("action")

        summary: Dict[str, Any] = {}
        if ev_type_str == "PushEvent":
            summary["commits_count"] = payload.get("size") or len(payload.get("commits", []))
            summary["head"] = payload.get("head")
        elif ev_type_str == "PullRequestEvent":
            pr = payload.get("pull_request", {})
            summary["number"] = pr.get("number") or payload.get("number")
            summary["merged"] = bool(pr.get("merged", False))
            summary["state"] = pr.get("state")
        elif ev_type_str == "IssuesEvent":
            issue = payload.get("issue", {})
            summary["number"] = issue.get("number") or payload.get("number")
            summary["state"] = issue.get("state")
        elif ev_type_str == "PullRequestReviewEvent":
            review = payload.get("review", {})
            summary["review_state"] = review.get("state")
        elif ev_type_str == "IssueCommentEvent":
            summary["comment_id"] = payload.get("comment", {}).get("id")

        return HistoricalEventRecord(
            id=str(raw.get("id")),
            type=HistoricalEventType(ev_type_str),
            repository_name=repo_name,
            actor_login=actor,
            created_at=created_at,
            action=action,
            payload_summary=summary,
        )

    def _generate_timeline_summary(
        self, repo_name: str, events: List[HistoricalEventRecord]
    ) -> HistoricalTimelineSummary:
        if not events:
            return HistoricalTimelineSummary(
                repository_name=repo_name,
                first_event_at=None,
                last_event_at=None,
                total_events=0,
                event_type_counts={e.value: 0 for e in HistoricalEventType},
                unique_actors_count=0,
                monthly_activity_distribution={},
                is_dormant_last_12m=True,
            )

        type_counts: Dict[str, int] = {e.value: 0 for e in HistoricalEventType}
        monthly_dist: Dict[str, int] = {}
        actors: Set[str] = set()

        for ev in events:
            type_counts[ev.type.value] = type_counts.get(ev.type.value, 0) + 1
            actors.add(ev.actor_login)
            dt = parse_iso_datetime(ev.created_at)
            if dt:
                month_key = dt.strftime("%Y-%m")
                monthly_dist[month_key] = monthly_dist.get(month_key, 0) + 1

        first_at = events[0].created_at
        last_at = events[-1].created_at

        # Check dormancy in last 12 months of timeline
        last_dt = parse_iso_datetime(last_at)
        cutoff_dt = last_dt - datetime.timedelta(days=365) if last_dt else None

        active_maintenance_in_last_year = False
        if cutoff_dt:
            for ev in events:
                dt = parse_iso_datetime(ev.created_at)
                if dt and dt >= cutoff_dt:
                    if ev.type in (HistoricalEventType.PUSH, HistoricalEventType.PULL_REQUEST):
                        active_maintenance_in_last_year = True
                        break

        return HistoricalTimelineSummary(
            repository_name=repo_name,
            first_event_at=first_at,
            last_event_at=last_at,
            total_events=len(events),
            event_type_counts=type_counts,
            unique_actors_count=len(actors),
            monthly_activity_distribution=monthly_dist,
            is_dormant_last_12m=not active_maintenance_in_last_year,
        )

    def to_mining_data(self, response: GHArchiveIngestionResponse) -> RepositoryMiningData:
        """
        Converts historical GH Archive events into a structured RepositoryMiningData container
        for direct compatibility with M0.3 indicators and M0.4 survival analysis.
        """
        prs: List[PullRequestRecord] = []
        issues: List[IssueRecord] = []
        commits: List[CommitRecord] = []
        actors_seen: Dict[str, int] = {}

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        repo_name = response.repository_name
        owner = repo_name.split("/")[0] if "/" in repo_name else "unknown"

        for ev in response.events:
            actors_seen[ev.actor_login] = actors_seen.get(ev.actor_login, 0) + 1

            if ev.type == HistoricalEventType.PULL_REQUEST:
                pr_num = ev.payload_summary.get("number", len(prs) + 1)
                is_merged = bool(ev.payload_summary.get("merged", False))
                state = ev.payload_summary.get("state", "closed" if is_merged else "open")
                prs.append(
                    PullRequestRecord(
                        id=pr_num,
                        number=pr_num,
                        title=f"Historical PR #{pr_num} from GH Archive",
                        state=state.lower(),
                        is_merged=is_merged,
                        created_at=ev.created_at,
                        closed_at=ev.created_at if state.lower() == "closed" or is_merged else None,
                        merged_at=ev.created_at if is_merged else None,
                        author_login=ev.actor_login,
                    )
                )
            elif ev.type == HistoricalEventType.ISSUES:
                iss_num = ev.payload_summary.get("number", len(issues) + 1)
                state = ev.payload_summary.get("state", "closed")
                issues.append(
                    IssueRecord(
                        id=iss_num,
                        number=iss_num,
                        title=f"Historical Issue #{iss_num} from GH Archive",
                        state=state.lower(),
                        created_at=ev.created_at,
                        closed_at=ev.created_at if state.lower() == "closed" else None,
                        author_login=ev.actor_login,
                    )
                )
            elif ev.type == HistoricalEventType.PUSH:
                head_sha = ev.payload_summary.get("head") or f"commit_{len(commits)}"
                commits.append(
                    CommitRecord(
                        sha=head_sha,
                        message="Historical commit from GH Archive",
                        author_login=ev.actor_login,
                        author_date=ev.created_at,
                    )
                )

        contributors: List[ContributorRecord] = [
            ContributorRecord(
                id=idx + 1,
                login=login,
                contributions_count=count,
            )
            for idx, (login, count) in enumerate(actors_seen.items())
        ]

        summary = response.timeline_summary
        repo_info = RepositoryInfo(
            name=repo_name.split("/")[-1] if "/" in repo_name else repo_name,
            full_name=repo_name,
            stars=summary.event_type_counts.get(HistoricalEventType.WATCH.value, 0),
            forks=summary.event_type_counts.get("ForkEvent", 0),
            open_issues_count=len([i for i in issues if i.state == "open"]),
            default_branch="main",
            is_archived=False,
            created_at=summary.first_event_at or now_iso,
            last_updated_at=summary.last_event_at or now_iso,
            owner=owner,
            html_url=f"https://github.com/{repo_name}",
            license_name="MIT",
            fetched_at=now_iso,
        )

        return RepositoryMiningData(
            repository=repo_info,
            pull_requests=prs,
            issues=issues,
            commits=commits,
            contributors=contributors,
        )



archive_service = GHArchiveService()

