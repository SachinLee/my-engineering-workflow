# Workflow Governance

Read this reference when routing a task, resolving conflicts between
integrations, or deciding where durable information belongs.

## Record Layout

`.workflow/` is a convention, not a program. Every file below is written and
read with the platform's own file tools. There is no CLI, no lock service, and
no background process; a missing file means the state it would hold was never
decided, and an unreadable file is an invalid dispatch, not a reason to guess.

```text
.workflow/
  CURRENT.md                 human-visible pointer: task path + updated (phase lives in STATUS)
  by-session/<key>.md        per-session pointer; <key> is <platform>-<session id>
                             or "main" when the harness exposes no session id
  journal.md                 one append-only line per closed task
  spec/                      optional durable conventions, package/layer scoped
  tasks/<MM-DD-slug>/
    prd.md                   requirements, scope, assumptions, acceptance criteria
    design.md                optional technical design
    implement.md             optional ordered vertical slices
    context.md               the files this task must read, each with a reason
    STATUS                   exactly two lines: phase and updated
    outcome.md               written at close: evidence per acceptance criterion
    tickets/                 one file per 工单 when the task spans sessions or writers
    research/                optional notes, source excerpts, measurements
  archive/<MM-DD-slug>/      moved here on close; contents are never edited
                             written only by a user-requested archival step
```

`STATUS` holds only:

```text
phase: planning | in_progress | review | awaiting-acceptance | done
updated: 2026-09-14T15:40:00Z
```

Rules that keep the layout cheap to read:

- One task, one directory, one `STATUS`. Never store the phase in the pointer
  file alone, because two concurrent sessions must not overwrite each other.
- `context.md` replaces automatic spec injection. It lists paths and one-line
  reasons, not file bodies. Dispatch copies those paths into the handoff `Read:`
  field.
- `outcome.md` is the only place delivery claims live. Anything not evidenced
  there is not delivered.
- `archive/` is append-only history. Recovering an old decision means reading
  it, never resurrecting it as current state.
- The whole layout is optional per repository. When a repository keeps no
  records, this workflow says so out loud instead of inventing a store.

## Artifact Language

Human-facing artifacts — `prd.md`, `design.md`, `implement.md`, `context.md`,
`outcome.md`, `journal.md`, and ticket bodies — are written in the user's
language, Chinese by default, including section headings and field labels. Keep
verbatim and greppable: code identifiers, file paths, commands, log and error
text, `STATUS` keys (`phase`, `updated`), ticket front-matter keys, and status
tokens (`PASS`, `NOT RUN`, `REVIEW_STATUS: CLEAN`). Do not translate an identifier
into prose, and do not restate in chat what the artifact already records.

## Tickets And Decomposition

Three split levels; use the smallest one that fits how the work gets executed:

| 级别 | 用在什么时候 | 落在哪里 |
| --- | --- | --- |
| 切片 | 同一会话顺序完成、共享模块、单 writer | `implement.md` 的 `### 切片 N` |
| 工单 | 可独立验收、跨会话续接、或多 writer | `tickets/NN-<slug>.md` |
| 多任务 | 不同发布单元、不同仓库、可独立收口 | 多个 task 目录，外加一个总控 task |

A ticket file starts with:

```text
---
id: T2
标题：摄像头状态 CAS 更新
covers: [AC-001]
blocked_by: [T1]
state: ready          # ready | in_progress | done | blocked
writer: main          # main | workflow-implementer
---
```

The frontier is the set of `ready` tickets whose `blocked_by` are all `done`. One
ticket, one live writer. `state: done` requires executed verification evidence,
recorded in `outcome.md`. Never duplicate the slice plan inside a ticket:
reference `implement.md#切片-N` and its 上下文包 instead.

## Acceptance And Archival

**The user accepts and archives. The agent never does it on its own initiative.**

- Once evidence is complete, the agent writes `outcome.md`, sets `STATUS` to
  `awaiting-acceptance`, and stops. It states what to verify: every AC with the
  command or manual step that proves it, plus every check left `NOT RUN`.
- Moving a task directory, deleting a pointer, and setting `phase: done` are the
  user's actions. The agent prints the commands instead of running them, and runs
  them only when the user explicitly asks in the current session and the task is
  already in `awaiting-acceptance`.
- A failed verification is a normal transition, not an exception: the user reports
  what is wrong, the agent moves `STATUS` back to `in_progress`, fixes, re-runs the
  affected checks, and appends a new round to `outcome.md`. Earlier rounds stay
  visible; nobody rewrites history to make a task look clean.
