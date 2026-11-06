"""
Unit and integration tests for M0.2: GitHub GraphQL API Mining.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import httpx

from backend.app.main import app
from backend.app.services.graphql_service import (
    GitHubGraphQLService,
    graphql_service,
)
from backend.app.schemas.graphql_mining import GraphQLMiningRequest

client = TestClient(app)


@pytest.fixture
def sample_graphql_response():
    return {
        "data": {
            "rateLimit": {
                "limit": 5000,
                "cost": 1,
                "remaining": 4980,
                "resetAt": "2026-11-06T10:00:00Z",
            },
            "repository": {
                "name": "sample-repo",
                "nameWithOwner": "test-org/sample-repo",
                "description": "A high-performance repository.",
                "stargazerCount": 1250,
                "forkCount": 240,
                "isArchived": False,
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
                "primaryLanguage": {"name": "Python"},
                "licenseInfo": {"spdxId": "MIT", "name": "MIT License"},
                "defaultBranchRef": {
                    "name": "main",
                    "target": {
                        "history": {
                            "totalCount": 150,
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": [
                                {
                                    "oid": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
                                    "messageHeadline": "Refactor core engine",
                                    "committedDate": "2024-01-01T12:00:00Z",
                                    "author": {
                                        "name": "Alice Developer",
                                        "email": "alice@example.com",
                                        "user": {"login": "alicedev"},
                                    },
                                }
                            ],
                        }
                    },
                },
                "issues": {
                    "totalCount": 25,
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "number": 101,
                            "title": "Bug in query generator",
                            "state": "CLOSED",
                            "createdAt": "2023-11-01T10:00:00Z",
                            "closedAt": "2023-11-03T10:00:00Z",
                            "author": {"login": "reporter1"},
                            "comments": {"totalCount": 3},
                            "labels": {"nodes": [{"name": "bug"}, {"name": "p1"}]},
                        }
                    ],
                },
                "pullRequests": {
                    "totalCount": 40,
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "number": 55,
                            "title": "Implement GraphQL cursor pagination",
                            "state": "MERGED",
                            "merged": True,
                            "mergedAt": "2023-12-01T15:00:00Z",
                            "createdAt": "2023-11-28T10:00:00Z",
                            "closedAt": "2023-12-01T15:00:00Z",
                            "isDraft": False,
                            "author": {"login": "contributor1"},
                            "comments": {"totalCount": 5},
                            "reviews": {
                                "totalCount": 2,
                                "nodes": [
                                    {
                                        "state": "APPROVED",
                                        "submittedAt": "2023-11-30T10:00:00Z",
                                        "author": {"login": "leadmaintainer"},
                                    }
                                ],
                            },
                        }
                    ],
                },
                "mentionableUsers": {
                    "totalCount": 2,
                    "nodes": [
                        {"login": "leadmaintainer", "avatarUrl": "https://example.com/avatar1.png"},
                        {"login": "contributor1", "avatarUrl": "https://example.com/avatar2.png"},
                    ],
                },
            },
        }
    }


@pytest.mark.asyncio
async def test_graphql_mining_transformation(sample_graphql_response):
    """Verify that GraphQL response transforms cleanly into compatible REST schemas."""
    service = GitHubGraphQLService()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_graphql_response
    mock_client.post.return_value = mock_resp

    req = GraphQLMiningRequest(url="https://github.com/test-org/sample-repo")
    result = await service.mine_repository(req, client=mock_client)

    assert result.success is True
    assert result.metadata.repository_full_name == "test-org/sample-repo"
    assert result.metadata.rate_limit.cost == 1
    assert result.metadata.rate_limit.remaining == 4980

    # Verify repository metadata
    repo = result.data.repository
    assert repo is not None
    assert repo.name == "sample-repo"
    assert repo.stars == 1250
    assert repo.forks == 240
    assert repo.language == "Python"
    assert repo.license_name == "MIT"

    # Verify Pull Requests
    assert len(result.data.pull_requests) == 1
    pr = result.data.pull_requests[0]
    assert pr.number == 55
    assert pr.is_merged is True
    assert pr.state == "merged"
    assert pr.author_login == "contributor1"

    # Verify Issues
    assert len(result.data.issues) == 1
    issue = result.data.issues[0]
    assert issue.number == 101
    assert issue.state == "closed"
    assert "bug" in issue.labels

    # Verify Commits
    assert len(result.data.commits) == 1
    commit = result.data.commits[0]
    assert commit.sha == "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"
    assert commit.author_login == "alicedev"

    # Verify Contributors
    assert len(result.data.contributors) == 2
    assert result.data.contributors[0].login == "leadmaintainer"


@pytest.mark.asyncio
async def test_graphql_rate_limit_error():
    """Verify handling of HTTP 429/403 rate-limit responses."""
    service = GitHubGraphQLService()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 403
    mock_resp.text = "You have exceeded a secondary rate limit."
    mock_client.post.return_value = mock_resp

    with pytest.raises(RuntimeError) as exc_info:
        await service.execute_query("query { viewer { login } }", {}, client=mock_client)

    assert "rate limit exceeded" in str(exc_info.value).lower()


def test_api_graphql_mining_endpoint(monkeypatch, sample_graphql_response):
    """Test POST /api/repository/mine/graphql endpoint."""
    async def fake_execute_query(*args, **kwargs):
        return sample_graphql_response

    monkeypatch.setattr(graphql_service, "execute_query", fake_execute_query)

    response = client.post(
        "/api/repository/mine/graphql",
        json={"url": "test-org/sample-repo", "max_prs": 50},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "metadata" in body
    assert "data" in body
    assert body["data"]["repository"]["full_name"] == "test-org/sample-repo"
    assert len(body["data"]["pull_requests"]) == 1

