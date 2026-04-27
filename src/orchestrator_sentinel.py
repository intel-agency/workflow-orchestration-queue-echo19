"""
OS-APOW Sentinel Orchestrator.

Implementation of Phase 1: Story 2 & 3.

This script acts as the 'Brain' of the OS-APOW system. It:
1. Polls GitHub for issues labeled 'agent:queued'.
2. Claims the task by updating labels and assigning the issue.
3. Manages the worker lifecycle via shell bridge scripts.
4. Reports progress and results back to GitHub.
"""

import asyncio
import logging
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI

from src.models.work_item import TaskType, WorkItem, WorkItemStatus

# --- Configuration from Environment ---

POLL_INTERVAL = int(os.getenv("SENTINEL_POLL_INTERVAL", "60"))
SENTINEL_ID = os.getenv("SENTINEL_ID", f"sentinel-{uuid.uuid4().hex[:8]}")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_ORG = os.getenv("GITHUB_ORG", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
SHELL_BRIDGE_PATH = "./scripts/devcontainer-opencode.sh"

# --- Structured Logging ---

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] {SENTINEL_ID} - %(message)s",
    handlers=[logging.FileHandler("sentinel.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("OS-APOW-Sentinel")


# --- Shell Bridge Interface ---


async def run_shell_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Invoke the local shell bridge (devcontainer-opencode.sh)."""
    try:
        logger.info(f"Executing Bridge: {' '.join(args)}")
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await process.communicate()

        return subprocess.CompletedProcess(
            args=args,
            returncode=process.returncode or 0,
            stdout=stdout_bytes.decode().strip() if stdout_bytes else "",
            stderr=stderr_bytes.decode().strip() if stderr_bytes else "",
        )
    except Exception as e:
        logger.error(f"Critical shell execution error: {e}")
        raise


# --- GitHub Queue Implementation ---


class GitHubQueue:
    """GitHub Issues-based task queue implementation."""

    def __init__(self, token: str, org: str, repo: str) -> None:
        self.token = token
        self.base_url = f"https://api.github.com/repos/{org}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def fetch_queued_tasks(self) -> list[WorkItem]:
        """Query GitHub for issues labeled 'agent:queued'."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/issues?labels=agent:queued&state=open"
            response = await client.get(url, headers=self.headers)

            if response.status_code != 200:
                logger.error(f"GitHub API connectivity error: {response.status_code}")
                return []

            issues = response.json()
            work_items: list[WorkItem] = []
            for issue in issues:
                labels = [label["name"] for label in issue.get("labels", [])]
                task_type = TaskType.IMPLEMENT
                if "agent:plan" in labels or "[Plan]" in issue.get("title", ""):
                    task_type = TaskType.PLAN
                elif "bug" in labels:
                    task_type = TaskType.FIX

                work_items.append(
                    WorkItem(
                        id=str(issue["id"]),
                        source_url=issue.get("html_url", ""),
                        context_body=issue.get("body") or "",
                        target_repo_slug=f"{GITHUB_ORG}/{GITHUB_REPO}",
                        task_type=task_type,
                        status=WorkItemStatus.QUEUED,
                        node_id=issue.get("node_id"),
                    )
                )
            return work_items

    async def claim_task(self, item: WorkItem) -> bool:
        """Lock the task using GitHub Assignees and update label to in-progress."""
        async with httpx.AsyncClient() as client:
            url_issue = f"{self.base_url}/issues/{item.id}"

            # 1. Update Labels (Remove queued, add in-progress)
            url_labels = f"{url_issue}/labels"
            try:
                await client.delete(f"{url_labels}/agent:queued", headers=self.headers)
            except Exception:
                pass
            await client.post(
                url_labels,
                json={"labels": ["agent:in-progress"]},
                headers=self.headers,
            )

            # 2. Post Claim Comment
            comment_url = f"{url_issue}/comments"
            msg = (
                f"Sentinel {SENTINEL_ID} has claimed this task.\n"
                f"- **Start Time:** {datetime.now(UTC).isoformat()}\n"
                f"- **Environment:** `devcontainer-opencode.sh` initializing..."
            )
            await client.post(comment_url, json={"body": msg}, headers=self.headers)

            logger.info(f"Successfully claimed Task #{item.id}")
            return True

    async def update_status(
        self,
        item: WorkItem,
        status: WorkItemStatus,
        comment: str | None = None,
    ) -> None:
        """Finalize the task state on GitHub with terminal labels and logs."""
        async with httpx.AsyncClient() as client:
            url_labels = f"{self.base_url}/issues/{item.id}/labels"

            # Cleanup transition label
            try:
                await client.delete(f"{url_labels}/agent:in-progress", headers=self.headers)
            except Exception:
                pass

            # Apply final status label
            label_map = {
                WorkItemStatus.SUCCESS: "agent:success",
                WorkItemStatus.ERROR: "agent:error",
                WorkItemStatus.INFRA_FAILURE: "agent:infra-failure",
            }
            label = label_map.get(status, "agent:error")
            await client.post(url_labels, json={"labels": [label]}, headers=self.headers)

            if comment:
                comment_url = f"{self.base_url}/issues/{item.id}/comments"
                await client.post(comment_url, json={"body": comment}, headers=self.headers)


# --- Orchestration Logic ---


class Sentinel:
    """Sentinel orchestrator managing worker lifecycle."""

    def __init__(self, queue: GitHubQueue) -> None:
        self.queue = queue

    async def process_task(self, item: WorkItem) -> None:
        """Process a single work item through the full lifecycle."""
        logger.info(f"Processing Task #{item.id}...")

        try:
            # Step 1: Initialize Infrastructure
            res_up = await run_shell_command([SHELL_BRIDGE_PATH, "up"])
            if res_up.returncode != 0:
                err = f"**Infrastructure Failure** during `up` stage:\n```\n{res_up.stderr}\n```"
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 2: Start Opencode Server
            res_start = await run_shell_command([SHELL_BRIDGE_PATH, "start"])
            if res_start.returncode != 0:
                err = f"**Infrastructure Failure** starting `opencode-server`:\n```\n{res_start.stderr}\n```"
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 3: Trigger Agent Workflow
            workflow_map: dict[TaskType, str] = {
                TaskType.PLAN: "create-app-plan.md",
                TaskType.IMPLEMENT: "perform-task.md",
                TaskType.FIX: "recover-from-error.md",
            }
            workflow = workflow_map.get(item.task_type, "perform-task.md")
            instruction = f"Execute workflow {workflow} for context: {item.source_url}"

            # This is the primary bridge call
            res_prompt = await run_shell_command([SHELL_BRIDGE_PATH, "prompt", instruction])

            # Step 4: Handle Completion
            if res_prompt.returncode == 0:
                success_msg = (
                    f"**Workflow Complete**\nSentinel successfully executed `{workflow}`. Please review Pull Requests."
                )
                await self.queue.update_status(item, WorkItemStatus.SUCCESS, success_msg)
            else:
                log_tail = res_prompt.stderr[-1500:] if res_prompt.stderr else "No error output captured."
                fail_msg = f"**Execution Error** during `{workflow}`:\n```\n...{log_tail}\n```"
                await self.queue.update_status(item, WorkItemStatus.ERROR, fail_msg)

        except Exception as e:
            logger.exception(f"Internal Sentinel Error on Task #{item.id}")
            await self.queue.update_status(
                item,
                WorkItemStatus.INFRA_FAILURE,
                f"Sentinel encountered an unhandled exception: {e}",
            )

    async def run_forever(self) -> None:
        """Main polling loop for the sentinel."""
        logger.info(f"Sentinel {SENTINEL_ID} entering polling loop (Interval: {POLL_INTERVAL}s)")

        while True:
            try:
                tasks = await self.queue.fetch_queued_tasks()
                if tasks:
                    logger.info(f"Found {len(tasks)} queued task(s).")
                    for task in tasks:
                        # Sequential processing for Phase 1 to prevent resource exhaustion
                        if await self.queue.claim_task(task):
                            await self.process_task(task)
                            break

            except Exception as e:
                logger.error(f"Polling cycle error: {e}")

            await asyncio.sleep(POLL_INTERVAL)


# --- FastAPI Health Endpoint ---

health_app = FastAPI(title="OS-APOW Sentinel", version="0.1.0")


@health_app.get("/health")
def health_check() -> dict:
    """Health check endpoint for the sentinel service."""
    return {"status": "online", "system": "OS-APOW Sentinel", "sentinel_id": SENTINEL_ID}


# --- Entry Point ---

if __name__ == "__main__":
    # Requirement Check
    env_vars = ["GITHUB_TOKEN", "GITHUB_ORG", "GITHUB_REPO"]
    missing = [v for v in env_vars if not os.getenv(v)]
    if missing:
        logger.error(f"Critical Error: Missing environment variables: {', '.join(missing)}")
        sys.exit(1)

    # Boot Sentinel
    gh_queue = GitHubQueue(GITHUB_TOKEN, GITHUB_ORG, GITHUB_REPO)
    sentinel = Sentinel(gh_queue)

    try:
        asyncio.run(sentinel.run_forever())
    except KeyboardInterrupt:
        logger.info("Sentinel shutting down gracefully.")
