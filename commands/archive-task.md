---
description: Archive a task the user has accepted - journal line, move to .workflow/archive/, clear pointers.
argument-hint: "[optional task path]"
---

# Archive Task

Use the `archive-task` skill to archive:

`$ARGUMENTS`

Resolve the task from the argument, this session's pointer, or
`.workflow/CURRENT.md`. Archive only when the task is in
`phase: awaiting-acceptance`, `outcome.md` covers every acceptance criterion, and
the user has accepted it in this session. Otherwise report
`ARCHIVE_STATUS: REFUSED` with the missing condition and stop.

When the preconditions hold, run the steps in order: record the acceptance in
`outcome.md`, set `STATUS` to `phase: done`, append the `.workflow/journal.md`
line, move the directory into `.workflow/archive/`, delete this session's pointer,
clear or retarget `CURRENT.md`, then report both resulting paths with
`ARCHIVE_STATUS: ARCHIVED`. Never commit, push, delete an archive, or archive a
task the user has not accepted.
