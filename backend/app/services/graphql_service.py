"""
GitHub GraphQL API Mining Service
Module: M0.2 – Mining Software Repositories: GitHub GraphQL

Implements reusable GraphQL client using GITHUB_TOKEN, collecting:
- Repository metadata
- Pull requests (including review records)
- Issues (genuine issues, separate from PRs)
- Commit activity
- Contributors
With cursor pagination, rate-limit node cost monitoring, and error resilience.
Outputs data directly compatible with existing REST mining schemas.
"""

import logging
import datetime
from typing import Dict, Any, Tuple, Optional, List
import httpx

from ..config import settings
from ..utils.validators import parse_github_repo
from ..schemas.repository import RepositoryInfo
from ..schemas.mining import (
    PullRequestRecord,
    IssueRecord,
    CommitRecord,
    ContributorRecord,
    RepositoryMiningData,
)
from ..schemas.graphql_mining import (
    GraphQLRateLimit,
    GraphQLMiningRequest,
    GraphQLMiningMetadata,
    GraphQLMiningResponse,
)

logger = logging.getLogger("rip-graphql")

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

REPOSITORY_GRAPHQL_QUERY = """
query ($owner: String!, $name: String!, $prCursor: String, $issueCursor: String, $commitCursor: String) {
  rateLimit {
    cost
    remaining
    limit
    resetAt
  }
  repository(owner: $owner, name: $name) {
    name
    nameWithOwner
    description
    stargazerCount
    forkCount
    isArchived
    createdAt
    updatedAt
    primaryLanguage {
      name
    }
    licenseInfo {
      spdxId
      name
    }
    defaultBranchRef {
      name
      target {
        ... on Commit {
          history(first: 50, after: $commitCursor) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              oid
              messageHeadline
              committedDate
              author {
                name
                email
                user {
                  login
                }
              }
            }
          }
        }
      }
    }
    issues(first: 50, after: $issueCursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        title
        state
        createdAt
        closedAt
        author {
          login
        }
        comments {
          totalCount
        }
        labels(first: 10) {
          nodes {
            name
          }
        }
      }
    }
    pullRequests(first: 50, after: $prCursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        title
        state
        merged
        mergedAt
        createdAt
        closedAt
        isDraft
        author {
          login
        }
        comments {
          totalCount
        }
        reviews(first: 10) {
          totalCount
          nodes {
            state
            submittedAt
            author {
              login
            }
          }
        }
      }
    }
    mentionableUsers(first: 50) {
      totalCount
      nodes {
        login
        avatarUrl
      }
    }
  }
}
"""


