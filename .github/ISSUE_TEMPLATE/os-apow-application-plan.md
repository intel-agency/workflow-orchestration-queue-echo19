# OS-APOW (workflow-orchestration-queue) – Complete Implementation

## Overview

**workflow-orchestration-queue (OS-APOW)** is a groundbreaking headless agentic orchestration platform that transforms standard project management artifacts (GitHub Issues, Epics, Kanban movements) into automated Execution Orders. It shifts AI from a passive co-pilot role to an autonomous background production service capable of multi-step, specification-driven task fulfillment without human intervention.

**Problem Solved**: Traditional AI development tools require continuous human-in-the-loop interaction. OS-APOW eliminates this dependency, enabling "Zero-Touch Construction" where a user opens a single Specification Issue and receives a functional, test-passed branch and PR.

**Key Documents**:
- [Implementation Specification v1](../plan_docs/OS-APOW%20Implementation%20Specification%20v1.md)
- [Development Plan v4](../plan_docs/OS-APOW%20Development%20Plan%20v4.md)
- [Architecture Guide v3](../plan_docs/OS-APOW%20Architecture%20Guide%20v3.md)
- [Technology Stack](../plan_docs/tech-stack.md)
- [Architecture Overview](../plan_docs/architecture.md)

## Goals

- **Zero-Touch Construction**: User opens an issue → system delivers verified PR without human prompts
- **Self-Bootstrapping Evolution**: System builds itself using its own orchestration capabilities
- **State Visibility**: All state in GitHub for transparency and auditability
- **Polling-First Resiliency**: Self-healing after server restarts or network failures

## Technology Stack

- **Language**: Python 3.12+
- **Web Framework**: FastAPI with Uvicorn ASGI server
- **Data Validation**: Pydantic
- **HTTP Client**: HTTPX (async)
- **Package Manager**: uv (Rust-based, high-speed)
- **Containerization**: Docker / DevContainers
- **Shell Scripts**: PowerShell Core (pwsh) / Bash
- **AI Runtime**: opencode CLI with ZhipuAI GLM-5 models
- **State Store**: GitHub Issues (Markdown as a Database)
- **Security**: HMAC SHA256 webhook validation

## Application Features

- **Secure Webhook Ingestion**: Hardened endpoint with HMAC SHA256 signature validation
- **Intelligent Triaging**: Automatic detection of issue templates and dynamic queue prioritization
- **Resilient Task Polling**: Polling-first discovery with jittered exponential backoff
- **Concurrency Control**: GitHub Assignees as distributed lock semaphore
- **Shell-Bridge Execution**: Reproducible DevContainer environments via shell scripts
- **Hierarchical Task Delegation**: Architect Sub-Agent decomposes Epics into child tasks
- **Self-Healing Loops**: Automatic recovery from "zombie" tasks and stalled workflows

## System Architecture

### Core Services

1. **The Ear (Work Event Notifier)** — FastAPI webhook receiver for secure event ingestion and triage
2. **The State (Work Queue)** — GitHub Issues as database with label-based state machine
3. **The Brain (Sentinel Orchestrator)** — Background polling service managing worker lifecycle
4. **The Hands (Opencode Worker)** — Isolated DevContainer executing AI-driven workflows

### Key Features (system-level)

