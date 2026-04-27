"""Tests for WorkItem model."""

from src.models.work_item import TaskType, WorkItem, WorkItemStatus


def test_create_work_item(sample_work_item_data):
    """Test basic WorkItem construction from dict."""
    item = WorkItem(**sample_work_item_data)
    assert item.id == "test-123"
    assert item.task_type == TaskType.IMPLEMENT
    assert item.status == WorkItemStatus.QUEUED


def test_work_item_status_transitions(sample_work_item_data):
    """Test that WorkItem status can be transitioned through the lifecycle."""
    item = WorkItem(**sample_work_item_data)
    item.status = WorkItemStatus.IN_PROGRESS
    assert item.status == WorkItemStatus.IN_PROGRESS
    item.status = WorkItemStatus.SUCCESS
    assert item.status == WorkItemStatus.SUCCESS


def test_work_item_default_status(sample_work_item_data):
    """Test that status defaults to QUEUED when not specified."""
    del sample_work_item_data["status"]
    item = WorkItem(**sample_work_item_data)
    assert item.status == WorkItemStatus.QUEUED


def test_work_item_metadata_default():
    """Test that metadata defaults to empty dict."""
    item = WorkItem(
        id="meta-test",
        source_url="https://github.com/test/repo/issues/2",
        context_body="Metadata test",
        target_repo_slug="test/repo",
        task_type=TaskType.PLAN,
    )
    assert item.metadata == {}
    assert item.node_id is None


def test_all_task_types():
    """Test that all TaskType enum values are accessible."""
    assert TaskType.PLAN == "plan"
    assert TaskType.IMPLEMENT == "implement"
    assert TaskType.REVIEW == "review"
    assert TaskType.FIX == "fix"


def test_all_work_item_statuses():
    """Test that all WorkItemStatus enum values are accessible."""
    assert WorkItemStatus.QUEUED == "queued"
    assert WorkItemStatus.IN_PROGRESS == "in_progress"
    assert WorkItemStatus.SUCCESS == "success"
    assert WorkItemStatus.ERROR == "error"
    assert WorkItemStatus.STALLED_BUDGET == "stalled_budget"
    assert WorkItemStatus.INFRA_FAILURE == "infra_failure"
