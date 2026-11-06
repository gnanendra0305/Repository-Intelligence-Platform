"""
GitHub Repository Mining Service
Module: M0.2 – GitHub Repository Mining (REST API Collection Pipeline)

Extends basic repository metadata collection into a full repository mining pipeline.
Collects 5 core categories via official GitHub REST API:
1. Repository Metadata
2. Pull Requests (open, closed, and merged)
3. Issues (excluding pull requests)
4. Commits
5. Contributors

Implements multi-page pagination with Link header following, deduplication,
rate-limit monitoring, bounded retries, and fault-tolerant partial collection.
"""

import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
import httpx

from ..config import settings
from ..schemas.mining import (
    PullRequestRecord,
    IssueRecord,
    CommitRecord,
    ContributorRecord,
    CategoryCollectionStats,
    RateLimitInfo,
    CollectionMetadata,
    RepositoryMiningData,
    RepositoryMiningRequest,
    RepositoryMiningResponse,
    MetricFieldCoverage,
)
from ..utils.validators import parse_github_repo
from .github_service import (
    github_service,
    GitHubAPIException,
    RepositoryNotFoundError,
    RateLimitExceededError,
    extract_rate_limit_meta,
)
from .metric_registry import metric_registry_service

logger = logging.getLogger("rip-mining")

ALL_CATEGORIES = ["metadata", "pull_requests", "issues", "commits", "contributors"]

# Endpoints this REST miner actually calls. Query-string variants are treated as the same path.
COLLECTED_API_PATHS = {
    "/repos/{owner}/{repo}",
    "/repos/{owner}/{repo}/pulls",
    "/repos/{owner}/{repo}/issues",
    "/repos/{owner}/{repo}/commits",
    "/repos/{owner}/{repo}/contributors",
}

# Maps GitHub payload field names (as listed in M0.1) to collected record attributes.
COLLECTED_PAYLOAD_FIELDS = {
    "state",
    "merged_at",
    "closed_at",
    "created_at",
    "number",
    "open_issues_count",
    "stargazers_count",
    "forks_count",
    "license",
    "id",
    "title",
    "updated_at",
    "sha",
    "login",
    "contributions",
}


def _normalize_endpoint(endpoint: str) -> str:
    path = endpoint.split("?")[0].strip()
    if not path.startswith("/"):
        path = "/" + path
    return path


def build_metric_coverage() -> List[MetricFieldCoverage]:
    """
    Compare M0.1 required_payload_fields / required_api_endpoints against this REST collector.
    Does not compute metric values.
    """
    coverage: List[MetricFieldCoverage] = []
    for metric in metric_registry_service.get_all_metrics():
        missing_endpoints = [
            ep for ep in metric.required_api_endpoints
            if _normalize_endpoint(ep) not in COLLECTED_API_PATHS
        ]
        missing_fields = [
            field for field in metric.required_payload_fields
            if field not in COLLECTED_PAYLOAD_FIELDS
        ]
        notes = None
        if missing_endpoints or missing_fields:
            notes = "Required GitHub REST fields or endpoints are not collected in M0.2."
        elif metric.metric_id in {"A4", "A7", "A8", "A8R", "C2"}:
            notes = (
                "Raw fields are collected, but completeness depends on pagination caps. "
                "Do not treat a truncated sample as a complete repository history."
            )
        coverage.append(
            MetricFieldCoverage(
                metric_id=metric.metric_id,
                metric_name=metric.metric_name,
                raw_data_available=not missing_endpoints and not missing_fields,
                missing_payload_fields=missing_fields,
                missing_api_endpoints=missing_endpoints,
                notes=notes,
            )
        )
    return coverage


def _rate_info_from_meta(meta: Dict[str, Any]) -> RateLimitInfo:
    return RateLimitInfo(
        remaining=meta.get("remaining"),
        limit=meta.get("limit"),
        reset_timestamp=meta.get("reset_timestamp"),
        reset_time_utc=(
            f"{meta['reset']} UTC" if meta.get("reset") else None
        ),
        used=meta.get("used"),
        retry_after_seconds=meta.get("retry_after"),
        authenticated=bool(meta.get("authenticated", bool(settings.GITHUB_TOKEN))),
    )


