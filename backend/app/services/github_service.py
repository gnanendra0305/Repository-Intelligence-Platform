import datetime
from typing import Dict, Any, Tuple, Optional
import httpx

from ..config import settings
from ..schemas.repository import RepositoryInfo
from ..utils.validators import parse_github_repo


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
            message=f"Repository '{owner}/{repo}' was not found on GitHub. Please check the spelling or ensure the repository is public.",
            status_code=404
        )


class RateLimitExceededError(GitHubAPIException):
    def __init__(self, reset_time_str: Optional[str] = None):
        msg = "GitHub API rate limit exceeded."
        if reset_time_str:
            msg += f" Rate limit will reset at {reset_time_str} UTC. (Tip: set GITHUB_TOKEN in backend environment to increase quota)."
        else:
            msg += " Please try again later or configure GITHUB_TOKEN."
        super().__init__(message=msg, status_code=429, details="GitHub REST API unauthenticated rate limit reached.")


class GitHubConnectionError(GitHubAPIException):
    def __init__(self, details: str):
        super().__init__(
            message="Failed to connect to GitHub API. Please check network connectivity.",
            status_code=503,
            details=details
        )


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

    async def fetch_repository(self, url_or_identifier: str) -> Tuple[RepositoryInfo, Dict[str, Any]]:
        """
        Parses repository URL/identifier and fetches comprehensive repository data from GitHub REST API.
        
        Returns:
            Tuple of (RepositoryInfo, metadata_dict) where metadata includes rate limit info.
        """
        owner, repo = parse_github_repo(url_or_identifier)
        api_url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url, headers=headers, follow_redirects=True)
        except httpx.ConnectTimeout:
            raise GitHubConnectionError("Connection timed out while contacting GitHub API.")
        except httpx.ConnectError as e:
            raise GitHubConnectionError(f"Network error connecting to GitHub: {str(e)}")
        except httpx.RequestError as e:
            raise GitHubConnectionError(f"HTTP request error: {str(e)}")

        # Extract rate limit headers
        rate_remaining = response.headers.get("x-ratelimit-remaining")
        rate_reset = response.headers.get("x-ratelimit-reset")
        reset_time_str = None
        if rate_reset and rate_reset.isdigit():
            try:
                reset_dt = datetime.datetime.fromtimestamp(int(rate_reset), tz=datetime.timezone.utc)
                reset_time_str = reset_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        rate_meta = {
            "remaining": int(rate_remaining) if rate_remaining and rate_remaining.isdigit() else None,
            "reset": reset_time_str
        }

        # Check response status
        if response.status_code == 200:
            data = response.json()
            return self._transform_to_repository_info(data), rate_meta

        if response.status_code == 404:
            raise RepositoryNotFoundError(owner, repo)

        if response.status_code == 403:
            # Check if this is a rate limit error
            if rate_remaining == "0" or "rate limit" in response.text.lower():
                raise RateLimitExceededError(reset_time_str)
            raise GitHubAPIException(
                message=f"Access to GitHub repository '{owner}/{repo}' was forbidden (HTTP 403).",
                status_code=403,
                details=response.text[:200]
            )

        if response.status_code >= 500:
            raise GitHubAPIException(
                message="GitHub API is currently experiencing internal errors (5xx). Please try again shortly.",
                status_code=502,
                details=f"Status code {response.status_code}"
            )

        raise GitHubAPIException(
            message=f"GitHub API returned unexpected status {response.status_code}.",
            status_code=response.status_code,
            details=response.text[:200]
        )

    def _transform_to_repository_info(self, data: Dict[str, Any]) -> RepositoryInfo:
        """Transforms raw GitHub API response to standardized RepositoryInfo model."""
        owner_data = data.get("owner", {})
        license_data = data.get("license") or {}
        
        license_name = None
        if isinstance(license_data, dict):
            license_name = license_data.get("spdx_id") or license_data.get("name")
            if license_name == "NOASSERTION":
                license_name = license_data.get("name") or "Custom"

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return RepositoryInfo(
            # Phase 1 Required Fields
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
            
            # Supplementary UI Fields
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
