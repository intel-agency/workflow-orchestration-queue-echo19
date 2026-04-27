"""
OS-APOW Work Event Notifier.

A FastAPI-based webhook receiver that maps provider events (GitHub, etc.)
to a unified Work Item queue.
"""

import hashlib
import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from src.interfaces.i_task_queue import ITaskQueue
from src.models.work_item import TaskType, WorkItem, WorkItemStatus

# --- FastAPI Application ---

app = FastAPI(title="OS-APOW Event Notifier", version="0.1.0")


# --- GitHub Issues Queue (Phase 1) ---


class GitHubIssuesQueue(ITaskQueue):
    """Phase 1 implementation: Maps WorkItems to GitHub Issue Labels/Comments."""

    def __init__(self, token: str) -> None:
        self.token = token

    async def fetch_queued_items(self) -> list[WorkItem]:
        """Fetch all items currently in the queue (not used by notifier)."""
        return []

    async def update_item_status(self, item_id: str, status: WorkItemStatus, message: str | None = None) -> bool:
        """Update the status of a work item on GitHub."""
        # Phase 1: Post comment and update labels via GitHub API
        return True

    async def add_to_queue(self, item: WorkItem) -> bool:
        """Add a work item to the queue via GitHub labels."""
        # Logic: Add 'agent:queued' label to the issue via GH API
        return True


# --- Dependency Injection ---


def get_queue() -> ITaskQueue:
    """Provide the task queue implementation (Phase 1: GitHub Issues)."""
    token = os.getenv("GITHUB_TOKEN", "")
    return GitHubIssuesQueue(token=token)


# --- Webhook Signature Verification ---


def _get_webhook_secret() -> bytes:
    """Retrieve the webhook secret from environment."""
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    return secret.encode("utf-8")


async def verify_signature(request: Request, x_hub_signature_256: str | None = Header(None)) -> None:
    """Verify the GitHub webhook HMAC SHA256 signature."""
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 missing")

    body = await request.body()
    secret = _get_webhook_secret()
    signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")


# --- Endpoints ---


@app.post("/webhooks/github", dependencies=[Depends(verify_signature)])
async def handle_github_webhook(request: Request, queue: ITaskQueue = Depends(get_queue)) -> dict:
    """Handle incoming GitHub webhook events and triage into work items."""
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "")

    # Triage Logic: Map GH Events to Unified Work Items
    if event_type == "issues" and payload.get("action") == "opened":
        issue = payload["issue"]
        labels = [label["name"] for label in issue.get("labels", [])]

        # Check if it matches an OS-APOW template
        if "[Application Plan]" in issue.get("title", "") or "agent:plan" in labels:
            task_type = TaskType.PLAN
        elif "bug" in labels:
            task_type = TaskType.FIX
        else:
            task_type = TaskType.IMPLEMENT

        work_item = WorkItem(
            id=str(issue["number"]),
            source_url=issue.get("html_url", ""),
            context_body=issue.get("body") or "",
            target_repo_slug=payload["repository"]["full_name"],
            task_type=task_type,
            metadata={"raw_payload": payload},
        )
        await queue.add_to_queue(work_item)
        return {"status": "accepted", "item_id": work_item.id}

    return {"status": "ignored", "reason": "No actionable OS-APOW event mapping found"}


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "online", "system": "OS-APOW Notifier"}


if __name__ == "__main__":
    import uvicorn

    # In dev, run with: uv run uvicorn src.notifier_service:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
