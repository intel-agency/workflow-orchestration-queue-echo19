"""Pydantic models and enums for work items."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    """Type of work to be performed."""

    PLAN = "plan"
    IMPLEMENT = "implement"
    REVIEW = "review"
    FIX = "fix"


class WorkItemStatus(StrEnum):
    """Status of a work item in the queue."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
    STALLED_BUDGET = "stalled_budget"
    INFRA_FAILURE = "infra_failure"


class WorkItem(BaseModel):
    """Unified representation of a work item from any provider."""

    id: str
    source_url: str
    context_body: str
    target_repo_slug: str
    task_type: TaskType
    status: WorkItemStatus = WorkItemStatus.QUEUED
    metadata: dict[str, Any] = Field(default_factory=dict)
    node_id: str | None = None
