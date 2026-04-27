# OS-APOW: Opencode-Server Agent Workflow Orchestration

A headless agentic orchestration platform that transforms GitHub Issues into automated Execution Orders fulfilled by specialized AI agents.

## Architecture Overview

The system is built around four conceptual pillars:

```
┌──────────────┐         ┌──────────────┐
│   THE EAR    │         │  THE STATE   │
│  (Notifier)  │────────>│   (Queue)    │
│   FastAPI    │         │ GitHub Issues│
└──────────────┘         └──────────────┘
       │                        │
       ▼                        ▼
┌──────────────────────────────────────┐
│         THE BRAIN (Sentinel)         │
│    Background Polling Service        │
│   Shell-Bridge Dispatch Protocol     │
└──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        THE HANDS (Worker)            │
│    Isolated DevContainer             │
│  Opencode + LLM Agent Runtime        │
└──────────────────────────────────────┘
```

- **The Ear (Notifier):** FastAPI webhook receiver that ingests GitHub events, validates HMAC signatures, and triages into unified WorkItem objects.
- **The State (Queue):** GitHub Issues used as a task database ("Markdown as a Database") with label-based state management.
- **The Brain (Sentinel):** Async polling service that claims tasks, manages worker lifecycle, and reports results.
- **The Hands (Worker):** Isolated DevContainer executing AI agent workflows via the opencode CLI.

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Language | Python 3.12+ | Core application |
| Web Framework | FastAPI | Webhook receiver |
| ASGI Server | Uvicorn | Production server |
| Validation | Pydantic v2 | Data models |
| HTTP Client | HTTPX | Async API calls |
| Package Manager | uv | Dependency management |
| Containerization | Docker | Worker isolation |
| AI Runtime | opencode CLI | Agent execution |

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for worker execution)

### Install Dependencies

```bash
uv sync
```

### Environment Variables

Create a `.env` file (or set environment variables):

```bash
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_ORG=your_org
GITHUB_REPO=your_repo
```

## Running the Service

### Notifier (Webhook Receiver)

```bash
# Development with auto-reload
uv run uvicorn src.notifier_service:app --reload --port 8000

# Or via Docker Compose
docker compose up notifier
```

The notifier exposes:
- `POST /webhooks/github` - GitHub webhook endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger UI (auto-generated)

### Sentinel (Background Orchestrator)

```bash
# Direct execution
uv run python -m src.orchestrator_sentinel

# Via Docker Compose (uses sentinel profile)
docker compose --profile sentinel up sentinel
```

## Testing

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_work_item.py
```

## Code Quality

```bash
# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/

# Type check
uv run mypy src/
```

## Project Structure

```
src/
├── __init__.py
├── notifier_service.py       # FastAPI webhook receiver
├── orchestrator_sentinel.py  # Sentinel background orchestrator
├── models/
│   ├── __init__.py
│   ├── work_item.py          # WorkItem model, Status/TaskType enums
│   └── github_events.py      # GitHub webhook event schemas
└── interfaces/
    ├── __init__.py
    └── i_task_queue.py        # ITaskQueue abstract base class

tests/
├── __init__.py
├── conftest.py
├── test_work_item.py
└── test_github_events.py

plan_docs/                     # Reference design documents
scripts/                       # Shell bridge scripts
docs/                          # Architecture and user docs
```

## Documentation

- [Architecture Guide](plan_docs/architecture.md)
- [Tech Stack](plan_docs/tech-stack.md)
- [Implementation Specification](plan_docs/OS-APOW%20Implementation%20Specification%20v1.md)
- [OS-APOW Architecture Guide v3](plan_docs/OS-APOW%20Architecture%20Guide%20v3.md)
- [Development Plan v4](plan_docs/OS-APOW%20Development%20Plan%20v4.md)

## License

See [LICENSE](LICENSE) for details.
