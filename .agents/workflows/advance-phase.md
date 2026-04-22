---
description: Mark the current sub-phase complete in PROJECT-STATUS.md and show the next task and its prompt.
---

When the user types `/advance-phase`, perform these steps:

## Step 1 — Read status
Read PROJECT-STATUS.md. Identify CURRENT_PHASE and CURRENT_SUB_PHASE.

## Step 2 — Update PROJECT-STATUS.md
- Change current sub-phase row from ⏳ to ✅
- Find next ⏳ row in the same phase
- Set CURRENT_SUB_PHASE to that row
- Set LAST_UPDATED to today
- Append to Completion Log: `YYYY-MM-DD | Phase X.Y | <description>`

## Step 3 — Phase boundary check
If all rows in the phase are ✅:
- Set STATUS to PHASE_COMPLETE
- Announce the phase is done
- Show what the next phase needs
- **PAUSE — wait for user confirmation before advancing CURRENT_PHASE**

If not at boundary:
- Show: "✅ Done. Next: [sub-phase ID] — [task name]"
- Show: "Tool: [recommended tool]"
- Show the prompt block from PROJECT-PROMPT.md for the new sub-phase

## Step 4 — Artifact
Produce an Artifact showing:
```
PROJECT STATUS UPDATE
=====================
Completed:  Phase X.Y — [description]
Next:       Phase X.Z — [description]
Tool:       [recommended tool]
Status:     IN_PROGRESS

Next prompt ready to copy:
[prompt text]
```
