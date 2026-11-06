import asyncio
import datetime
import re
from typing import Dict, Any, Tuple, Optional, List
import httpx

from ..config import settings
from ..schemas.repository import RepositoryInfo
from ..utils.validators import parse_github_repo


LINK_REL_REGEX = re.compile(r'<([^>]+)>\s*;\s*rel="([^"]+)"')

# Bounded retry policy for throttling. Long GitHub primary-limit resets are not slept through.
MAX_RETRY_ATTEMPTS = 3
MAX_RETRY_WAIT_SECONDS = 5.0


class GitHubAPIException(Exception):
    """Base exception for GitHub API interactions."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class RepositoryNotFoundError(GitHubAPIException):
    def __init__(self, owner: str, repo: str):
        super().__init__(
            message=(
                f"Repository '{owner}/{repo}' was not found on GitHub. "
                "Please check the spelling or ensure the repository is public."
            ),
            status_code=404,
        )


class RateLimitExceededError(GitHubAPIException):
    def __init__(self, reset_time_str: Optional[str] = None, retry_after: Optional[int] = None):
        msg = "GitHub API rate limit exceeded."
        if reset_time_str:
            msg += (
                f" Rate limit will reset at {reset_time_str} UTC. "
                "(Tip: set GITHUB_TOKEN in backend environment to increase quota)."
            )
        else:
            msg += " Please try again later or configure GITHUB_TOKEN."
        details = "GitHub REST API rate limit reached."
        if retry_after is not None:
            details += f" Retry-After: {retry_after}s."
        super().__init__(message=msg, status_code=429, details=details)


class GitHubConnectionError(GitHubAPIException):
    def __init__(self, details: str):
        super().__init__(
            message="Failed to connect to GitHub API. Please check network connectivity.",
            status_code=503,
            details=details,
        )


def parse_link_header(link_header: str) -> Dict[str, str]:
    """Parse RFC 5988 Link header into rel -> URL mapping."""
    links: Dict[str, str] = {}
    if not link_header:
        return links
    for part in link_header.split(","):
        match = LINK_REL_REGEX.search(part.strip())
        if match:
            links[match.group(2)] = match.group(1)
    return links


def extract_rate_limit_meta(headers: httpx.Headers) -> Dict[str, Any]:
    """Extract GitHub rate-limit headers into a plain dict. Never includes auth credentials."""
    rem = headers.get("x-ratelimit-remaining")
    lim = headers.get("x-ratelimit-limit")
    res = headers.get("x-ratelimit-reset")
    used = headers.get("x-ratelimit-used")
    retry_after_raw = headers.get("retry-after")

    remaining = int(rem) if rem and rem.isdigit() else None
    limit = int(lim) if lim and lim.isdigit() else None
    reset_ts = int(res) if res and res.isdigit() else None
    used_count = int(used) if used and used.isdigit() else None
    retry_after = int(retry_after_raw) if retry_after_raw and retry_after_raw.isdigit() else None

    reset_time_str = None
    if reset_ts:
        try:
            reset_dt = datetime.datetime.fromtimestamp(reset_ts, tz=datetime.timezone.utc)
            reset_time_str = reset_dt.strftime("%Y-%m-%d %H:%M:%S")
        except (OSError, OverflowError, ValueError):
            reset_time_str = None

    return {
        "remaining": remaining,
        "limit": limit,
        "reset": reset_time_str,
        "reset_timestamp": reset_ts,
        "used": used_count,
        "retry_after": retry_after,
        "authenticated": bool(settings.GITHUB_TOKEN),
    }


def is_rate_limit_response(response: httpx.Response, remaining: Optional[int]) -> bool:
    """Detect primary or secondary GitHub rate-limit responses (HTTP 403 or 429)."""
    if response.status_code == 429:
        return True
    if response.status_code != 403:
        return False
    if remaining == 0:
        return True
    text = (response.text or "").lower()
    return "rate limit" in text or "secondary rate limit" in text


class GitHubService:
    """Service to interact asynchronously with the official GitHub REST API."""

    def __init__(self):
        self.base_url = settings.GITHUB_API_BASE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        return headers

    async def github_get(
        self,
        url: str,
        *,
        client: httpx.AsyncClient,
        params: Optional[Dict[str, Any]] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        allow_retry: bool = True,
    ) -> httpx.Response:
        """
        GET a GitHub REST URL with rate-limit header tracking and bounded retries.

        Retries only when Retry-After (or a short default) is within MAX_RETRY_WAIT_SECONDS.
        Does not wait for the hourly primary-limit reset window.
        """
        headers = self._get_headers()
        attempts = 0
        last_response: Optional[httpx.Response] = None

        while attempts < MAX_RETRY_ATTEMPTS:
            attempts += 1
            try:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    follow_redirects=True,
                )
            except httpx.ConnectTimeout:
                raise GitHubConnectionError("Connection timed out while contacting GitHub API.")
            except httpx.ConnectError as e:
                raise GitHubConnectionError(f"Network error connecting to GitHub: {str(e)}")
            except httpx.RequestError as e:
                raise GitHubConnectionError(f"HTTP request error: {str(e)}")

            last_response = response
            meta = extract_rate_limit_meta(response.headers)

            if response.status_code in (403, 429) and is_rate_limit_response(response, meta["remaining"]):
                retry_after = meta["retry_after"]
                # Primary quota exhaustion will not recover within a request; do not retry-loop.
                if meta["remaining"] == 0:
                    raise RateLimitExceededError(meta["reset"], retry_after=retry_after)
                wait_s = float(retry_after) if retry_after is not None else 1.0
                if allow_retry and wait_s <= MAX_RETRY_WAIT_SECONDS and attempts < MAX_RETRY_ATTEMPTS:
                    await asyncio.sleep(wait_s)
                    continue
                raise RateLimitExceededError(meta["reset"], retry_after=retry_after)

            if response.status_code == 404 and owner and repo:
                raise RepositoryNotFoundError(owner, repo)

            if response.status_code == 403:
                target = f"{owner}/{repo}" if owner and repo else url
                raise GitHubAPIException(
                    message=f"Access to GitHub resource '{target}' was forbidden (HTTP 403).",
                    status_code=403,
                    details=(response.text or "")[:200],
                )

            if response.status_code >= 500:
                raise GitHubAPIException(
                    message="GitHub API is currently experiencing internal errors (5xx). Please try again shortly.",
                    status_code=502,
                    details=f"Status code {response.status_code}",
                )

            return response

        if last_response is not None:
            return last_response
        raise GitHubConnectionError("GitHub request failed without a response.")

    async def fetch_paginated(
        self,
        url: str,
        *,
        client: httpx.AsyncClient,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
        max_pages: int = 3,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Fetch list endpoints across multiple pages using GitHub Link headers.

        Returns (items, diagnostics) where diagnostics includes pages_fetched, has_more,
        warnings, error_message, status, and rate_limit.
        """
        collected: List[Any] = []
        pages_fetched = 0
        has_more = False
        warnings: List[str] = []
        error_message: Optional[str] = None
        rate_meta: Dict[str, Any] = extract_rate_limit_meta(httpx.Headers())
        next_url: Optional[str] = url
        next_params: Optional[Dict[str, Any]] = {**(params or {}), "per_page": per_page, "page": 1}

        while next_url and pages_fetched < max_pages:
            remaining = rate_meta.get("remaining")
            if remaining is not None and remaining <= 0:
                has_more = True
                warnings.append("Stopped pagination because GitHub rate-limit remaining is 0.")
                break

            try:
                response = await self.github_get(
                    next_url,
                    client=client,
                    params=next_params,
                    owner=owner,
                    repo=repo,
                    allow_retry=True,
                )
            except RateLimitExceededError as rle:
                has_more = True
                error_message = rle.message
                warnings.append(error_message)
                break
            except GitHubConnectionError as ce:
                error_message = ce.message
                warnings.append(error_message)
                has_more = True
                break
            except GitHubAPIException as ge:
                if ge.status_code == 404:
                    raise
                error_message = ge.message
                warnings.append(error_message)
                break

            rate_meta = extract_rate_limit_meta(response.headers)
            pages_fetched += 1

            if response.status_code == 202:
                # Contributor stats can be generated asynchronously.
                warnings.append("GitHub returned HTTP 202 (statistics still generating); collection is partial.")
                has_more = True
                error_message = "GitHub accepted the request but data was not ready (HTTP 202)."
                break

            if response.status_code != 200:
                error_message = f"HTTP {response.status_code} while paginating {url}"
                warnings.append(error_message)
                has_more = True
                break

            payload = response.json()
            if payload is None:
                break
            if not isinstance(payload, list):
                error_message = "Expected a JSON array from a paginated GitHub list endpoint."
                warnings.append(error_message)
                break
            if len(payload) == 0:
                has_more = False
                break

            collected.extend(payload)

            links = parse_link_header(response.headers.get("link", ""))
            next_link = links.get("next")
            if next_link and len(payload) >= 1:
                has_more = True
                next_url = next_link
                next_params = None  # query is already encoded in the Link URL
            else:
                has_more = False
                next_url = None

        if has_more and pages_fetched >= max_pages:
            warnings.append(
                f"Reached maximum configured pages ({max_pages}). "
                "Additional uncollected records remain on GitHub; this dataset is not complete."
            )

        status = "success"
        if error_message and not collected:
            status = "error"
        elif error_message or has_more:
            status = "partial"

        return collected, {
            "pages_fetched": pages_fetched,
            "has_more": has_more,
            "warnings": warnings,
            "error_message": error_message,
            "status": status,
            "rate_limit": rate_meta,
            "records_raw": len(collected),
        }

    async def fetch_repository(self, url_or_identifier: str) -> Tuple[RepositoryInfo, Dict[str, Any]]:
        """
        Parses repository URL/identifier and fetches comprehensive repository data from GitHub REST API.

        Returns:
            Tuple of (RepositoryInfo, metadata_dict) where metadata includes rate limit info.
        """
        owner, repo = parse_github_repo(url_or_identifier)
        api_url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self.github_get(api_url, client=client, owner=owner, repo=repo)
        except RateLimitExceededError:
            raise
        except RepositoryNotFoundError:
            raise
        except GitHubAPIException:
            raise

        rate_meta = extract_rate_limit_meta(response.headers)
        if response.status_code == 200:
            data = response.json()
            return self._transform_to_repository_info(data), {
                "remaining": rate_meta.get("remaining"),
                "reset": rate_meta.get("reset"),
            }

        raise GitHubAPIException(
            message=f"GitHub API returned unexpected status {response.status_code}.",
            status_code=response.status_code,
            details=(response.text or "")[:200],
        )

    def _transform_to_repository_info(self, data: Dict[str, Any]) -> RepositoryInfo:
        """Transforms raw GitHub API response to standardized RepositoryInfo model."""
        owner_data = data.get("owner", {}) or {}
        license_data = data.get("license") or {}

        license_name = None
        if isinstance(license_data, dict):
            license_name = license_data.get("spdx_id") or license_data.get("name")
            if license_name == "NOASSERTION":
                license_name = license_data.get("name") or "Custom"

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return RepositoryInfo(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            language=data.get("language"),
            created_at=data.get("created_at", ""),
            last_updated_at=data.get("updated_at", ""),
            open_issues_count=data.get("open_issues_count", 0),
            default_branch=data.get("default_branch", "main"),
            is_archived=bool(data.get("archived", False)),
            owner=owner_data.get("login", ""),
            owner_avatar_url=owner_data.get("avatar_url"),
            html_url=data.get("html_url", f"https://github.com/{data.get('full_name', '')}"),
            license_name=license_name,
            topics=data.get("topics", []),
            watchers_count=data.get("watchers_count", 0),
            size_kb=data.get("size", 0),
            network_count=data.get("network_count"),
            subscribers_count=data.get("subscribers_count"),
            fetched_at=now_iso,
        )


github_service = GitHubService()