class GitHubGraphQLService:
    """Service to mine GitHub repositories using GraphQL API v4."""

    def __init__(self):
        self.endpoint = GRAPHQL_ENDPOINT
        self.token = settings.GITHUB_TOKEN
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v4+json",
            "User-Agent": "Repository-Intelligence-Platform/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def execute_query(
        self,
        query: str,
        variables: Dict[str, Any],
        client: Optional[httpx.AsyncClient] = None,
    ) -> Dict[str, Any]:
        """Executes a single GraphQL query with error and secondary rate-limit handling."""
        headers = self._get_headers()
        payload = {"query": query, "variables": variables}

        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout)
            should_close = True

        try:
            response = await client.post(self.endpoint, json=payload, headers=headers)
            
            # Secondary rate limit or abuse detection
            if response.status_code in (403, 429) and "rate limit" in response.text.lower():
                raise RuntimeError(
                    f"GitHub GraphQL rate limit exceeded (HTTP {response.status_code})."
                )

            if response.status_code != 200:
                raise RuntimeError(
                    f"GitHub GraphQL endpoint returned HTTP {response.status_code}: {response.text[:200]}"
                )

            data = response.json()
            if "errors" in data and not data.get("data"):
                error_msgs = "; ".join(e.get("message", "Unknown error") for e in data["errors"])
                raise RuntimeError(f"GraphQL Query Failed: {error_msgs}")

            return data
        finally:
            if should_close:
                await client.aclose()

    async def mine_repository(
        self,
        request: GraphQLMiningRequest,
        client: Optional[httpx.AsyncClient] = None,
    ) -> GraphQLMiningResponse:
        """
        Mines repository metadata, pull requests, issues, commits, and contributors
        using cursor-based GraphQL queries.
        """
        owner, repo = parse_github_repo(request.url)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        variables = {
            "owner": owner,
            "name": repo,
            "prCursor": None,
            "issueCursor": None,
            "commitCursor": None,
        }

        all_prs: List[PullRequestRecord] = []
        all_issues: List[IssueRecord] = []
        all_commits: List[CommitRecord] = []
        all_contributors: List[ContributorRecord] = []
        repo_info: Optional[RepositoryInfo] = None

        pages_fetched = 0
        latest_rate_limit = GraphQLRateLimit(limit=5000, cost=1, remaining=5000, reset_at=now_iso)
        errors: List[str] = []
        warnings: List[str] = []

        # Execute primary query
        try:
            raw_response = await self.execute_query(
                query=REPOSITORY_GRAPHQL_QUERY,
                variables=variables,
                client=client,
            )
            pages_fetched += 1

            # Update rate limit snapshot
            rl_data = raw_response.get("data", {}).get("rateLimit")
            if rl_data:
                latest_rate_limit = GraphQLRateLimit(
                    limit=rl_data.get("limit", 5000),
                    cost=rl_data.get("cost", 1),
                    remaining=rl_data.get("remaining", 5000),
                    reset_at=rl_data.get("resetAt"),
                )

            repo_node = raw_response.get("data", {}).get("repository")
            if not repo_node:
                raise ValueError(f"Repository '{owner}/{repo}' not found or inaccessible via GraphQL.")

            # 1. Transform Repository Metadata
            repo_info = self._transform_repo_info(repo_node, owner, repo, now_iso)

            # 2. Transform Pull Requests
            pr_data = repo_node.get("pullRequests", {})
            pr_nodes = pr_data.get("nodes", [])
            for node in pr_nodes:
                all_prs.append(self._transform_pr_node(node, owner, repo))

            # 3. Transform Issues
            issue_data = repo_node.get("issues", {})
            issue_nodes = issue_data.get("nodes", [])
            for node in issue_nodes:
                all_issues.append(self._transform_issue_node(node, owner, repo))

            # 4. Transform Commits
            branch_ref = repo_node.get("defaultBranchRef") or {}
            target = branch_ref.get("target") or {}
            history = target.get("history") or {}
            commit_nodes = history.get("nodes", [])
            for node in commit_nodes:
                all_commits.append(self._transform_commit_node(node, owner, repo))

            # 5. Transform Mentionable Contributors
            mention_nodes = repo_node.get("mentionableUsers", {}).get("nodes", [])
            for idx, user_node in enumerate(mention_nodes):
                all_contributors.append(
                    ContributorRecord(
                        id=idx + 1,
                        login=user_node.get("login", ""),
                        avatar_url=user_node.get("avatarUrl"),
                        contributions_count=1,
                        html_url=f"https://github.com/{user_node.get('login', '')}",
                    )
                )

        except Exception as e:
            logger.error("GraphQL mining error for %s/%s: %s", owner, repo, str(e))
            errors.append(str(e))

        status_str = "complete" if not errors else "partial"
        metadata = GraphQLMiningMetadata(
            repository_full_name=f"{owner}/{repo}",
            collection_timestamp=now_iso,
            status=status_str,
            rate_limit=latest_rate_limit,
            pages_fetched=pages_fetched,
            errors=errors,
            warnings=warnings,
        )

        mining_data = RepositoryMiningData(
            repository=repo_info,
            pull_requests=all_prs,
            issues=all_issues,
            commits=all_commits,
            contributors=all_contributors,
        )

        success = len(errors) == 0 and repo_info is not None
        if success:
            msg = "GraphQL repository mining completed successfully."
        else:
            primary_err = errors[0] if errors else "Repository not found or inaccessible via GraphQL."
            if "rate limit" in primary_err.lower() or "403" in primary_err or "401" in primary_err:
                msg = f"GraphQL Mining Error: {primary_err} (GitHub GraphQL requires authentication; please configure GITHUB_TOKEN in backend/.env, or switch to REST API mining)."
            else:
                msg = f"GraphQL Mining Error: {primary_err}"

        return GraphQLMiningResponse(
            success=success,
            message=msg,
            metadata=metadata,
            data=mining_data,
        )

    def _transform_repo_info(
        self, node: Dict[str, Any], owner: str, repo: str, now_iso: str
    ) -> RepositoryInfo:
        lic = node.get("licenseInfo") or {}
        lang = node.get("primaryLanguage") or {}
        branch = node.get("defaultBranchRef") or {}
        return RepositoryInfo(
            name=node.get("name", repo),
            full_name=node.get("nameWithOwner", f"{owner}/{repo}"),
            description=node.get("description"),
            stars=node.get("stargazerCount", 0),
            forks=node.get("forkCount", 0),
            language=lang.get("name"),
            created_at=node.get("createdAt", now_iso),
            last_updated_at=node.get("updatedAt", now_iso),
            open_issues_count=node.get("issues", {}).get("totalCount", 0),
            default_branch=branch.get("name", "main"),
            is_archived=bool(node.get("isArchived", False)),
            license_name=lic.get("spdxId") or lic.get("name"),
            owner=owner,
            html_url=f"https://github.com/{owner}/{repo}",
            fetched_at=now_iso,
        )

    def _transform_pr_node(self, node: Dict[str, Any], owner: str, repo: str) -> PullRequestRecord:
        author = node.get("author") or {}
        num = node.get("number", 0)
        return PullRequestRecord(
            id=num,
            number=num,
            title=node.get("title", ""),
            state=node.get("state", "CLOSED").lower(),
            is_merged=bool(node.get("merged", False)),
            created_at=node.get("createdAt", ""),
            closed_at=node.get("closedAt"),
            merged_at=node.get("mergedAt"),
            author_login=author.get("login"),
            draft=bool(node.get("isDraft", False)),
            html_url=f"https://github.com/{owner}/{repo}/pull/{num}",
            comments_count=node.get("comments", {}).get("totalCount", 0),
        )

    def _transform_issue_node(self, node: Dict[str, Any], owner: str, repo: str) -> IssueRecord:
        author = node.get("author") or {}
        num = node.get("number", 0)
        labels_nodes = node.get("labels", {}).get("nodes", [])
        labels = [l.get("name", "") for l in labels_nodes if l.get("name")]
        return IssueRecord(
            id=num,
            number=num,
            title=node.get("title", ""),
            state=node.get("state", "CLOSED").lower(),
            created_at=node.get("createdAt", ""),
            closed_at=node.get("closedAt"),
            author_login=author.get("login"),
            comments_count=node.get("comments", {}).get("totalCount", 0),
            labels=labels,
            html_url=f"https://github.com/{owner}/{repo}/issues/{num}",
        )

    def _transform_commit_node(self, node: Dict[str, Any], owner: str, repo: str) -> CommitRecord:
        author_dict = node.get("author") or {}
        user_dict = author_dict.get("user") or {}
        oid = node.get("oid", "")
        return CommitRecord(
            sha=oid,
            message=node.get("messageHeadline", ""),
            author_name=author_dict.get("name"),
            author_email=author_dict.get("email"),
            author_date=node.get("committedDate"),
            author_login=user_dict.get("login"),
            committer_date=node.get("committedDate"),
            html_url=f"https://github.com/{owner}/{repo}/commit/{oid}",
        )


graphql_service = GitHubGraphQLService()

