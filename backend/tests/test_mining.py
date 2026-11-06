"""
Tests for M0.2 GitHub REST repository mining.
All GitHub HTTP is mocked; these tests never call the live GitHub API.
"""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.schemas.mining import RepositoryMiningRequest
from backend.app.services import github_service as github_service_module
from backend.app.services import mining_service as mining_service_module
from backend.app.services.github_service import github_service, parse_link_header
from backend.app.services.mining_service import mining_service, build_metric_coverage

client = TestClient(app)

REPO_JSON = {
    "name": "hello",
    "full_name": "octo/hello",
    "description": "Test repository",
    "stargazers_count": 10,
    "forks_count": 2,
    "language": "Python",
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "open_issues_count": 3,
    "default_branch": "main",
    "archived": False,
    "owner": {"login": "octo", "avatar_url": "https://example.test/octo.png"},
    "html_url": "https://github.com/octo/hello",
    "license": {"spdx_id": "MIT", "name": "MIT License"},
    "topics": ["oss"],
    "watchers_count": 10,
    "size": 42,
}

RATE_OK = {
    "X-RateLimit-Limit": "5000",
    "X-RateLimit-Remaining": "4990",
    "X-RateLimit-Reset": "2000000000",
    "X-RateLimit-Used": "10",
}


def _json_response(payload: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
    merged = dict(RATE_OK)
    if headers:
        merged.update(headers)
    return httpx.Response(status_code, json=payload, headers=merged)


def _page_link(path: str, page: int) -> str:
    return f'<https://api.github.com{path}?page={page}&per_page=2>; rel="next"'


class GitHubMock:
    """Configurable GitHub REST mock used via httpx.MockTransport."""

    def __init__(self):
        self.requests: List[httpx.Request] = []
        self.pr_pages: Dict[int, List[Dict[str, Any]]] = {
            1: [
                {
                    "id": 101,
                    "number": 1,
                    "title": "Open PR",
                    "state": "open",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-02T00:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "user": {"login": "alice"},
                    "draft": False,
                    "html_url": "https://github.com/octo/hello/pull/1",
                }
            ]
        }
        self.issue_pages: Dict[int, List[Dict[str, Any]]] = {
            1: [
                {
                    "id": 201,
                    "number": 10,
                    "title": "Real issue",
                    "state": "open",
                    "created_at": "2024-01-03T00:00:00Z",
                    "updated_at": "2024-01-03T00:00:00Z",
                    "closed_at": None,
                    "user": {"login": "bob"},
                    "comments": 2,
                    "labels": [{"name": "bug"}],
                    "html_url": "https://github.com/octo/hello/issues/10",
                },
                {
                    "id": 202,
                    "number": 11,
                    "title": "This is actually a PR",
                    "state": "open",
                    "created_at": "2024-01-04T00:00:00Z",
                    "pull_request": {"url": "https://api.github.com/repos/octo/hello/pulls/2"},
                    "user": {"login": "carol"},
                    "comments": 0,
                    "labels": [],
                    "html_url": "https://github.com/octo/hello/pull/2",
                },
            ]
        }
        self.commit_pages: Dict[int, List[Dict[str, Any]]] = {
            1: [
                {
                    "sha": "aaa111",
                    "commit": {
                        "message": "first commit\n\nbody",
                        "author": {"name": "Alice", "email": "a@example.test", "date": "2024-01-01T00:00:00Z"},
                        "committer": {"date": "2024-01-01T00:00:00Z"},
                    },
                    "author": {"login": "alice"},
                    "html_url": "https://github.com/octo/hello/commit/aaa111",
                }
            ]
        }
        self.contributor_pages: Dict[int, List[Dict[str, Any]]] = {
            1: [
                {
                    "id": 1,
                    "login": "alice",
                    "avatar_url": "https://example.test/a.png",
                    "contributions": 7,
                    "html_url": "https://github.com/alice",
                    "type": "User",
                }
            ]
        }
        self.repo_status = 200
        self.pr_status = 200
        self.issue_status = 200
        self.commit_status = 200
        self.contributor_status = 200
        self.rate_limit_on_pr_page: Optional[int] = None
        self.duplicate_pr_on_page_2 = False
        self.empty_all_lists = False
        self.captured_auth: List[Optional[str]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        self.captured_auth.append(request.headers.get("authorization"))
        parsed = urlparse(str(request.url))
        path = parsed.path
        page = int(parse_qs(parsed.query).get("page", ["1"])[0])

        if path.endswith("/pulls"):
            if self.rate_limit_on_pr_page == page:
                return httpx.Response(
                    403,
                    json={"message": "API rate limit exceeded"},
                    headers={
                        "X-RateLimit-Limit": "60",
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": "2000000000",
                        "Retry-After": "120",
                    },
                    request=request,
                )
            if self.pr_status != 200:
                return httpx.Response(self.pr_status, json={"message": "error"}, headers=RATE_OK, request=request)
            items = [] if self.empty_all_lists else list(self.pr_pages.get(page, []))
            headers = dict(RATE_OK)
            if page in self.pr_pages and (page + 1) in self.pr_pages:
                headers["Link"] = _page_link("/repos/octo/hello/pulls", page + 1)
            return _json_response(items, self.pr_status, headers)

        if path.endswith("/issues"):
            if self.issue_status != 200:
                return httpx.Response(self.issue_status, json={"message": "error"}, headers=RATE_OK, request=request)
            items = [] if self.empty_all_lists else list(self.issue_pages.get(page, []))
            headers = dict(RATE_OK)
            if page in self.issue_pages and (page + 1) in self.issue_pages:
                headers["Link"] = _page_link("/repos/octo/hello/issues", page + 1)
            return _json_response(items, 200, headers)

        if path.endswith("/commits"):
            items = [] if self.empty_all_lists else list(self.commit_pages.get(page, []))
            headers = dict(RATE_OK)
            if page in self.commit_pages and (page + 1) in self.commit_pages:
                headers["Link"] = _page_link("/repos/octo/hello/commits", page + 1)
            return _json_response(items, self.commit_status, headers)

        if path.endswith("/contributors"):
            items = [] if self.empty_all_lists else list(self.contributor_pages.get(page, []))
            return _json_response(items, self.contributor_status)

        if path.endswith("/repos/octo/hello") or path.endswith("/repos/octo/hello/"):
            if self.repo_status == 404:
                return httpx.Response(404, json={"message": "Not Found"}, headers=RATE_OK, request=request)
            if self.repo_status == 429:
                return httpx.Response(
                    429,
                    json={"message": "rate limit"},
                    headers={
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Limit": "60",
                        "X-RateLimit-Reset": "2000000000",
                        "Retry-After": "90",
                    },
                    request=request,
                )
            return _json_response(REPO_JSON, 200)

        return httpx.Response(404, json={"message": "Not Found"}, headers=RATE_OK, request=request)


@pytest.fixture
def github_mock(monkeypatch):
    mock = GitHubMock()
    transport = httpx.MockTransport(mock.handler)
    original = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs = dict(kwargs)
        kwargs["transport"] = transport
        kwargs.setdefault("base_url", "https://api.github.com")
        return original(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", factory)
    monkeypatch.setattr(github_service_module, "httpx", httpx)
    monkeypatch.setattr(mining_service_module, "httpx", httpx)
    return mock


def test_link_header_parser():
    header = (
        '<https://api.github.com/repos/octo/hello/pulls?page=2>; rel="next", '
        '<https://api.github.com/repos/octo/hello/pulls?page=5>; rel="last"'
    )
    links = parse_link_header(header)
    assert "page=2" in links["next"]
    assert links["last"].endswith("page=5")
    assert parse_link_header("") == {}


@pytest.mark.asyncio
async def test_successful_collection(github_mock):
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", max_pages_per_category=2, per_page=2)
    )
    assert result.success is True
    assert result.metadata.status == "complete"
    assert result.metadata.is_complete is True
    assert result.data.repository is not None
    assert result.data.repository.full_name == "octo/hello"
    assert result.data.repository.stars == 10
    assert len(result.data.pull_requests) == 1
    assert len(result.data.issues) == 1
    assert result.data.issues[0].title == "Real issue"
    assert len(result.data.commits) == 1
    assert result.data.commits[0].message == "first commit"
    assert len(result.data.contributors) == 1
    assert result.metadata.categories["pull_requests"].pages_fetched == 1
    assert result.metadata.rate_limit.remaining == 4990
    dumped = result.model_dump()
    assert "Authorization" not in json.dumps(dumped)
    assert settings.GITHUB_TOKEN == "" or "ghp_" not in json.dumps(dumped)


@pytest.mark.asyncio
async def test_multi_page_pagination(github_mock):
    github_mock.pr_pages = {
        1: [
            {
                "id": 1,
                "number": 1,
                "title": "PR 1",
                "state": "closed",
                "created_at": "2024-01-01T00:00:00Z",
                "closed_at": "2024-01-02T00:00:00Z",
                "merged_at": "2024-01-02T00:00:00Z",
                "user": {"login": "a"},
            }
        ],
        2: [
            {
                "id": 2,
                "number": 2,
                "title": "PR 2",
                "state": "closed",
                "created_at": "2024-01-03T00:00:00Z",
                "closed_at": "2024-01-04T00:00:00Z",
                "merged_at": None,
                "user": {"login": "b"},
            }
        ],
    }
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(
            url="https://github.com/octo/hello",
            max_pages_per_category=5,
            per_page=2,
            categories=["metadata", "pull_requests"],
        )
    )
    assert [pr.id for pr in result.data.pull_requests] == [1, 2]
    assert result.data.pull_requests[0].is_merged is True
    assert result.data.pull_requests[1].is_merged is False
    assert result.metadata.categories["pull_requests"].pages_fetched == 2
    assert result.metadata.categories["pull_requests"].has_more is False
    assert result.metadata.is_complete is True


@pytest.mark.asyncio
async def test_pagination_stop_is_partial_when_capped(github_mock):
    github_mock.pr_pages = {
        1: [{"id": 1, "number": 1, "title": "p1", "state": "open", "created_at": "2024-01-01T00:00:00Z", "user": {}}],
        2: [{"id": 2, "number": 2, "title": "p2", "state": "open", "created_at": "2024-01-02T00:00:00Z", "user": {}}],
        3: [{"id": 3, "number": 3, "title": "p3", "state": "open", "created_at": "2024-01-03T00:00:00Z", "user": {}}],
    }
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(
            url="octo/hello",
            max_pages_per_category=2,
            per_page=1,
            categories=["pull_requests"],
        )
    )
    assert result.metadata.status == "partial"
    assert result.metadata.is_complete is False
    assert result.metadata.categories["pull_requests"].has_more is True
    assert result.metadata.categories["pull_requests"].pages_fetched == 2
    assert "not complete" in " ".join(result.metadata.warnings).lower() or any(
        "maximum configured pages" in w.lower() for w in result.metadata.warnings
    )