- **Markdown as a Database**: Perfect auditability via GitHub UI
- **Script-First Integration**: Shell bridge ensures environment parity with human developers
- **Provider-Agnostic Interfaces**: `ITaskQueue` abstraction enables future provider swapping

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # uv dependencies and metadata
├── uv.lock                      # Deterministic lockfile
├── src/                         # Main application source
│   ├── notifier_service.py      # FastAPI webhook ingestion
│   ├── orchestrator_sentinel.py # Background polling/dispatch
│   ├── models/                  # Pydantic data schemas
│   │   ├── work_item.py         # WorkItem, Status, Types
│   │   └── github_events.py     # GitHub webhook schemas
│   └── interfaces/              # Abstract Base Classes
│       └── i_task_queue.py      # ITaskQueue interface
├── scripts/                     # Shell Bridge layer
│   ├── devcontainer-opencode.sh # Core orchestrator script
│   ├── gh-auth.ps1              # GitHub App auth utility
│   └── update-remote-indices.ps1# Vector index sync
├── local_ai_instruction_modules/# Decoupled Markdown workflows
│   ├── create-app-plan.md       # Application planning prompts
│   ├── perform-task.md          # Feature implementation
│   └── analyze-bug.md           # Bug analysis and fixes
└── docs/                        # Architecture and user docs
```

---

## Implementation Plan

### Phase 0: Seeding & Bootstrapping ✅ COMPLETE

*This phase was completed manually during repository initialization.*

- [x] 0.1. Repository cloned from template (`workflow-orchestration-queue-echo19`)
- [x] 0.2. Plan documents seeded in `plan_docs/` directory
- [x] 0.3. DevContainer environment initialized
- [x] 0.4. Project setup workflow executed

---

### Phase 1: The Sentinel (MVP)

*Milestone: [Phase 1: The Sentinel (MVP)](https://github.com/intel-agency/workflow-orchestration-queue-echo19/milestone/1)*

**Goal**: Establish a persistent background service that detects work orders via GitHub Labels and triggers the devcontainer-opencode.sh infrastructure.

#### Story 1: Standardized Work Item Interface
- [ ] 1.1.1. Create `models/work_item.py` with Pydantic `WorkItem` model
  - Fields: `id`, `source_url`, `context_body`, `target_repo_slug`, `task_type` (Enum), `status` (Enum), `metadata`, `node_id`
- [ ] 1.1.2. Create `models/github_events.py` with GitHub webhook payload schemas
- [ ] 1.1.3. Create `interfaces/i_task_queue.py` with `ITaskQueue` abstract base class
  - Methods: `fetch_queued_items()`, `update_item_status()`
- [ ] 1.1.4. Implement `GitHubIssueQueue` class mapping GH REST API calls to interfaces

#### Story 2: The Resilient Polling Engine
- [ ] 1.2.1. Create `orchestrator_sentinel.py` as async background service
- [ ] 1.2.2. Implement polling loop with 60-second configurable interval
- [ ] 1.2.3. Add jittered exponential backoff for rate limit handling
- [ ] 1.2.4. Integrate with `scripts/gh-auth.ps1` for token management
- [ ] 1.2.5. Add structured logging with `SENTINEL_ID` correlation

#### Story 3: Shell-Bridge Dispatcher
- [ ] 1.3.1. Implement `run_shell_command()` async wrapper
- [ ] 1.3.2. Add environment check via `devcontainer-opencode.sh up`
- [ ] 1.3.3. Implement prompt dispatch via `devcontainer-opencode.sh prompt`
- [ ] 1.3.4. Capture stdout/stderr to JSONL log files
- [ ] 1.3.5. Handle non-zero exit codes with error state transitions

#### Story 4: Automated Status Feedback
- [ ] 1.4.1. Implement label transitions: `agent:queued` → `agent:in-progress` → terminal state
- [ ] 1.4.2. Add claim comment with Sentinel ID and timestamp
- [ ] 1.4.3. Implement heartbeat comments for long-running tasks (>5 min)
- [ ] 1.4.4. Add contextual error labeling (`agent:infra-failure` vs `agent:error`)

#### Story 5: Unique Instance Identification
- [ ] 1.5.1. Generate or accept `SENTINEL_ID` on startup
- [ ] 1.5.2. Include `SENTINEL_ID` in all log entries and GitHub comments
- [ ] 1.5.3. Support environment variable override for multi-node deployments

#### Story 6: Cost Guardrails & Resource Safety
- [ ] 1.6.1. Implement LLM usage tracking via `credits_used` file
- [ ] 1.6.2. Add daily budget threshold check
- [ ] 1.6.3. Auto-shutdown and `agent:stalled-budget` labeling when exceeded

---

### Phase 2: The Ear (Webhook Automation)

*Milestone: [Phase 2: The Ear (Webhook Automation)](https://github.com/intel-agency/workflow-orchestration-queue-echo19/milestone/3)*

**Goal**: Implement a FastAPI service for sub-second task ingestion and automated template validation.

#### Story 1: Hardened FastAPI Webhook Receiver
- [ ] 2.1.1. Create `notifier_service.py` with FastAPI application
- [ ] 2.1.2. Implement HMAC SHA256 signature validation
- [ ] 2.1.3. Add `/webhooks/github` endpoint with 202 Accepted response
- [ ] 2.1.4. Configure uv dependency management

#### Story 2: Intelligent Template Triaging
- [ ] 2.2.1. Parse issue body and labels for template detection
- [ ] 2.2.2. Map detected patterns to `WorkItemType` enum
- [ ] 2.2.3. Auto-apply `agent:queued` label via GitHub API

#### Story 3: Local-to-Cloud Tunneling (Dev Mode)
- [ ] 2.3.1. Create `start_dev_notifier.sh` script
- [ ] 2.3.2. Integrate ngrok/tailscale tunnel support
- [ ] 2.3.3. Auto-log webhook URL for GitHub App configuration

---

### Phase 3: Deep Orchestration (Planning)

*Milestone: [Phase 3: Deep Orchestration](https://github.com/intel-agency/workflow-orchestration-queue-echo19/milestone/2)*

**Goal**: Upgrade from simple "Prompt Passing" to high-level reasoning with hierarchical decomposition and self-correction.

#### Story 1: The Architect Sub-Agent
- [ ] 3.1.1. Implement Epic decomposition logic
- [ ] 3.1.2. Create child issues with "Related To" links
- [ ] 3.1.3. Define dependency chains between Epics
- [ ] 3.1.4. Block child issues until dependencies complete

#### Story 2: Autonomous Bug Correction Loop
- [ ] 3.2.1. Detect `pull_request_review_comment` events
- [ ] 3.2.2. Transition issue from `agent:success` back to `agent:queued`
- [ ] 3.2.3. Include reviewer feedback in worker context

#### Story 3: Proactive Workspace Indexing
- [ ] 3.3.1. Trigger `update-remote-indices.ps1` after clone
- [ ] 3.3.2. Verify index presence before generation tasks

---

## Mandatory Requirements Implementation

### Testing & Quality Assurance
- [ ] Unit tests — coverage target: 80%+
- [ ] Integration tests for webhook ingestion and queue operations
- [ ] E2E tests for full workflow execution
- [ ] Performance/load tests for polling engine
- [ ] Automated tests in CI pipeline

### Documentation & UX
- [ ] Comprehensive README with setup instructions
- [ ] API documentation (auto-generated via FastAPI/Swagger)
- [ ] Inline code documentation (Sphinx/Google docstrings)
- [ ] Troubleshooting guide for common issues
- [ ] Instructional logic modules documentation

### Build & Distribution
- [ ] Build scripts for container images
- [ ] Containerization support (Docker, DevContainers)
- [ ] Release pipeline with versioned tags

### Infrastructure & DevOps
- [ ] CI/CD workflows (build, test, scan, publish)
- [ ] Static analysis and security scanning
- [ ] Performance monitoring and alerting

---

## Acceptance Criteria

### Task Claiming
- [ ] Given a valid GitHub issue labeled with `agent:queued`, when the Sentinel executes its polling cycle, then the Sentinel must successfully assign itself as the owner, remove `agent:queued`, apply `agent:in-progress`, and log the transition without errors.

### Infrastructure Failure Handling
- [ ] Given a task that is `agent:in-progress`, when `devcontainer-opencode.sh up` exits with non-zero code, then the orchestrator must label the issue `agent:infra-failure` and post the last 50 lines of stderr as a comment.

### Successful Execution & Delivery
- [ ] Given a successful execution inside the DevContainer, the system must detect zero exit code, push changes to a new remote branch, generate a formatted Pull Request linking to the original issue, and label the parent issue `agent:success`.

### Security & Payload Rejection
- [ ] Given an HTTP POST to the webhook endpoint with invalid/missing signature, the Notifier must reject with HTTP 401 prior to any JSON parsing.

---

## Risk Mitigation Strategies

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub API Rate Limiting | High | Use GitHub App Installation tokens (5,000 req/hr); implement aggressive local caching; use long-polling intervals |
| LLM "Looping" / Hallucination | High | Implement `max_steps` timeout in opencode config; cost guardrails; `agent:retries` counter (stall if >3) |
| Concurrency Collisions | Medium | Use GitHub "Assignee" feature as distributed lock; Sentinel must successfully assign before status change |
| Container Drift | Medium | Run `docker-compose down && up` between major Epics for clean environment |
| Security Injection | Medium | Strict HMAC signature validation; worker denied access to host `.env` files |

---

## Timeline Estimate

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 0: Seeding & Bootstrapping | 1 day | ✅ Complete |
| Phase 1: The Sentinel (MVP) | 2-3 weeks | 🎯 Active |
| Phase 2: The Ear (Webhook Automation) | 1-2 weeks | Upcoming |
| Phase 3: Deep Orchestration | 2-3 weeks | Upcoming |
| **Total** | **6-9 weeks** | |

---

## Success Metrics

- **Zero-Touch Rate**: Percentage of issues resolved without human intervention
- **Time-to-PR**: Average time from issue creation to Pull Request submission
- **Self-Healing Rate**: Percentage of stalled tasks automatically recovered
- **Cost Efficiency**: LLM token usage per completed task
- **Auditability**: 100% of state transitions visible in GitHub UI

---

## Repository Branch

Target branch for implementation: `dynamic-workflow-project-setup`

---

## Implementation Notes

### Key Assumptions
- The template repository (`workflow-orchestration-queue-echo19`) provides the foundational Docker/DevContainer configs
- The `devcontainer-opencode.sh` shell bridge handles all Docker orchestration
- GitHub App authentication is configured with appropriate scopes

### Adaptations from Plan Docs
- Python/FastAPI stack (not .NET) - all examples use Python ecosystem
- `uv` package manager for speed (not pip or poetry)
- DevContainer-based execution (not local development)

### References
- [Architecture Guide v3](../plan_docs/OS-APOW%20Architecture%20Guide%20v3.md) - System diagrams and ADRs
- [Development Plan v4](../plan_docs/OS-APOW%20Development%20Plan%20v4.md) - Phased roadmap and user stories
- [Implementation Specification v1](../plan_docs/OS-APOW%20Implementation%20Specification%20v1.md) - Detailed requirements
- [Code Samples](../plan_docs/) - `notifier_service.py`, `orchestrator_sentinel.py` reference implementations
