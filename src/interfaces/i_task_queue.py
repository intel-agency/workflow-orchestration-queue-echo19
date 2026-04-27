"""Abstract base class for task queue providers."""

from abc import ABC, abstractmethod

from src.models.work_item import WorkItem, WorkItemStatus


class ITaskQueue(ABC):
    """Provider-agnostic interface for managing work items."""

    @abstractmethod
    async def fetch_queued_items(self) -> list[WorkItem]:
        """Fetch all items currently in the queue."""

    @abstractmethod
    async def add_to_queue(self, item: WorkItem) -> bool:
        """Add a work item to the queue."""

    @abstractmethod
    async def update_item_status(self, item_id: str, status: WorkItemStatus, message: str | None = None) -> bool:
        """Update the status of a work item."""
