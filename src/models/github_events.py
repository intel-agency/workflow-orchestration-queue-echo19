"""GitHub webhook event payload schemas."""

from pydantic import BaseModel, Field


class GitHubLabel(BaseModel):
    """GitHub label."""

    id: int
    name: str
    color: str
    description: str | None = None


class GitHubIssue(BaseModel):
    """GitHub issue."""

    number: int
    title: str
    body: str | None = None
    labels: list[GitHubLabel] = Field(default_factory=list)
    html_url: str = ""
    node_id: str = ""


class GitHubRepository(BaseModel):
    """GitHub repository."""

    full_name: str
    name: str
    owner_login: str = ""


class IssuesEvent(BaseModel):
    """GitHub issues webhook event."""

    action: str
    issue: GitHubIssue
    repository: GitHubRepository
