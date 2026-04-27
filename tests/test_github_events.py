"""Tests for GitHub event models."""

from src.models.github_events import GitHubIssue, GitHubLabel, GitHubRepository, IssuesEvent


def test_parse_issue_event():
    """Test parsing a complete IssuesEvent from field values."""
    event = IssuesEvent(
        action="opened",
        issue=GitHubIssue(
            number=1,
            title="Test Issue",
            body="Test body",
            labels=[GitHubLabel(id=1, name="bug", color="ff0000")],
            html_url="https://github.com/test/repo/issues/1",
            node_id="test_node",
        ),
        repository=GitHubRepository(
            full_name="test/repo",
            name="repo",
            owner_login="test",
        ),
    )
    assert event.action == "opened"
    assert event.issue.number == 1
    assert event.issue.labels[0].name == "bug"
    assert event.repository.full_name == "test/repo"


def test_github_issue_defaults():
    """Test GitHubIssue default values."""
    issue = GitHubIssue(number=42, title="Minimal issue")
    assert issue.body is None
    assert issue.labels == []
    assert issue.html_url == ""
    assert issue.node_id == ""


def test_github_label_optional_description():
    """Test GitHubLabel with and without description."""
    label = GitHubLabel(id=1, name="enhancement", color="0075ca")
    assert label.description is None

    label_with_desc = GitHubLabel(id=2, name="bug", color="ff0000", description="Something isn't working")
    assert label_with_desc.description == "Something isn't working"


def test_github_repository_defaults():
    """Test GitHubRepository default values."""
    repo = GitHubRepository(full_name="org/repo", name="repo")
    assert repo.owner_login == ""
