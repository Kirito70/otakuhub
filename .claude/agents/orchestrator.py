"""
OtakuHub orchestrator agent.

Purpose:
- Classify incoming user requests by domain.
- Summarize requested change in one sentence.
- Hand off to @architect in a strict, compact format.

This agent does not implement code changes itself.
"""

from __future__ import annotations

class OrchestrationResult:
    def __init__(self, task: str, domain: str, user_request: str) -> None:
        self.task = task
        self.domain = domain
        self.user_request = user_request

    def render(self) -> str:
        return (
            f"TASK: {self.task}\n"
            f"DOMAIN: {self.domain}\n"
            f"USER REQUEST: {self.user_request}"
        )


DOMAINS = (
    "backend",   # FastAPI, SQLAlchemy, Celery, DB, API contracts
    "frontend",  # Quasar/Vue pages, stores, UX
    "fullstack", # touches backend + frontend
    "sync",      # AniList/MangaDex/Jikan pipeline, seed/backfill, Celery sync tasks
    "infra",     # Docker, CI/CD, deploy, env/runtime
    "security",  # auth, permissions, secrets, audit
    "docs",      # ADRs, status docs, specs
)


def _classify_domain(user_text: str) -> str:
    text = user_text.lower()

    backend_hits = any(k in text for k in (
        "fastapi", "endpoint", "router", "service", "repository", "alembic", "sql", "postgres", "pydantic"
    ))
    frontend_hits = any(k in text for k in (
        "tailwind", "shadcn", "vite", "vue", "pinia", "page", "component", "form", "layout", "sidebar", "mobile ui"
    ))
    sync_hits = any(k in text for k in (
        "sync", "seed", "anilist", "mangadex", "jikan", "celery", "backfill", "weekly refresh"
    ))
    infra_hits = any(k in text for k in (
        "docker", "compose", "nginx", "ci", "github actions", "deploy", "tls", "infra"
    ))
    security_hits = any(k in text for k in (
        "auth", "jwt", "permission", "rbac", "security", "secret", "injection", "idor"
    ))
    docs_hits = any(k in text for k in (
        "adr", "project-status", "api-spec", "documentation", "docs"
    ))

    # Priority rules
    if sync_hits:
        return "sync"
    if infra_hits:
        return "infra"
    if security_hits and not (backend_hits or frontend_hits):
        return "security"
    if docs_hits and not (backend_hits or frontend_hits or sync_hits):
        return "docs"
    if backend_hits and frontend_hits:
        return "fullstack"
    if backend_hits:
        return "backend"
    if frontend_hits:
        return "frontend"
    return "fullstack"


def _one_sentence_summary(user_text: str) -> str:
    cleaned = " ".join(user_text.strip().split())
    if not cleaned:
        return "Clarify the requested change and route it to the appropriate implementation agent."
    if len(cleaned) <= 140:
        return cleaned[0].upper() + cleaned[1:]
    return cleaned[:137].rstrip() + "..."


def run(**kwargs):
    """
    Expected kwargs (best effort):
    - user_request / request / prompt / task: str

    Returns strict handoff format for @architect.
    """
    user_request = (
        kwargs.get("user_request")
        or kwargs.get("request")
        or kwargs.get("prompt")
        or kwargs.get("task")
        or ""
    )
    user_request = str(user_request)

    result = OrchestrationResult(
        task=_one_sentence_summary(user_request),
        domain=_classify_domain(user_request),
        user_request=user_request,
    )

    return result.render()
