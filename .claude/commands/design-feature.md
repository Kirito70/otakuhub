# Design a New Feature End-to-End

When this command is invoked with a feature name, produce a complete design document.
Do NOT write any implementation code. Output only the design spec.

## Your Output (in this exact order)

### 1. Feature Overview
- What problem it solves for the OtakuHub friend group
- User stories (max 5, format: "As a [user], I want to [action] so that [benefit]")
- Out of scope (what we are explicitly NOT building)

### 2. Architecture Decision Record
Follow the ADR template from CLAUDE.md.
Save as `docs/adr/NNN-<feature-slug>.md` (find the next available number).

### 3. Database Schema Changes
For each new or modified table:
- Table name, columns with types, constraints, indexes
- Rationale for each design choice
- Alembic migration command to generate

### 4. API Contract
For each new endpoint:
- Method, path, auth requirement
- Request schema (JSON)
- Response schema (success + error codes)
- Any rate limiting or special behaviour

### 5. Flutter State Shape
- Which Riverpod providers are needed
- State type (AsyncNotifier, FutureProvider, etc.)
- What data the screen receives and how it's structured

### 6. Implementation Sequence
Ordered list of tasks for the build agents:
1. DB migration
2. SQLAlchemy models
3. Pydantic schemas
4. Repository methods
5. Service methods
6. FastAPI router
7. Tests
8. Flutter provider
9. Flutter screen/widgets
10. Flutter tests

### 7. Open Questions
List anything that needs a decision before building can start.
