# Architecture Overview - workflow-orchestration-queue (OS-APOW)

## Executive Summary

workflow-orchestration-queue represents a paradigm shift from **Interactive AI Coding** to **Headless Agentic Orchestration**. The system transforms standard project management artifacts (GitHub Issues) into "Execution Orders" autonomously fulfilled by specialized AI agents.

The system is **Self-Bootstrapping**: once the "Sentinel" is active, the system uses its own orchestration capabilities to refine its components, effectively allowing the AI to "build its own house."

---

## System Architecture

### Four Conceptual Pillars

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OS-APOW SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐         ┌──────────────┐
     │   THE EAR    │         │  THE STATE   │
     │  (Notifier)  │────────▶│   (Queue)    │
     │   FastAPI    │         │ GitHub Issues│
     └──────────────┘         └──────────────┘
            │                        │
            │                        │
            ▼                        ▼
     ┌──────────────────────────────────────┐
     │           THE BRAIN (Sentinel)        │
     │     Background Polling Service        │
     │   Shell-Bridge Dispatch Protocol      │
     └──────────────────────────────────────┘
                         │
                         ▼
     ┌──────────────────────────────────────┐
     │          THE HANDS (Worker)           │
     │      Isolated DevContainer            │
     │    Opencode + LLM Agent Runtime       │
     └──────────────────────────────────────┘
```

---

## Component Details

### 1. The Ear (Work Event Notifier)

**Technology**: Python 3.12, FastAPI, Pydantic

**Role**: Primary gateway for external stimuli and asynchronous triggers

**Responsibilities**:
- **Secure Webhook Ingestion**: Hardened endpoint for GitHub events (issues, issue_comment, pull_request)
- **Cryptographic Verification**: HMAC SHA256 validation against `WEBHOOK_SECRET`
- **Intelligent Event Triage**: Parse payloads into unified `WorkItem` objects
- **Queue Initialization**: Apply `agent:queued` label via GitHub REST API

**Security Model**:
- Rejects requests with invalid/missing `X-Hub-Signature-256`
- Prevents "Prompt Injection via Webhook" attacks

**Endpoint**: `/webhooks/github`

---

### 2. The State (Work Queue)

**Technology**: GitHub Issues, Labels, Milestones

**Philosophy**: "Markdown as a Database"

**Rationale**:
- World-class audit logs
- Transparent versioning of requirements
- Out-of-the-box UI for human supervision
- Real-time "intervention-via-commenting" capability

**State Machine (Label Logic)**:

```
┌─────────────┐     Claim      ┌──────────────┐
│ agent:      │───────────────▶│ agent:       │
│ queued      │                │ in-progress  │
└─────────────┘                └──────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
            │ agent:      │  │ agent:      │  │ agent:      │
            │ success     │  │ error       │  │ infra-      │
            │             │  │             │  │ failure     │
            └─────────────┘  └─────────────┘  └─────────────┘
```

**Special States**:
- `agent:reconciling`: Recovery loop for "zombie" tasks (no updates > 15 min)

**Concurrency Control**: GitHub "Assignees" as distributed lock semaphore

---

### 3. The Brain (Sentinel Orchestrator)

**Technology**: Python (Async), PowerShell Core, Docker CLI

**Role**: Persistent supervisor managing Worker lifecycle and mapping intent to shell commands

**Lifecycle**:

```
┌──────────────────────────────────────────────────────────────┐
│                    SENTINEL LIFECYCLE                         │
└──────────────────────────────────────────────────────────────┘

1. POLLING DISCOVERY (every 60s)
   │
   ▼
2. AUTH SYNCHRONIZATION (scripts/gh-auth.ps1)
   │
   ▼
3. SHELL-BRIDGE PROTOCOL
   │
   ├──▶ ./scripts/devcontainer-opencode.sh up
   │    (Provision Docker network/volumes)
   │
   ├──▶ ./scripts/devcontainer-opencode.sh start
   │    (Launch opencode-server in DevContainer)
   │
   └──▶ ./scripts/devcontainer-opencode.sh prompt "{instruction}"
        (Dispatch AI workflow)
   │
   ▼
4. TELEMETRY & REPORTING
   (Heartbeat comments, log capture, status updates)
```

**Exit Code Protocol**:
- Exit 0: Success
- Exit 1-10: Infrastructure Error (retry or escalate)
- Exit 11+: Logic/Agent Error (requires human intervention)

**Workflow Mapping**:
| Issue Type | Workflow Module |
|------------|-----------------|
| PLAN | `create-app-plan.md` |
| IMPLEMENT | `perform-task.md` |
| BUGFIX | `recover-from-error.md` |

---

### 4. The Hands (Opencode Worker)

**Technology**: opencode-server CLI, LLM Core (GLM-5), DevContainer

**Environment**: High-fidelity DevContainer from template repository

**Capabilities**:
- **Contextual Awareness**: Vector-indexed codebase view via `update-remote-indices.ps1`
- **Instructional Logic**: Executes `.md` workflow modules from `/local_ai_instruction_modules/`
- **Verification**: Runs local test suites before PR submission

**Isolation**:
- Dedicated Docker network (no host subnet access)
- Resource limits (2 CPUs, 4GB RAM)
- Ephemeral credentials (destroyed on exit)

---

## Data Flow (Happy Path)

```
1. STIMULUS
   User opens GitHub Issue with [Application Plan] template
   │
   ▼
