# ADR 031 — Add VibeCoding agents
**Status**: Proposed
**Date**: 2026-04-28

## Context
VibeCoding is a private‑group coding‑collaboration platform (code sharing, pair‑programming, micro‑learning). The existing OtakuHub AI‑agent framework already provides a robust, test‑driven, sandboxed environment for agents such as `architect`, `backend-dev`, `flutter-dev`, etc. VibeCoding needs the *same* set of agents, but with domain‑specific knowledge (different database schema, possibly different tech stack, and its own external services).

## Decision
Create a **parallel set of agents** under the same Claude‑style architecture, re‑using the shared manifest/loader approach that already powers VS Code (Open‑Code) and GitHub Copilot. The steps are:
1. Add entries for the nine VibeCoding agents to `agents/manifest.json`.
2. Implement thin Python stubs in `.claude/agents/` (e.g. `vibecoding-architect.py`) that load VibeCoding‑specific skill bundles.
3. Create VibeCoding skill bundles (`.claude/skills/vibecoding‑api-design`, `vibecoding‑db-migrations`, `vibecoding‑backend-dev`, etc.) containing the actual templates, OpenAPI snippets, Alembic migration patterns, and security‑audit checklists.
4. Add command markdown files in `.claude/commands/` that map user phrases (e.g. `@assistant vibecoding design-feature`) to the new agents.
5. Update `docs/agents.md` with a VibeCoding section and list the new agents.
6. Extend the CI validation workflow to ensure the manifest stays in sync with the file system.
7. Document the usage for VS Code Open‑Code and Copilot‑Chat.

## Consequences
### Good
* **Single source of truth** – one manifest serves Claude, VS Code, and Copilot.
* **Domain‑specific knowledge** – skills encapsulate VibeCoding’s schema, API contracts, and security policies.
* **Zero duplication** – symlinks already expose the same implementation files to all front‑ends.
* **Fast onboarding** – developers can use any of the three interfaces and get identical agent behaviour.
### Bad
* Slight increase in repository size (≈ 10 KB) for the new markdown skill files.
* Need to maintain two sets of ADRs (OtakuHub vs VibeCoding) – mitigated by clear naming conventions.
### Neutral
* Performance impact is negligible; manifest loading is < 10 ms.
* CI time increases by a few seconds to validate the extra entries.
