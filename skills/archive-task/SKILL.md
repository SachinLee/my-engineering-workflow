---
name: archive-task
description: Archive an accepted task in .workflow/ - journal line, move to archive/, clear pointers. Use only after the user has verified the work and asked to archive it. Never archive an unaccepted task on your own initiative.
---

# Archive Task

Close out a task record after the user has accepted it. This is the only place a
task directory moves, and it runs on the user's instruction — never on the
agent's own conclusion that the work looks finished.

## Verify Acceptance First

Resolve the task: the path the user gave, otherwise this session's pointer under
`.workflow/by-session/`, otherwise `.workflow/CURRENT.md`. Then read its `STATUS`
and `outcome.md`. Archive only when all three hold:

1. `STATUS` is `phase: awaiting-acceptance`.
2. `outcome.md` exists and its 验收标准 table has one row for every
   `- [ ] AC-NNN` in `prd.md`.
3. The user accepted this task in the current session in their own words
   ("验收通过", "没问题，归档吧", or an equivalent).

Anything else returns `ARCHIVE_STATUS: REFUSED` naming the missing condition. Do
not run extra checks to earn the archive; report the gap and the next step to
invoke — `finish-with-evidence` when evidence is missing, or a fix plus a new
`## 复验轮次 N` round when the user reported a problem.

When several tasks exist and none is clearly accepted, list each candidate with
its `phase` and ask which one to archive instead of guessing.

## Archive

Run in this order and stop at the first failure:

1. Append the acceptance record to `outcome.md` under 验收: `acceptance:
   accepted by user`, the date, and the user's verification note if they gave one.
2. Set `STATUS` to `phase: done` with the current timestamp.
3. Append one line to `.workflow/journal.md`:

   ```text
   <date>  <task path>  <one-sentence outcome>  <commit or branch>
   ```

   Take the outcome from 概述 and the commit from 提交; write `NOT COMMITTED`
   when that is what the record says. Never invent a hash.
4. Ensure `.workflow/archive/` exists, then move the task directory into
   `.workflow/archive/<same-name>/`. A missing destination directory makes
   `Move-Item` and `mv` rename the source instead of moving it — verify the
   archived path still carries the task name before continuing.
5. Delete this session's pointer file, then set `.workflow/CURRENT.md` to
   `task: none`, or to the next task the user names.
6. Confirm `.workflow/tasks/` no longer lists the task and `.workflow/archive/`
   now holds it, and report both paths.

Finish with exactly one status line:

- `ARCHIVE_STATUS: ARCHIVED` — every step completed.
- `ARCHIVE_STATUS: REFUSED` — a precondition was missing; nothing was moved.
- `ARCHIVE_STATUS: PARTIAL` — state which steps already happened and which failed,
  so the user can finish the remainder by hand. Never silently retry a move.

## Boundaries

- Committing, pushing, publishing, and deleting an archived task stay out of
  scope; this command only relocates the record inside the repository.
- Never edit a task that is already archived. A corrected conclusion belongs in a
  new task that references the archive.
- Promoting a reusable convention into `.workflow/spec/` or `CONTEXT.md` is
  separate work, done before this command, not inside it.
- One invocation archives one task.
- Write `.workflow/` text through the platform's file tools. If a shell command is
  unavoidable, force UTF-8: PowerShell 5.1's `Add-Content`/`Set-Content` default to
  the ANSI codepage and store Chinese journal lines as GBK.