2. NOTIFICATION
   GitHub Webhook → Notifier (FastAPI)
   │
   ▼
3. TRIAGE
   Notifier validates signature
   Confirms title pattern
   Adds agent:queued label
   │
   ▼
4. CLAIM
   Sentinel poller detects queued issue
   Assigns issue to Agent account
   Updates label to agent:in-progress
   │
   ▼
5. SYNC
   Sentinel runs git clone/pull on target repo
   │
   ▼
6. ENVIRONMENT CHECK
   Sentinel executes devcontainer-opencode.sh up
   │
   ▼
7. DISPATCH
   Sentinel sends prompt with workflow instruction
   │
   ▼
8. EXECUTION
   Worker (Opencode) reads issue, analyzes tech stack
   Creates child issues, generates code, runs tests
   │
   ▼
9. FINALIZE
   Worker posts "Execution Complete" comment
   Sentinel detects exit code
   Removes in-progress label
   Adds agent:success label
```

---

## Key Architectural Decisions (ADRs)

### ADR-001: Standardized Shell-Bridge Execution
- **Decision**: Orchestrator interacts with agentic environment exclusively via `./scripts/devcontainer-opencode.sh`
- **Rationale**: Prevents "Configuration Drift" - agent environment identical to local developer
- **Consequence**: Python code focuses on logic/state; Shell handles container orchestration

### ADR-002: Polling-First Resiliency Model
- **Decision**: Sentinel uses polling as primary discovery; Webhooks are optimization
- **Rationale**: Webhooks are "fire and forget" - lost if server is down. Polling ensures "State Reconciliation" on restart
- **Consequence**: System inherently self-healing against server downtime

### ADR-003: Provider-Agnostic Interface Layer
- **Decision**: Queue interactions abstracted behind `ITaskQueue` interface (Strategy Pattern)
- **Rationale**: Enables future support for Linear, Notion, or custom queues without Orchestrator rewrite
- **Interface Methods**: `fetch_queued()`, `claim_task()`, `update_progress()`, `finish_task()`

---

## Security Architecture

### Network Isolation
```
┌─────────────────────────────────────────────────────────────┐
│                      HOST SERVER                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  Sentinel   │    │  Notifier   │    │   Other     │      │
│  │  Service    │    │  Service    │    │  Services   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                  │                   │             │
│         └──────────────────┼───────────────────┘             │
│                            │                                 │
│                     Host Network                             │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐              │
│         │        ISOLATED BRIDGE NETWORK       │              │
│         │    ┌─────────────────────────┐      │              │
│         │    │     Worker Container    │      │              │
│         │    │   (No host subnet access)│     │              │
│         │    └─────────────────────────┘      │              │
│         │              │ Internet only        │              │
│         └──────────────┼──────────────────────┘              │
│                        │                                     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                    Internet
```

### Credential Flow
```
┌─────────────────┐
│  Sentinel       │
│  (Host)         │
│                 │
│  GITHUB_TOKEN   │
│       │         │
│       ▼         │
│  Generate       │
│  Installation   │
│  Token          │
│       │         │
│       ▼         │
│  Inject as      │
│  ENV VAR        │
│  (in-memory)    │
└─────────────────┘
        │
        │ Docker Run
        ▼
┌─────────────────┐
│  Worker         │
│  (Container)    │
│                 │
│  ENV: TOKEN     │──────▶ Used for git ops
│  (destroyed     │        and API calls
│   on exit)      │
└─────────────────┘
```

### Log Scrubbing Pipeline
```
Raw Worker Output
       │
       ▼
┌─────────────────┐
│  Regex Scrubber │
│  - Remove tokens│
│  - Remove IPs   │
│  - Remove secrets│
└─────────────────┘
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌─────────────────┐  ┌─────────────────┐
│  Public Log     │  │  Black Box Log  │
│  (GitHub Issue  │  │  (Encrypted,    │
│   Comments)     │  │   local only)   │
└─────────────────┘  └─────────────────┘
```

---

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
│   │   └── github_events.py     # GitHub webhook payload schemas
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

## Self-Bootstrapping Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│              SELF-BOOTSTRAPPING EVOLUTION                        │
└─────────────────────────────────────────────────────────────────┘

Stage 0: SEEDING
├── Developer manually clones template repository
├── Adds plan documents to /docs
└── Configures environment variables

Stage 1: MANUAL LAUNCH
├── Developer runs devcontainer-opencode.sh up
└── Initializes worker environment

Stage 2: PROJECT SETUP
├── Developer runs orchestrate-project-setup workflow
├── Agent indexes repository
└── Configures notifier/sentinel skeletons

Stage 3: HANDOVER
├── Developer starts sentinel.py on host
├── From this point: human interacts ONLY via GitHub issues
└── AI builds remaining features (Phase 2, 3) autonomously
```

---

*Document created as part of the create-app-plan assignment*
*Repository: intel-agency/workflow-orchestration-queue-echo19*
