# Advance to Next Sub-Phase

When this command is run, perform the following steps in order:

## Step 1 — Read current status
Read PROJECT-STATUS.md. Find the row with CURRENT_SUB_PHASE. Confirm its status is ✅ or that the user has confirmed the task is done.

## Step 2 — Update PROJECT-STATUS.md
1. Change the current sub-phase row from ⏳ to ✅ (if not already done)
2. Find the next ⏳ row in the same phase
3. Update CURRENT_SUB_PHASE to that row's identifier
4. Update LAST_UPDATED to today's date
5. Add a line to the Completion Log:
   `YYYY-MM-DD | Phase X.Y | <one-line description of what was completed>`

## Step 3 — Phase boundary check
If ALL rows in the current phase are now ✅:
- Set STATUS to PHASE_COMPLETE
- Print a phase completion summary
- Show the user what Phase N+1 requires and which tool to use
- Wait for the user to confirm before setting CURRENT_PHASE to N+1

If NOT at a phase boundary:
- Print: "✅ Sub-phase X.Y complete. Next task: X.Z — [task description]"
- Print: "Primary tool for this task: [tool name]"
- Print: "Copy the prompt from PROJECT-PROMPT.md § Phase X, Prompt X.Z"

## Step 4 — Show next prompt
Find the corresponding prompt block in PROJECT-PROMPT.md for the new CURRENT_SUB_PHASE.
Print it so the user can copy it directly.

## Example output format
```
✅ Sub-phase 3.4 complete — Seed script: download + import anime-offline-database

Next: Sub-phase 3.5 — Celery app + Redis broker configured
Tool: Cline or OpenCode (@sync-engineer)

--- Copy this prompt ---
[prompt text from PROJECT-PROMPT.md]
--- End prompt ---
```