- `phase: done` means "the user accepted", not "the checks passed".

The `archive-task` command performs these steps when you ask for it
(`$archive-task`, `/archive-task`, or `/skill:archive-task`). It re-checks the three
acceptance conditions, returns `ARCHIVE_STATUS: REFUSED` naming what is missing
instead of archiving, and on success reports `ARCHIVE_STATUS: ARCHIVED` with both
resulting paths. Running the commands yourself stays equally valid.

Archival, run by the user (PowerShell):

```text
$task = ".workflow\tasks\<id>"
New-Item -ItemType Directory -Force -Path .workflow\archive | Out-Null
[IO.File]::AppendAllText("$PWD\.workflow\journal.md", "<date>  $task  <一句话结果>  <commit or branch>`r`n", (New-Object Text.UTF8Encoding $false))
Move-Item -LiteralPath $task -Destination .workflow\archive\
Remove-Item -LiteralPath .workflow\by-session\<key>.md
Set-Content -LiteralPath .workflow\CURRENT.md -Value "task: none"
```

or in POSIX shells:

```text
task=.workflow/tasks/<id>
printf '%s  %s  <一句话结果>  <commit or branch>\n' "$(date -F)" "$task" >> .workflow/journal.md
mkdir -p .workflow/archive
mv "$task" .workflow/archive/   # destination must exist, or mv renames instead
rm -f .workflow/by-session/<key>.md
printf 'task: none\n' > .workflow/CURRENT.md
```

Use the platform's file tools when you can. Shell writes to `.workflow/` need an
explicit UTF-8: on Windows PowerShell 5.1 `Add-Content` and `Set-Content` default
to the ANSI codepage, so Chinese text lands in the journal as GBK and reads as
mojibake everywhere else. The `[IO.File]::AppendAllText` form above writes UTF-8
without a BOM on any PowerShell version.

Afterwards `.workflow/tasks/` no longer contains the task, and the archived copy is
read-only from then on.

## Prompt Cache Constraint

Task state must reach the model through reads, never through head-of-request
injection. A per-turn injector places volatile content before the conversation
history, which invalidates the cached prefix for every later turn; measured cost
of one phase-change injection in a long session was a full re-bill of the entire
history, tens of thousands of tokens, to deliver a few hundred tokens of state.
Reads append to the tail and keep the prefix stable. This constraint outranks
convenience: a hook or extension that "helpfully" injects `.workflow/` state is
a defect, not a feature.

## Artifact Ownership

`.workflow/` is the canonical owner of task state and durable delivery records.
Store one fact in one authoritative place. Do not duplicate task facts across
workflow systems.

| Artifact | Canonical owner | Purpose |
| --- | --- | --- |
| `prd.md` | Active task directory | Requirements, scope, assumptions, acceptance criteria |
| `design.md` | Active task directory | Technical design, alternatives, compatibility, rollout |
| `implement.md` | Active task directory | Ordered execution and validation plan |
| `outcome.md` | Active task directory | Actual delivery, evidence, review, deviations, remaining risk |
| `STATUS` | Active task directory | Current phase and last transition |
| `by-session/` | Workflow record | Session-to-task binding only, never requirements |
| `tickets/` | Active task directory | Scheduling state for cross-session or parallel work; never a second plan |
| `.workflow/spec/` | Project knowledge | Durable conventions and prevention rules |
| `.workflow/journal.md` | Project journal | One-line closure record per task |
| `CONTEXT.md` | Domain glossary | Stable business vocabulary only |
| `docs/adr/` | Architecture decisions | Hard-to-reverse decisions and rationale |
| Code and tests | Git | Executable implementation and behavioral proof |

## Legacy `.trellis/` Repositories

Some repositories were initialized with Trellis before this workflow dropped it.
Treat `.trellis/` as a read-only historical format:

- Read `prd.md`, `design.md`, `implement.md`, `outcome.md`,
  `implement.jsonl`, `check.jsonl`, `research/`, and `task.json` when they are
  the only record of an active task. Map `task.json` `status` onto `phase`
  (`planning` → `planning`, `in_progress` → `in_progress`, `completed` → `done`).
- Convert a `*.jsonl` spec manifest into `context.md` the first time you
  dispatch for that task.
- Never execute a Trellis script, never install a Trellis injector, and never
  write into `.trellis/`. New state goes to `.workflow/`.
- Global spec directories (`.trellis/spec/`) may still be read; new conventions
  are written to `.workflow/spec/`.

## Context Loading Contract

Use three context tiers:

| Tier | When loaded | Contents |
| --- | --- | --- |
| Project context | Session start | Project identity, workflow rules, and relevant spec index |
| Task pointer | Session start or resume | One task path; the phase comes from that task's `STATUS` |
| Task package | Activation or dispatch | Inlined AC text, the design decisions it rests on, located `file:line` conclusions, invariants, file bounds, and the exact checks |

The task package is derived from the active task artifacts and is not a second
durable record. Refresh it after requirement clarification, plan approval, slice
completion, review findings, and cross-session resume. When a harness cannot
bind a pointer to a session, use explicit task paths and bounded artifact
sections as the compatibility mode and record the limitation.

Inlining is the point: the package exists so a fresh worker starts from
conclusions. Paths alone are only acceptable for material the worker genuinely
has to open itself — usually the two or three files it will edit. When the package
is thin, the planning was thin; fix `implement.md` rather than letting every
dispatch re-run the same repository survey.

Issue trackers may link to a task directory, but must not duplicate its design
and implementation record.

## Routing Ownership

| Need | Primary capability | Destination |
| --- | --- | --- |
| Resume context | pointer + `STATUS` read | Existing task |
| Clarify intent | Matt `grilling` + observable ACs | `prd.md` |
| Model domain | Matt domain modeling | `CONTEXT.md`, rare ADR |
| Design solution | `plan-solution` + relevant specialists | `design.md` |
| Plan execution | `plan-solution` + test strategy | `implement.md` |
| Implement behavior | Matt `tdd` / ECC `tdd-workflow` | Code and tests |
| Review independently | `review-implementation` + Matt `code-review` | Findings returned to main session |
| Verify and record | repository checks + risk-specific checks | `outcome.md` |
| Reduce complexity | Ponytail review | Code, then re-verification |
| Preserve learning | `finish-with-evidence` promotion step | `.workflow/spec/` |

Do not run Matt `to-spec` or `to-tickets` as a parallel record system: their
output belongs inside the active task directory. Skip `to-spec` when
`clarify-requirements` already produced a complete `prd.md`. Do not use Ponytail
minimal checks to replace required repository checks.

## Source Trust

When sources disagree, use this order:

1. Running code, tests, and externally verified behavior.
2. Project specs (`.workflow/spec/`, or `.trellis/spec/` in legacy repos) and
   accepted ADRs.
3. Active task PRD, design, implementation plan, and outcome.
4. Git history and reviewed issue references.
5. Workflow journal, session pointers, and explicit handoffs.
6. Raw AI conversations and generated memory entries.

Promote reusable knowledge only after checking code, tests, or the user.

## OMP Model Roles

Use role aliases so the workflow remains provider-independent:

| Responsibility | OMP role | Reason |
| --- | --- | --- |
| Main orchestration and user questions | `@default` | Holds task context and user interaction |
| Solution planning | `@plan` | Dedicated architecture/planning role |
| `workflow-implementer` | `@task` | Cost-effective coding subagent under a reviewed plan |
| Independent review | `@advisor` | Different model/context from the implementer |
| Escalation | `@slow` or `@default` | Critical risk, repeated failure, or unresolved design drift |

Requirement clarification stays in the main session because subagents cannot
reliably conduct the one-question-at-a-time user dialogue. Do not use `@smol`
for requirements, architecture, security decisions, or final sign-off.

The `@task` implementation role does not lower quality gates. Escalate before
continuing when a critical task exposes uncertain security, data-integrity, or
public-contract decisions, or when the implementation repeatedly fails its
targeted checks.

## Claude Code Model Roles

Claude Code has named agents and per-agent `model` settings, but no OMP role
aliases. Use the interactive main session for requirements, orchestration,
approvals, remediation, and delivery. Use this repository's Opus
`workflow-planner` and read-only Opus `workflow-reviewer` for independent
planning and final review contexts.

All three agent definitions are owned by this repository and installed by
`scripts/install.ps1`. Because nothing is injected automatically, every dispatch
must carry the task path, the `context.md` read list, and the approved
RED/GREEN slices in its prompt; a handoff that omits them is invalid rather than
recoverable by scanning.

Launching the main session with `claude --model sonnet` normally separates the
implementation model from the Opus planning/review agents. When the main
session is Opus, subagent review is still a fresh context but not cross-model.

## Review Independence

For standard behavior changes and every critical task, the final reviewer must
use a fresh context and, when available, a different model role from the
implementer. The reviewer reports findings; the main session owns remediation,
re-verification, and the final delivery claim. A model never approves its own
unverified work merely because no separate reviewer is available.