def _process_pr(item: Dict[str, Any]) -> Tuple[Optional[PullRequestRecord], Any]:
    pr_id = item.get("id")
    if pr_id is None:
        return None, None
    user = item.get("user") or {}
    record = PullRequestRecord(
        id=pr_id,
        number=item.get("number", 0),
        title=item.get("title", ""),
        state=item.get("state", "open"),
        is_merged=item.get("merged_at") is not None,
        created_at=item.get("created_at", ""),
        updated_at=item.get("updated_at"),
        closed_at=item.get("closed_at"),
        merged_at=item.get("merged_at"),
        author_login=user.get("login") if isinstance(user, dict) else None,
        draft=bool(item.get("draft", False)),
        html_url=item.get("html_url"),
        comments_count=item.get("comments"),
    )
    return record, pr_id


def _process_issue(item: Dict[str, Any]) -> Tuple[Optional[IssueRecord], Any]:
    # GitHub /issues returns pull requests as well; exclude those.
    if "pull_request" in item:
        return None, None
    issue_id = item.get("id")
    if issue_id is None:
        return None, None
    user = item.get("user") or {}
    label_names = [
        lbl.get("name") for lbl in item.get("labels", [])
        if isinstance(lbl, dict) and "name" in lbl
    ]
    record = IssueRecord(
        id=issue_id,
        number=item.get("number", 0),
        title=item.get("title", ""),
        state=item.get("state", "open"),
        created_at=item.get("created_at", ""),
        updated_at=item.get("updated_at"),
        closed_at=item.get("closed_at"),
        author_login=user.get("login") if isinstance(user, dict) else None,
        comments_count=item.get("comments", 0) or 0,
        labels=label_names,
        html_url=item.get("html_url"),
    )
    return record, issue_id


def _process_commit(item: Dict[str, Any]) -> Tuple[Optional[CommitRecord], Any]:
    sha = item.get("sha")
    if not sha:
        return None, None
    commit_obj = item.get("commit", {}) or {}
    author_obj = commit_obj.get("author", {}) or {}
    committer_obj = commit_obj.get("committer", {}) or {}
    github_author = item.get("author") or {}
    raw_msg = commit_obj.get("message", "") or ""
    first_line = raw_msg.split("\n")[0]
    record = CommitRecord(
        sha=sha,
        message=first_line,
        author_name=author_obj.get("name"),
        author_email=author_obj.get("email"),
        author_date=author_obj.get("date"),
        author_login=github_author.get("login") if isinstance(github_author, dict) else None,
        committer_date=committer_obj.get("date"),
        html_url=item.get("html_url"),
    )
    return record, sha


def _process_contributor(item: Dict[str, Any]) -> Tuple[Optional[ContributorRecord], Any]:
    c_id = item.get("id")
    login = item.get("login")
    if c_id is None or not login:
        return None, None
    record = ContributorRecord(
        id=c_id,
        login=login,
        avatar_url=item.get("avatar_url"),
        contributions_count=item.get("contributions", 0) or 0,
        html_url=item.get("html_url"),
        user_type=item.get("type", "User") or "User",
    )
    return record, c_id


