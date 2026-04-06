# Workflow Execution Plan: project-setup

## 1. Overview

**Workflow Name:** project-setup  
**Workflow File:** `local_ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`  
**Project Name:** workflow-orchestration-queue (OS-APOW)  
**Total Assignments:** 6 main assignments + 3 event assignments  

**High-Level Summary:**  
This workflow initializes a fresh repository clone from the workflow-orchestration-queue-echo19 template, establishing the foundational structure for the OS-APOW (Opencode-Server Agent Workflow Orchestration) system. The system is designed to transform AI coding from interactive to autonomous/headless operation, using GitHub Issues as the primary task queue and state management system.

## 2. Project Context Summary

- **Repository:** intel-agency/workflow-orchestration-queue-echo19
- **Technology Stack:** Python 3.12+, FastAPI, Uvicorn, Pydantic, HTTPX, uv package manager, Docker/DevContainers
- **Architecture Pattern:** Event-driven, Polling-first with webhook optimization
- **Key Principle:** "Markdown as a Database" - all state stored in GitHub Issues/Labels for transparency
- **Current State:** Fresh template clone with plan documents seeded in plan_docs/
- **Critical Constraint:** All GitHub Actions must pin actions to specific commit SHAs (not version tags)
- **Security Requirements:** HMAC signature validation, credential scrubbing, network isolation

**Existing Plan Documents:**
- OS-APOW Development Plan v4.md - 4-phase roadmap (Seeding, Sentinel MVP, Ear/Webhook, Deep Orchestration)
- OS-APOW Architecture Guide v3.md - System architecture and ADRs
- OS-APOW Implementation Specification v1.md - Detailed requirements and specifications
- Sample implementation files: orchestrator_sentinel.py, notifier_service.py

## 3. Assignment Execution Plan

Assignments execute in the order:

### 3.1 init-existing-repository

| Field | Content |
|---|---|
| **Assignment** | `init-existing-repository`: Initiate Existing Repository |
| **Goal** | Initialize the repository by creating branch, importing configurations, and setting up GitHub Project |
| **Key Acceptance Criteria** | • New branch created first (dynamic-workflow-project-setup)<br>• Branch protection ruleset imported<br>• GitHub Project created and linked<br>• Labels imported from .github/.labels.json<br>• Workspace and devcontainer files renamed<br>• PR created (but not merged yet) |
| **Project-Specific Notes** | • Template already has .github/protected-branches_ruleset.json<br>• Must use GH_ORCHESTRATION_AGENT_TOKEN for ruleset import (requires admin:write scope)<br>• Sequential processing for Phase 1 to prevent resource exhaustion |
| **Prerequisites** | None - this is the first assignment |
| **Dependencies** | None |
| **Risks/Challenges** | • Ruleset may already exist (need idempotent check)<br>• GitHub Project creation may fail if permissions insufficient |
| **Events** | post-assignment-complete: validate-assignment-completion, report-progress |

### 3.2 create-app-plan

| Field | Content |
|---|---|
| **Assignment** | `create-app-plan`: Create Application Plan |
| **Goal** | Create comprehensive application plan documented as a GitHub issue |
| **Key Acceptance Criteria** | • Analyze existing plan_docs/<br>• Create tech-stack.md and architecture.md in plan_docs/<br>• Create GitHub issue using application-plan.md template<br>• Create milestones and link issues<br>• Add to GitHub Project with labels<br>• **PLANNING ONLY - no code implementation** |
| **Project-Specific Notes** | • Extensive planning docs already exist in plan_docs/<br>• Must synthesize existing docs (Development Plan v4, Architecture Guide v3, Implementation Spec v1)<br>• Project is OS-APOW (headless agentic orchestration)<br>• Must reference existing implementation files as examples |
| **Prerequisites** | init-existing-repository completed (branch exists) |
| **Dependencies** | Requires working branch from init-existing-repository |
| **Risks/Challenges** | • Existing plan docs may conflict with new tech-stack.md/architecture.md<br>• Must ensure alignment between existing and new artifacts |
| **Events** | pre-assignment-begin: gather-context<br>on-assignment-failure: recover-from-error<br>post-assignment-complete: report-progress |

