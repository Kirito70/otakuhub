# OtakuHub & VibeCoding – AI Agent Catalog

## Global Quality Gate (Applies to Claude, OpenCode, Copilot)
- TDD is mandatory: red → green → refactor for frontend and backend changes.
- Frontend forms must include client-side validation (required fields + basic format checks) before API submission.
- Frontend form tests are mandatory: empty submit, invalid input, inline error states, and successful submit flow.
- No phase/sub-phase can be marked complete until relevant tests are updated and executed.

## Shared Manifest & Loader
All agents live under the **`.claude/`** directory (the original Claude‑style implementation). The same definitions are exposed to VS Code (Open‑Code) and GitHub Copilot via the shared manifest in `agents/manifest.json` and the helper `agents/loader.py`.

## Agent Table
| Agent | Primary Tool | Responsibility | Entry point (Claude) | VS Code / Copilot entry |
|-------|--------------|----------------|----------------------|--------------------------|
| **architect** | Claude Code | System design, ADRs, schema, API contracts | `.claude/agents/architect.py` | `agents/vscode/architect.py` |
| **backend‑dev** | Cline / OpenCode | FastAPI routes, services, repos | `.claude/agents/backend-dev.py` | `agents/vscode/backend-dev.py` |
| **flutter‑dev** | Antigravity | Flutter UI, Riverpod, GoRouter | `.claude/agents/flutter-dev.py` | `agents/vscode/flutter-dev.py` |
| **db‑designer** | Claude Code | DB schema, Alembic migrations | `.claude/agents/db-designer.py` | `agents/vscode/db-designer.py` |
| **code‑reviewer** | Copilot / Claude Code | PR review, quality gates | `.claude/agents/code-reviewer.py` | `agents/vscode/code-reviewer.py` |
| **security‑auditor** | Claude Code | Auth, injection, secret handling | `.claude/agents/security-auditor.py` | `agents/vscode/security-auditor.py` |
| **sync‑engineer** | Cline / OpenCode | AniList/MangaDex sync pipeline | `.claude/agents/sync-engineer.py` | `agents/vscode/sync-engineer.py` |
| **api‑designer** | Claude Code | OpenAPI spec, endpoint contracts | `.claude/agents/api-designer.py` | `agents/vscode/api-designer.py` |
| **tdd‑enforcer** | Claude Code | Enforce test‑first workflow | `.claude/agents/tdd-enforcer.py` | `agents/vscode/tdd-enforcer.py` |
| **vibecoding‑architect** | Claude Code | System design, ADRs, schema, API contracts for VibeCoding | `.claude/agents/vibecoding-architect.py` | `agents/vscode/vibecoding-architect.py` |
| **vibecoding‑backend‑dev** | Cline / OpenCode | FastAPI routes, services, repos for VibeCoding | `.claude/agents/vibecoding-backend-dev.py` | `agents/vscode/vibecoding-backend-dev.py` |
| **vibecoding‑flutter‑dev** | Antigravity | Flutter UI, Riverpod, GoRouter for VibeCoding | `.claude/agents/vibecoding-flutter-dev.py` | `agents/vscode/vibecoding-flutter-dev.py` |
| **vibecoding‑db‑designer** | Claude Code | DB schema, Alembic migrations for VibeCoding | `.claude/agents/vibecoding-db-designer.py` | `agents/vscode/vibecoding-db-designer.py` |
| **vibecoding‑code‑reviewer** | Copilot / Claude Code | PR review, quality gates for VibeCoding | `.claude/agents/vibecoding-code-reviewer.py` | `agents/vscode/vibecoding-code-reviewer.py` |
| **vibecoding‑security‑auditor** | Claude Code | Auth, injection, secret handling for VibeCoding | `.claude/agents/vibecoding-security-auditor.py` | `agents/vscode/vibecoding-security-auditor.py` |
| **vibecoding‑sync‑engineer** | Cline / OpenCode | Sync pipeline for VibeCoding | `.claude/agents/vibecoding-sync-engineer.py` | `agents/vscode/vibecoding-sync-engineer.py` |
| **vibecoding‑api‑designer** | Claude Code | OpenAPI spec, endpoint contracts for VibeCoding | `.claude/agents/vibecoding-api-designer.py` | `agents/vscode/vibecoding-api-designer.py` |
| **vibecoding‑tdd‑enforcer** | Claude Code | Enforce test‑first workflow for VibeCoding | `.claude/agents/vibecoding-tdd-enforcer.py` | `agents/vscode/vibecoding-tdd-enforcer.py` |

> **How it works**
> - The **manifest** (`agents/manifest.json`) lists each agent name, description, allowed tools, and the relative path to its implementation file.
> - VS Code’s *Open‑Code* extension reads the manifest and loads the Python module directly (via `agents/loader.py`).
> - GitHub Copilot‑Chat also reads the same manifest, so the same agent logic is available inside PR comment threads.
>
**Note:** Do **not** edit the files under `agents/vscode/` or `agents/copilot/` directly – they are symbolic links to the canonical `.claude/agents/`. All source‑of‑truth changes must be made in `.claude/agents/` and will instantly propagate.
