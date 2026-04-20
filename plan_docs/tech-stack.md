# Technology Stack - workflow-orchestration-queue (OS-APOW)

## Overview

This document defines the complete technology stack for the workflow-orchestration-queue system, a headless agentic orchestration platform that transforms GitHub Issues into automated Execution Orders.

---

## Primary Languages

### Python 3.12+
- **Purpose**: Core application language for Orchestrator, API Webhook receiver, and all system logic
- **Rationale**: Optimal blend of asynchronous capabilities and robust text processing
- **Features Used**: Async/await, improved error messages, performance enhancements

### PowerShell Core (pwsh) / Bash
- **Purpose**: Shell Bridge Scripts, Auth synchronization, cross-platform CLI interactions
- **Rationale**: Maximum compatibility across Linux and Windows host environments
- **Scope**: Exclusively for shell scripts, not application logic

---

## Web Framework & Server

### FastAPI
- **Purpose**: High-performance async web framework for the Webhook Notifier ("The Ear")
- **Version**: Latest stable
- **Rationale**: 
  - Native Pydantic integration
  - Automatic OpenAPI/Swagger generation
  - Unparalleled async performance
- **Key Features**: 
  - Dependency injection
  - Request validation
  - Automatic documentation at `/docs`

### Uvicorn
- **Purpose**: ASGI web server implementation
- **Rationale**: Lightning-fast ASGI server for production deployment
- **Usage**: Serves the FastAPI application

---

## Data Validation & Models

### Pydantic v2
- **Purpose**: Strict data validation, settings management, schema definitions
- **Rationale**: Type-safe data models with runtime validation; v2 brings Rust-based performance
- **Usage**:
  - WorkItem models
  - TaskType enums
  - WorkItemStatus enums
  - Configuration management

---

## HTTP Client

### HTTPX
- **Purpose**: Asynchronous HTTP client for GitHub API interactions
- **Rationale**: 
  - Fully async (unlike `requests`)
  - Non-blocking GitHub REST API calls
  - Significantly improved throughput
- **Usage**: All external HTTP communications

---

## Package Management

### uv
- **Purpose**: Python package installer and dependency resolver
- **Version**: 0.10.9+
- **Rationale**:
  - Written in Rust - orders of magnitude faster than pip/poetry
  - Vastly accelerated DevContainer build times
  - Deterministic lockfiles (`uv.lock`)
- **Configuration**: `pyproject.toml`

---

## Containerization & Infrastructure

### Docker
- **Purpose**: Core worker execution engine
- **Features**:
  - Sandboxing and isolation
  - Environment consistency
  - Lifecycle hooks for LLM agents
- **Key Configurations**:
  - Network isolation (dedicated bridge network)
  - Resource constraints (2 CPUs, 4GB RAM)
  - Ephemeral credentials

### DevContainers
- **Purpose**: Reproducible development and execution environments
- **Rationale**: 
  - Bit-for-bit identical environments for AI and humans
  - Eliminates "it works on my machine" discrepancies
- **Configuration**: `devcontainer.json`, `Dockerfile`

### Docker Compose
- **Purpose**: Multi-container orchestration
- **Usage**: 
  - Complex multi-service needs (web app + PostgreSQL)
  - Environment reset between tasks (`docker-compose down -v && up --build`)

---

## AI/LLM Runtime

### opencode CLI
- **Purpose**: AI agent runtime
- **Version**: 1.2.24+
- **Usage**: Executes agents defined in `.opencode/agents/` with MCP server support
- **Command**: `opencode --model zai-coding-plan/glm-5 --agent Orchestrator`

### ZhipuAI GLM Models
- **Purpose**: Primary LLM backend
- **Model**: GLM-5
- **Authentication**: `ZHIPU_API_KEY`

### MCP Servers
- **Purpose**: Model Context Protocol servers for extended capabilities
- **Servers**:
  - `@modelcontextprotocol/server-sequential-thinking` - Step-by-step reasoning
  - `@modelcontextprotocol/server-memory` - Knowledge graph persistence

---

## State Management

### GitHub REST API
- **Purpose**: Primary API for issue/label/PR operations
- **Usage**: Task claiming, status updates, comment posting
- **Authentication**: GitHub App Installation tokens (5,000 req/hr)

### GitHub GraphQL API
- **Purpose**: Efficient queries for complex data fetching (e.g., issue relationships, project board items)
- **Usage**: Batch queries, nested data retrieval

### GitHub Apps
- **Purpose**: Authentication and authorization model
- **Features**:
  - Installation tokens with fine-grained permissions
  - Webhook event subscriptions (issues, issue_comment, pull_request)
  - HMAC secret for payload verification

### GitHub Webhooks
- **Purpose**: Event-driven triggers for real-time task ingestion
- **Events Subscribed**: `issues`, `issue_comment`, `pull_request`, `pull_request_review`
- **Security**: HMAC SHA256 signature validation on all incoming payloads

