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

### Pydantic
- **Purpose**: Strict data validation, settings management, schema definitions
- **Rationale**: Type-safe data models with runtime validation
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
| Validation | Pydantic | Latest | Data models |
| HTTP Client | HTTPX | Latest | Async API calls |
| Package Manager | uv | 0.10.9+ | Dependency management |
| Containerization | Docker | Latest | Worker isolation |
| Dev Environment | DevContainers | Latest | Reproducible envs |
| AI Runtime | opencode CLI | 1.2.24+ | Agent execution |
| LLM Backend | ZhipuAI GLM | GLM-5 | Language model |
| State Store | GitHub Issues | - | Task queue/database |
| Security | HMAC SHA256 | - | Webhook validation |

---

*Document created as part of the create-app-plan assignment*
*Repository: intel-agency/workflow-orchestration-queue-echo19*