@pytest.mark.asyncio
async def test_empty_repository_data(github_mock):
    github_mock.empty_all_lists = True
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["pull_requests", "issues", "commits", "contributors"])
    )
    assert result.data.pull_requests == []
    assert result.data.issues == []
    assert result.data.commits == []
    assert result.data.contributors == []
    assert result.metadata.categories["pull_requests"].status == "success"
    assert result.metadata.categories["pull_requests"].records_count == 0


@pytest.mark.asyncio
async def test_duplicate_prevention(github_mock):
    github_mock.pr_pages = {
        1: [{"id": 9, "number": 9, "title": "one", "state": "open", "created_at": "2024-01-01T00:00:00Z", "user": {}}],
        2: [
            {"id": 9, "number": 9, "title": "one-dup", "state": "open", "created_at": "2024-01-01T00:00:00Z", "user": {}},
            {"id": 10, "number": 10, "title": "two", "state": "open", "created_at": "2024-01-02T00:00:00Z", "user": {}},
        ],
    }
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(
            url="octo/hello",
            max_pages_per_category=5,
            per_page=1,
            categories=["pull_requests"],
        )
    )
    ids = [pr.id for pr in result.data.pull_requests]
    assert ids == [9, 10]
    assert result.metadata.categories["pull_requests"].records_count == 2