class RepositoryMiningService:
    """Service orchestrating multi-category repository mining with pagination and rate-limit safety."""

    def __init__(self):
        self.base_url = settings.GITHUB_API_BASE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    def _dedupe(self, raw_items: List[Any], process_fn) -> List[Any]:
        unique: List[Any] = []
        seen: Set[Any] = set()
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                continue
            processed, key = process_fn(raw_item)
            if processed is None or key is None:
                continue
            if key in seen:
                continue
            seen.add(key)
            unique.append(processed)
        return unique

    async def _collect_category(
        self,
        *,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        cat_name: str,
        endpoint_url: str,
        params: Dict[str, Any],
        process_fn,
        request: RepositoryMiningRequest,
        rate_info: RateLimitInfo,
        warnings: List[str],
        errors: List[str],
    ) -> Tuple[List[Any], CategoryCollectionStats, RateLimitInfo]:
        if rate_info.remaining is not None and rate_info.remaining <= 0:
            msg = f"Skipped '{cat_name}' because the GitHub rate limit is exhausted."
            warnings.append(msg)
            return [], CategoryCollectionStats(
                records_count=0,
                pages_fetched=0,
                has_more=True,
                status="skipped",
                error_message=msg,
            ), rate_info

        raw_items, diag = await github_service.fetch_paginated(
            endpoint_url,
            client=client,
            params=params,
            per_page=request.per_page,
            max_pages=request.max_pages_per_category,
            owner=owner,
            repo=repo,
        )
        if diag.get("rate_limit"):
            rate_info = _rate_info_from_meta(diag["rate_limit"])
        for warning in diag.get("warnings") or []:
            warnings.append(f"{cat_name}: {warning}")
        if diag.get("error_message"):
            errors.append(f"{cat_name}: {diag['error_message']}")

        records = self._dedupe(raw_items, process_fn)
        return records, CategoryCollectionStats(
            records_count=len(records),
            pages_fetched=diag.get("pages_fetched", 0),
            has_more=bool(diag.get("has_more")),
            status=diag.get("status", "success"),
            error_message=diag.get("error_message"),
        ), rate_info

    async def mine_repository(
        self,
        request: RepositoryMiningRequest,
        client: Optional[httpx.AsyncClient] = None,
    ) -> RepositoryMiningResponse:
        owner, repo = parse_github_repo(request.url)
        full_name = f"{owner}/{repo}"
        collection_start = datetime.datetime.now(datetime.timezone.utc).isoformat()

        requested = request.categories or list(ALL_CATEGORIES)
        unknown = [c for c in requested if c not in ALL_CATEGORIES]
        categories_to_run = [c for c in requested if c in ALL_CATEGORIES]

        rate_info = RateLimitInfo(authenticated=bool(settings.GITHUB_TOKEN))
        categories_stats: Dict[str, CategoryCollectionStats] = {}
        errors: List[str] = []
        warnings: List[str] = []
        if unknown:
            warnings.append(f"Ignored unknown categories: {unknown}")

        repo_metadata = None
        mined_prs: List[PullRequestRecord] = []
        mined_issues: List[IssueRecord] = []
        mined_commits: List[CommitRecord] = []
        mined_contributors: List[ContributorRecord] = []

        async def _run_mining(http_client: httpx.AsyncClient):
            nonlocal rate_info, repo_metadata, mined_prs, mined_issues, mined_commits, mined_contributors

            if "metadata" in categories_to_run:
                try:
                    meta_url = f"{self.base_url}/repos/{owner}/{repo}"
                    resp = await github_service.github_get(
                        meta_url,
                        client=http_client,
                        owner=owner,
                        repo=repo,
                    )
                    rate_info = _rate_info_from_meta(extract_rate_limit_meta(resp.headers))
                    raw_meta = resp.json()
                    repo_metadata = github_service._transform_to_repository_info(raw_meta)
                    categories_stats["metadata"] = CategoryCollectionStats(
                        records_count=1,
                        pages_fetched=1,
                        has_more=False,
                        status="success",
                    )
                except (RepositoryNotFoundError, RateLimitExceededError):
                    raise
                except GitHubAPIException as ge:
                    logger.error("Metadata collection failed for %s: %s", full_name, ge.message)
                    categories_stats["metadata"] = CategoryCollectionStats(
                        records_count=0,
                        pages_fetched=1,
                        has_more=False,
                        status="error",
                        error_message=ge.message,
                    )
                    errors.append(f"Metadata collection failed: {ge.message}")
                except Exception as e:
                    logger.error("Metadata collection failed for %s: %s", full_name, str(e))
                    categories_stats["metadata"] = CategoryCollectionStats(
                        records_count=0,
                        pages_fetched=1,
                        has_more=False,
                        status="error",
                        error_message=str(e),
                    )
                    errors.append(f"Metadata collection failed: {str(e)}")

            if rate_info.remaining is not None and rate_info.remaining <= 0:
                warnings.append(
                    "GitHub rate limit exhausted after metadata. Remaining categories were not collected."
                )
                for cat in categories_to_run:
                    if cat != "metadata" and cat not in categories_stats:
                        categories_stats[cat] = CategoryCollectionStats(
                            records_count=0,
                            pages_fetched=0,
                            has_more=True,
                            status="skipped",
                            error_message="Rate limit exhausted",
                        )
                return

            if "pull_requests" in categories_to_run:
                mined_prs, pr_stat, rate_info = await self._collect_category(
                    client=http_client,
                    owner=owner,
                    repo=repo,
                    cat_name="pull_requests",
                    endpoint_url=f"{self.base_url}/repos/{owner}/{repo}/pulls",
                    params={"state": "all", "sort": "created", "direction": "desc"},
                    process_fn=_process_pr,
                    request=request,
                    rate_info=rate_info,
                    warnings=warnings,
                    errors=errors,
                )
                categories_stats["pull_requests"] = pr_stat

            if "issues" in categories_to_run:
                mined_issues, issue_stat, rate_info = await self._collect_category(
                    client=http_client,
                    owner=owner,
                    repo=repo,
                    cat_name="issues",
                    endpoint_url=f"{self.base_url}/repos/{owner}/{repo}/issues",
                    params={"state": "all", "sort": "created", "direction": "desc"},
                    process_fn=_process_issue,
                    request=request,
                    rate_info=rate_info,
                    warnings=warnings,
                    errors=errors,
                )
                categories_stats["issues"] = issue_stat

            if "commits" in categories_to_run:
                mined_commits, commit_stat, rate_info = await self._collect_category(
                    client=http_client,
                    owner=owner,
                    repo=repo,
                    cat_name="commits",
                    endpoint_url=f"{self.base_url}/repos/{owner}/{repo}/commits",
                    params={},
                    process_fn=_process_commit,
                    request=request,
                    rate_info=rate_info,
                    warnings=warnings,
                    errors=errors,
                )
                categories_stats["commits"] = commit_stat

            if "contributors" in categories_to_run:
                mined_contributors, contrib_stat, rate_info = await self._collect_category(
                    client=http_client,
                    owner=owner,
                    repo=repo,
                    cat_name="contributors",
                    endpoint_url=f"{self.base_url}/repos/{owner}/{repo}/contributors",
                    params={"anon": "false"},
                    process_fn=_process_contributor,
                    request=request,
                    rate_info=rate_info,
                    warnings=warnings,
                    errors=errors,
                )
                categories_stats["contributors"] = contrib_stat

        if client:
            await _run_mining(client)
        else:
            async with httpx.AsyncClient(timeout=self.timeout) as http_client:
                await _run_mining(http_client)

        total_records = (
            (1 if repo_metadata else 0)
            + len(mined_prs)
            + len(mined_issues)
            + len(mined_commits)
            + len(mined_contributors)
        )
        pages_fetched_total = sum(stat.pages_fetched for stat in categories_stats.values())
        has_any_more = any(stat.has_more for stat in categories_stats.values())
        has_any_error = any(stat.status == "error" for stat in categories_stats.values()) or bool(errors)
        has_skipped = any(stat.status == "skipped" for stat in categories_stats.values())
        has_partial_category = any(stat.status == "partial" for stat in categories_stats.values())

        if has_any_error and total_records == 0:
            overall_status = "failed"
            is_complete = False
        elif has_any_more or has_any_error or has_skipped or has_partial_category:
            overall_status = "partial"
            is_complete = False
        else:
            overall_status = "complete"
            is_complete = True

        metadata = CollectionMetadata(
            repository_full_name=full_name,
            collection_timestamp=collection_start,
            status=overall_status,
            is_complete=is_complete,
            categories=categories_stats,
            total_records_collected=total_records,
            pages_fetched_total=pages_fetched_total,
            rate_limit=rate_info,
            errors=errors,
            warnings=warnings,
            metric_coverage=build_metric_coverage(),
        )

        mining_data = RepositoryMiningData(
            repository=repo_metadata,
            pull_requests=mined_prs,
            issues=mined_issues,
            commits=mined_commits,
            contributors=mined_contributors,
        )

        return RepositoryMiningResponse(
            success=overall_status != "failed",
            message=(
                f"Repository mining {overall_status}: collected {len(mined_prs)} PRs, "
                f"{len(mined_issues)} issues, {len(mined_commits)} commits, "
                f"{len(mined_contributors)} contributors."
            ),
            metadata=metadata,
            data=mining_data,
        )


mining_service = RepositoryMiningService()
