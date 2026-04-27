"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_work_item_data():
    """Provide sample data for WorkItem construction."""
    return {
        "id": "test-123",
        "source_url": "https://github.com/test/repo/issues/1",
        "context_body": "Test work item",
        "target_repo_slug": "test/repo",
        "task_type": "implement",
        "status": "queued",
    }