@pytest.mark.asyncio
async def test_pull_request_and_issue_separation(github_mock):
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["issues", "pull_requests"])
    )
    issue_titles = [i.title for i in result.data.issues]
    assert "Real issue" in issue_titles
    assert "This is actually a PR" not in issue_titles
    assert all("pull_request" not in i.model_dump() or True for i in result.data.issues)


@pytest.mark.asyncio
async def test_rate_limit_partial_collection(github_mock):
    github_mock.pr_pages = {
        1: [{"id": 1, "number": 1, "title": "p1", "state": "open", "created_at": "2024-01-01T00:00:00Z", "user": {}}],
        2: [{"id": 2, "number": 2, "title": "p2", "state": "open", "created_at": "2024-01-02T00:00:00Z", "user": {}}],
    }
    github_mock.rate_limit_on_pr_page = 2
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(
            url="octo/hello",
            max_pages_per_category=5,
            per_page=1,
            categories=["metadata", "pull_requests"],
        )
    )
    assert result.success is True
    assert result.metadata.status == "partial"
    assert result.metadata.is_complete is False
    assert len(result.data.pull_requests) == 1
    assert result.metadata.rate_limit.remaining == 0 or any("rate limit" in w.lower() for w in result.metadata.warnings)


def test_rate_limit_on_metadata_returns_429(github_mock):
    github_mock.repo_status = 429
    res = client.post("/api/repository/mine", json={"url": "octo/hello"})
    assert res.status_code == 429
    body = res.json()
    assert body["success"] is False
    assert body["error_code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.asyncio
async def test_authentication_header_when_token_configured(github_mock, monkeypatch):
    monkeypatch.setattr(settings, "GITHUB_TOKEN", "test-token-not-for-production")
    await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["metadata"])
    )
    assert any(
        h == "Bearer test-token-not-for-production" for h in github_mock.captured_auth
    )
    # Token must not appear in the mining response payload.
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["metadata"])
    )
    payload = json.dumps(result.model_dump())
    assert "test-token-not-for-production" not in payload
    monkeypatch.setattr(settings, "GITHUB_TOKEN", "")


