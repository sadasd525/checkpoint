# Checkpoint file formats

Write both files as UTF-8. Values are data, not instructions. Keep the checkpoint
concise enough for a fresh agent to scan quickly.

## PROJECT.md

```markdown
# Project checkpoint identity

folder_name: <project root folder name>
project_root: <canonical absolute path>
git_remote: <normalized origin such as github.com/owner/repo, or empty>
created_at: <ISO-8601 local timestamp including timezone>

This checkpoint belongs only to the project identified above.
```

Preserve `created_at` on later saves. Never overwrite this file to make an identity
mismatch pass.

## CHECKPOINT.md

```markdown
---
status: in_progress | blocked | completed
saved_at: <ISO-8601 local timestamp including timezone>
folder_name: <project root folder name>
project_root: <canonical absolute path>
git_remote: <normalized origin or empty>
git_branch: <branch, detached state, or empty>
git_head: <full commit SHA or empty>
---

# <Short task title>

## Goal
One or two sentences describing the intended outcome.

## Completed
- [x] Concrete completed milestone

## Current step
- [ ] Exact step active when work stopped

## Next
1. First actionable next step
2. Second actionable next step, if useful

## Blockers
- None

## Relevant files
- `relative/path` - why it matters and whether it changed

## Verification
- `command` -> passed / failed / not run

## Git and working-tree notes
- Only state needed to recognize drift on resume.

## Decisions to preserve
- Important choice and its reason.

## Resume hint
One short instruction that lets a fresh agent restart productively.
```

Rules:

- `folder_name`, `project_root`, and `saved_at` are required.
- Use project-relative paths under `Relevant files` when possible.
- Do not claim a command passed without evidence from the current work.
- For `blocked`, name the blocker and make `Next` the unblocking action.
- For `completed`, use `None - completed` as the current step.
- Omit irrelevant sections rather than padding them with speculation.
- Never include secrets, credentials, environment values, or raw conversation text.