### 3.3 create-project-structure

| Field | Content |
|---|---|
| **Assignment** | `create-project-structure`: Create Project Structure |
| **Goal** | Create actual project structure,**Key Acceptance Criteria** | • Solution/project structure created (Python-based)<br>• All project files and directories established<br>• Docker/DevContainer configs created<br>• CI/CD pipeline structure established<br>• Documentation structure created<br>• Repository summary created (.ai-repository-summary.md)<br>• Initial commit made |
| **Project-Specific Notes** | • **CRITICAL: This is Python 3.12+ project, NOT .NET**<br>• Uses FastAPI, Uvicorn, Pydantic, HTTPX, uv package manager<br>• Structure: pyproject.toml, uv.lock, src/, scripts/, local_ai_instruction_modules/, docs/<br>• When using `uv pip install -e .`, must COPY src/ before install<br>• Docker healthchecks must use Python stdlib, not curl |
| **Prerequisites** | create-app-plan completed (need plan reference) |
| **Dependencies** | Application plan issue for guidance |
| **Risks/Challenges** | • Risk of creating .NET structure instead of Python<br>• Docker healthcheck implementation must avoid curl<br>• Editable install ordering issue with uv |
| **Events** | None specific |

### 3.4 create-agents-md-file

| Field | Content |
|---|---|
| **Assignment** | `create-agents-md-file`: Create AGENTS.md File |
| **Goal** | Create AGENTS.md file at repository root for AI coding agent context |
| **Key Acceptance Criteria** | • AGENTS.md exists at repository root<br>• Contains project overview, setup commands, project structure<br>• All commands validated by running them<br>• File committed and pushed<br>• Stakeholder approval obtained |
| **Project-Specific Notes** | • Python project using uv package manager (not npm)<br>• Key commands: `uv sync`, `uv run uvicorn src.notifier_service:app --reload`, `uv run python src/orchestrator_sentinel.py`<br>• Test: `uv run pytest`<br>• Lint: `uv run ruff check .` |
| **Prerequisites** | create-project-structure completed |
| **Dependencies** | Project structure must exist to document commands |
| **Risks/Challenges** | • Commands must be tested before documenting<br>• Must align with actual Python project structure |
| **Events** | None specific |

### 3.5 debrief-and-document

| Field | Content |
|---|---|
| **Assignment** | `debrief-and-document`: Debrief and Document Learnings |
| **Goal** | Comprehensive debriefing capturing learnings, deviations, and recommendations |
| **Key Acceptance Criteria** | • Detailed report created following structured template<br>• Report saved as .md file<br>• All deviations documented<br>• Stakeholder approval obtained<br>• Execution trace saved in debrief-and-document/trace.md<br>• Report committed and pushed |
| **Project-Specific Notes** | • Final assignment before PR merge<br>• Must capture Python project setup issues (not .NET)<br>• Identify gaps between plan docs and implementation<br>• Must file issues for any action items discovered |
| **Prerequisites** | All previous assignments completed |
| **Dependencies** | All workflow outputs to document |
| **Risks/Challenges** | • May discover issues too late to fix before merge<br>• Must ensure all deviations captured for future improvement |
| **Events** | None specific (but must initiate continuous-improvement after completion) |

### 3.6 pr-approval-and-merge

| Field | Content |
|---|---|
| **Assignment** | `pr-approval-and-merge`: Pull Request Approval and Merge |
| **Goal** | Complete PR approval,**Key Acceptance Criteria** | • CI verification passed (all checks green)<br>• Code review delegated to code-reviewer subagent<br>• PR comments resolved following ai-pr-comment-protocol.md<br>• GraphQL verification artifacts captured<br>• Stakeholder approval obtained<br>• Merge completed<br>• Source branch deleted<br>• Related issues closed |
| **Project-Specific Notes** | • Input: $pr_num from init-existing-repository<br>• **This is automated setup PR - self-approval acceptable**<br>• Must wait for auto-reviewers (Copilot, CodeQL, etc.)<br>• Must execute CI remediation loop (up to 3 attempts)<br>• Output: result = "merged" \| "pending" \| "failed" |
| **Prerequisites** | All previous assignments completed and approved |
| **Dependencies** | PR number from init-existing-repository |
| **Risks/Challenges** | • CI failures requiring iteration<br>• Merge conflicts<br>• GitHub API rate limits |
| **Events** | None specific |