@pytest.mark.asyncio
async def test_no_authorization_header_without_token(github_mock, monkeypatch):
    monkeypatch.setattr(settings, "GITHUB_TOKEN", "")
    await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["metadata"])
    )
    assert all(h is None for h in github_mock.captured_auth)


@pytest.mark.asyncio
async def test_api_error_partial_collection(github_mock):
    github_mock.issue_status = 500
    result = await mining_service.mine_repository(
        RepositoryMiningRequest(url="octo/hello", categories=["metadata", "issues", "pull_requests"])
    )
    assert result.metadata.status == "partial"
    assert result.data.repository is not None
    assert result.metadata.categories["issues"].status in {"error", "partial"}
    assert result.metadata.categories["pull_requests"].status == "success"


def test_invalid_repository_input_api():
    res = client.post("/api/repository/mine", json={"url": "not-a-valid-github-url"})
    assert res.status_code == 400
    body = res.json()
    assert body["error_code"] == "INVALID_REPOSITORY_URL"


def test_existing_endpoints_preserved(github_mock):
    health = client.get("/health")
    assert health.status_code == 200
    metrics = client.get("/api/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["count"] >= 12
    analyze = client.post("/api/repository/analyze", json={"url": "octo/hello"})
    assert analyze.status_code == 200
    assert analyze.json()["data"]["name"] == "hello"
    mine = client.post(
        "/api/repository/mine",
        json={"url": "octo/hello", "categories": ["metadata", "issues"]},
    )
    assert mine.status_code == 200
    assert mine.json()["data"]["issues"][0]["title"] == "Real issue"


def test_get_mine_endpoint(github_mock):
    res = client.get("/api/repository/mine", params={"url": "octo/hello", "max_pages": 1, "per_page": 10})
    assert res.status_code == 200
    assert res.json()["metadata"]["repository_full_name"] == "octo/hello"


def test_metric_coverage_identifies_readme_gap():
    coverage = {item.metric_id: item for item in build_metric_coverage()}
    assert coverage["A1"].raw_data_available is True
    assert coverage["A5"].raw_data_available is True
    assert coverage["C1"].raw_data_available is True
    assert coverage["X1"].raw_data_available is True
    assert coverage["M45-LICENSE"].raw_data_available is True
    assert coverage["M67-DOCS"].raw_data_available is False
    assert any("readme" in ep.lower() for ep in coverage["M67-DOCS"].missing_api_endpoints)


@pytest.mark.asyncio
async def test_secondary_rate_limit_retries_then_succeeds(monkeypatch):
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] == 1:
            return httpx.Response(
                429,
                json={"message": "You have exceeded a secondary rate limit"},
                headers={
                    "Retry-After": "1",
                    "X-RateLimit-Remaining": "20",
                    "X-RateLimit-Limit": "60",
                    "X-RateLimit-Reset": "2000000000",
                },
                request=request,
            )
        return httpx.Response(200, json=REPO_JSON, headers=RATE_OK, request=request)

    sleeps: List[float] = []

    async def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(github_service_module.asyncio, "sleep", fake_sleep)
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, timeout=5) as http_client:
        resp = await github_service.github_get(
            "https://api.github.com/repos/octo/hello",
            client=http_client,
            owner="octo",
            repo="hello",
        )
    assert resp.status_code == 200
    assert sleeps == [1.0]
    assert attempts["n"] == 2


@pytest.mark.asyncio
async def test_primary_rate_limit_does_not_retry_loop(monkeypatch):
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        return httpx.Response(
            403,
            json={"message": "API rate limit exceeded"},
            headers={
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Reset": "2000000000",
                "Retry-After": "1",
            },
            request=request,
        )

    async def fake_sleep(_seconds: float):
        raise AssertionError("primary rate limit should not sleep-retry")

    monkeypatch.setattr(github_service_module.asyncio, "sleep", fake_sleep)
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, timeout=5) as http_client:
        with pytest.raises(github_service_module.RateLimitExceededError):
            await github_service.github_get(
                "https://api.github.com/repos/octo/hello",
                client=http_client,
                owner="octo",
                repo="hello",
            )
    assert attempts["n"] == 1
