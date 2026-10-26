---
description: Archive an OpenSpec change the user has accepted.
argument-hint: "[optional change id]"
---

# Archive OpenSpec Change

Use the `archive-task` skill to archive the requested OpenSpec change:

`$ARGUMENTS`

Resolve the change from the argument or the workflow's active OpenSpec selection.
Archive only when the change is `awaiting-acceptance`,
`artifacts/verification.md` covers every acceptance criterion, and the user has
accepted it in this session. Otherwise report `ARCHIVE_STATUS: REFUSED` with the
missing condition and stop.

When the preconditions hold, run the skill's ordered steps: record acceptance in
`artifacts/verification.md`, update the OpenSpec status, move the change into
`openspec/changes/archive/`, verify both active and archive paths, and remove a
legacy pointer only when the user explicitly requested that cleanup. Never commit,
push, delete an archive, or archive a change the user has not accepted.