### GitHub Issues & Labels
- **Purpose**: Primary database ("Markdown as a Database")
- **Rationale**:
  - World-class audit logs
  - Transparent versioning
  - Out-of-the-box UI for human supervision
- **State Labels**:
  - `agent:queued` - Awaiting Sentinel
  - `agent:in-progress` - Claimed by Sentinel
  - `agent:success` - Terminal success
  - `agent:error` - Technical failure
  - `agent:infra-failure` - Infrastructure failure

---

## Logging & Observability

### Python Logging
- **Handlers**:
  - `StreamHandler` - Console output
  - `FileHandler` - Rotating disk storage
- **Format**: Structured JSON lines with `SENTINEL_ID` correlation

### Log Types
- **Worker Output (Black Box)**: Encrypted local files for forensic analysis
- **Public Telemetry**: Sanitized "Heartbeat" comments on GitHub Issues
- **Service Logging**: Structured logs from Sentinel and Notifier

---

## Security

### HMAC SHA256
- **Purpose**: Webhook signature validation
- **Usage**: `X-Hub-Signature-256` header verification
- **Rationale**: Prevents prompt injection and unauthorized execution

### Credential Management
- **GitHub Installation Tokens**: Dynamic generation, ephemeral injection
- **Scrubbing**: Regex-based credential removal from public logs
- **Least Privilege**: Minimal token scopes

---

## Testing

### pytest
- **Purpose**: Primary testing framework for all Python components
- **Rationale**: Industry-standard Python testing with powerful fixture system
- **Usage**: Unit tests, integration tests, parametrized test cases

### pytest-asyncio
- **Purpose**: Async test support for pytest
- **Rationale**: Essential for testing the async Sentinel polling loop and FastAPI endpoints
- **Usage**: `@pytest.mark.asyncio` decorators for async test functions

### httpx (Test Client)
- **Purpose**: Async HTTP test client for FastAPI application testing
- **Rationale**: Direct ASGI test client support — test webhook endpoints without running a server
- **Usage**: `httpx.AsyncClient(app=app, base_url="http://test")` for endpoint testing

### Test Strategy
| Test Type | Tool | Scope |
|-----------|------|-------|
| Unit Tests | pytest + pytest-asyncio | Models, interfaces, business logic |
| API Tests | httpx test client | FastAPI webhook endpoints |
| Integration Tests | pytest + httpx (live) | GitHub API interactions |
| E2E Tests | pytest + subprocess | Full workflow execution |
| Performance | pytest-benchmark | Polling engine throughput |

**Coverage Target**: 80%+

---

## Linting & Code Quality

### ruff
- **Purpose**: Fast Python linter and formatter (Rust-based)
- **Rationale**: Replaces flake8, isort, and black with a single tool
- **Configuration**: `pyproject.toml` `[tool.ruff]` section
- **Usage**: 
  - Linting: `ruff check src/`
  - Formatting: `ruff format src/`
  - CI enforcement: `ruff check --no-fix`

### Type Checking
- **Tool**: mypy (optional, recommended)
- **Purpose**: Static type checking for Pydantic models and async code

### Code Quality Standards
- **Docstrings**: Sphinx/Google format for all public APIs
- **Line Length**: 120 characters (configurable via ruff)
- **Import Sorting**: Handled by ruff (replaces isort)
- **Complexity**: Max cyclomatic complexity of 10 per function

---

## Development Tools

### GitHub CLI (gh)
- **Purpose**: Repository, issue, and PR management
- **Authentication**: `GITHUB_TOKEN` environment variable

### Git
- **Purpose**: Version control
- **Branch Strategy**:
  - `main` - Production-ready releases
  - `develop` - Integration and staging

---

## Summary Table

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.12+ | Core application |
| Shell | pwsh/Bash | - | Bridge scripts |
| Web Framework | FastAPI | Latest | Webhook receiver |
| ASGI Server | Uvicorn | Latest | Production server |
| Validation | Pydantic v2 | Latest | Data models |
| HTTP Client | HTTPX | Latest | Async API calls |
| Package Manager | uv | 0.10.9+ | Dependency management |
| Containerization | Docker | Latest | Worker isolation |
| Dev Environment | DevContainers | Latest | Reproducible envs |
| AI Runtime | opencode CLI | 1.2.24+ | Agent execution |
| LLM Backend | ZhipuAI GLM | GLM-5 | Language model |
| State Store | GitHub Issues | - | Task queue/database |
| Security | HMAC SHA256 | - | Webhook validation |
| Testing | pytest | Latest | Test framework |
| Async Testing | pytest-asyncio | Latest | Async test support |
| API Testing | httpx (test client) | Latest | FastAPI endpoint tests |
| Linting | ruff | Latest | Linter & formatter |
| Type Checking | mypy | Latest | Static type analysis |

---

*Document created as part of the create-app-plan assignment*
*Repository: intel-agency/workflow-orchestration-queue-echo19*
