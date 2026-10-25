import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.utils.validators import parse_github_repo

client = TestClient(app)

def test_url_parser_valid():
    """Verify various valid GitHub repository formats."""
    assert parse_github_repo("https://github.com/fastapi/fastapi") == ("fastapi", "fastapi")
    assert parse_github_repo("http://github.com/pallets/flask") == ("pallets", "flask")
    assert parse_github_repo("github.com/psf/requests") == ("psf", "requests")
    assert parse_github_repo("https://www.github.com/facebook/react/") == ("facebook", "react")
    assert parse_github_repo("psf/requests.git") == ("psf", "requests")
    assert parse_github_repo("torvalds/linux") == ("torvalds", "linux")

def test_url_parser_invalid():
    """Verify that invalid repository inputs raise ValueError."""
    with pytest.raises(ValueError):
        parse_github_repo("")
    with pytest.raises(ValueError):
        parse_github_repo("https://google.com/foo/bar")
    with pytest.raises(ValueError):
        parse_github_repo("justastring")
    with pytest.raises(ValueError):
        parse_github_repo("https://github.com/")

def test_health_endpoint():
    """Verify health endpoint returns status 200."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Phase 1" in data["phase"]

def test_invalid_url_api():
    """Verify API rejects malformed URL with 400 Bad Request."""
    res = client.post("/api/repository/analyze", json={"url": "not-a-valid-github-url"})
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_REPOSITORY_URL"

def test_nonexistent_repository_api():
    """Verify API handles non-existent repository with 404 Not Found."""
    # Using a randomly generated nonexistent repository name
    res = client.post("/api/repository/analyze", json={"url": "https://github.com/nonexistent-user-xyz-9999/nonexistent-repo-9999"})
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()

@pytest.mark.parametrize("repo_url,expected_name", [
    ("https://github.com/fastapi/fastapi", "fastapi"),
    ("pallets/flask", "flask"),
    ("https://github.com/psf/requests", "requests"),
])
def test_live_public_repositories(repo_url, expected_name):
    """
    Test Phase 1 requirement:
    Test at least three public GitHub repositories and verify all required Phase 1 fields exist.
    """
    res = client.post("/api/repository/analyze", json={"url": repo_url})
    if res.status_code == 429:
        pytest.skip("GitHub unauthenticated rate limit reached in test environment.")
    
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    
    # Verify Phase 1 required fields
    assert data["name"].lower() == expected_name.lower()
    assert "full_name" in data and "/" in data["full_name"]
    assert "description" in data
    assert isinstance(data["stars"], int) and data["stars"] >= 0
    assert isinstance(data["forks"], int) and data["forks"] >= 0
    assert "language" in data
    assert "created_at" in data and len(data["created_at"]) > 0
    assert "last_updated_at" in data and len(data["last_updated_at"]) > 0
    assert isinstance(data["open_issues_count"], int)
    assert "default_branch" in data
    assert isinstance(data["is_archived"], bool)