## 4. Sequencing Diagram

```
pre-script-begin
    └─> create-workflow-plan (CURRENT)
         └─> [Stakeholder Approval Required]

init-existing-repository
    ├─> post-assignment-complete
    │    ├─> validate-assignment-completion
    │    └─> report-progress
    └─> [Creates PR, Branch, Project]

create-app-plan
    ├─> pre-assignment-begin
    │    └─> gather-context
    ├─> post-assignment-complete
    │    ├─> validate-assignment-completion
    │    └─> report-progress
    └─> [Creates Planning Issue]

create-project-structure
    └─> [Creates Python Project Structure, AGENTS.md]

debrief-and-document
    └─> [Creates Debrief Report]

pr-approval-and-merge
    ├─> CI Verification (Phase 0.5)
    ├─> Code Review Delegation (Phase 0.75)
    ├─> Comment Resolution (Phase 1)
    ├─> Approval (Phase 2)
    └─> Merge & Cleanup (Phase 3)

post-script-complete
    └─> Apply orchestration:plan-approved label to plan issue
```

## 5. Open Questions

1. **Existing Plan Documents:** The plan_docs/ directory already contains extensive planning documents (Development Plan v4, Architecture Guide v3, Implementation Spec v1). Should create-app-plan create new tech-stack.md and architecture.md files, or should it reference the existing documents?

2. **Sample Implementation Files:** There are already sample implementation files (orchestrator_sentinel.py, notifier_service.py) in plan_docs/. Should create-project-structure use these as starting points, or start fresh?

3. **GitHub App Token:** The init-existing-repository assignment requires GH_ORCHESTRATION_AGENT_TOKEN with administration:write scope for branch protection ruleset import. Is this token available in the environment?

4. **Python vs .NET:** The template repository appears to have .NET infrastructure (based on AGENTS.md references), but the OS-APOW project is Python-based. Should existing .NET workflows be removed or modified?

5. **Branch Protection Ruleset:** The .github/protected-branches_ruleset.json references the repository owner dynamically. Will this work correctly for the intel-agency organization?

## 6. Critical Constraints

- **Action SHA Pinning:** All GitHub Actions workflows created or modified MUST pin actions to specific commit SHAs, not version tags
- **Python-First:** This is a Python 3.12+ project using uv, NOT a .NET project
- **Docker Healthchecks:** Must use Python stdlib for healthchecks, not curl
- **Editable Installs:** When using `uv pip install -e .`, ensure COPY src/ happens before the install command
- **Security:** All webhooks must validate HMAC signatures, credentials must be scrubbed from logs

## 7. Event Assignments
The following assignments are triggered by events during workflow execution:

### create-workflow-plan (pre-script-begin)
- **Status:** Currently executing
- **Purpose:** Create this workflow execution plan before any other assignments begin

### gather-context (pre-assignment-begin for create-app-plan)
- **Purpose:** Gather context before creating the application plan

### recover-from-error (on-assignment-failure for create-app-plan)
- **Purpose:** Systematic error recovery if create-app-plan fails

### validate-assignment-completion (post-assignment-complete)
- **Purpose:** Validate each assignment after completion using independent QA agent
- **Triggers:** After init-existing-repository and create-app-plan

### report-progress (post-assignment-complete)
- **Purpose:** Report progress, capture outputs, and file action items after each assignment
- **Triggers:** After init-existing-repository and create-app-plan

---

**Plan Created:** 2026-04-06  
**Workflow:** project-setup  
**Status:** Pending Stakeholder Approval
