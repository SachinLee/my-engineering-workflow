---
name: archive-task
description: Archive an accepted OpenSpec change after the user explicitly verifies it and asks to archive. Never archive an unaccepted change on the agent's own initiative.
---

# Archive OpenSpec Change

Close out an OpenSpec change after the user has accepted it. This is the only
workflow operation that moves a change into `openspec/changes/archive/`, and it
runs only on the user's explicit instruction.

## Verify Acceptance First

Resolve the change id the user gave, otherwise the active OpenSpec change selected
by the workflow. Read `proposal.md`, `specs/`, `design.md`, `tasks.md`, and
`artifacts/verification.md`. Archive only when all three hold:

1. The change handoff is `awaiting-acceptance`.
2. `artifacts/verification.md` has one result row for every AC in the proposal and
   relevant specs, with no unverified criterion omitted.
3. The user accepted this change in the current session in their own words
   ("验收通过", "没问题，归档吧", or an equivalent).

Anything else returns `ARCHIVE_STATUS: REFUSED` naming the missing condition. Do not run extra checks to earn the archive; report the gap and the next step to
invoke — `finish-with-evidence` when evidence is missing, or a fix plus a new
`## 复验轮次 N` round when the user reported a problem.

When several changes exist and none is clearly accepted, list each candidate with
its OpenSpec status and ask which one to archive instead of guessing.

## Archive

Run in this order and stop at the first failure:

1. Append the acceptance record to the change's `artifacts/verification.md` under
   `验收`: `accepted by user`, the date, and the user's verification note if given.
2. Update the change status to `accepted` in the repository's approved OpenSpec
   status mechanism.
3. Move the change directory to `openspec/changes/archive/<same-change-id>/` using
   the OpenSpec CLI or platform file tools. Verify the archived path still carries
   the change id before continuing.
4. Confirm `openspec/changes/` no longer lists the active change and
   `openspec/changes/archive/` now holds it.
5. Only after the archive is verified, delete a legacy compatibility pointer when
   the user explicitly requested that cleanup. Never mutate `.workflow/` or
   `.trellis/` as part of ordinary new-work archival.

Finish with exactly one status line:

- `ARCHIVE_STATUS: ARCHIVED` — every step completed.
- `ARCHIVE_STATUS: REFUSED` — a precondition was missing; nothing was moved.
- `ARCHIVE_STATUS: PARTIAL` — state which steps already happened and which failed,
  so the user can finish the remainder by hand. Never silently retry a move.

## Boundaries

- Committing, pushing, publishing, and deleting an archived change stay out of
  scope; this operation only relocates the OpenSpec record inside the repository.
- Never edit a change that is already archived. A corrected conclusion belongs in a
  new change that references the archive.
- Promoting a reusable convention into `openspec/specs/`, `CONTEXT.md`, or an ADR
  is separate work, done before this operation, not inside it.
- One invocation archives one change.
- Write OpenSpec text through the platform's file tools. If a shell command is
  unavoidable, force UTF-8.
