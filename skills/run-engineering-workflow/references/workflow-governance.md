# Workflow Governance

Read this reference when routing a task, resolving conflicts between
integrations, or deciding where durable information belongs.

## Record Layout

OpenSpec is the canonical record system for new work. It owns requirements,
change design, tasks, completion status, and archived change history. `.workflow/`
and `.trellis/` remain compatibility inputs only.

```text
openspec/
  config.yaml                 OpenSpec schema/configuration
  changes/<change-id>/        proposal, specs, design, tasks, artifacts/
  changes/archive/             OpenSpec archive, written only after acceptance

.workflow/                    legacy compatibility records
  CURRENT.md                  recoverable task pointer
  tasks/<MM-DD-slug>/         old prd/design/implement/context/outcome records
  by-session/<key>.md         old session binding
  archive/                    old archive; never recreated by new work

.trellis/                     read-only legacy records; never write or execute
```

The routing invariant is strict:

- If `openspec/config.yaml` or `config.yml` exists, OpenSpec is canonical.
- New work starts from read-only discovery (`scripts/openspec_compat.py`
  `list_changes`) over the current project's unarchived changes. Nothing is
  auto-selected, not even when exactly one change exists; multiple candidates
  are a normal waiting state, not an environment failure.
- Creating a change or reusing one requires an explicit user confirmation of the
  current proposal, once. Rejecting reuse is not consent to create; a
  confirmation expires when the candidate is archived or the goal changes.
- Same-goal matching judges the work object, expected outcome, compatible
  scope, and acceptance relationship; related-but-different goals are not a
  match, and environment errors are never reported as "no match".
- A legacy `.workflow` task may be read or explicitly migrated, but no new
  durable state is written there.
- `.trellis/` may be read for recovery only. Never run Trellis scripts or install
  Trellis injectors.
- Do not dual-write equivalent requirements, tasks, status, or evidence into
  OpenSpec and `.workflow/`.

`STATUS` and session pointers are still understood when recovering a legacy
`.workflow` task, but they are not part of the new canonical lifecycle.

## Artifact Language

Human-facing artifacts — OpenSpec `proposal.md`, `design.md`, `tasks.md`,
change specs, verification artifacts, and legacy records — are written in the
user's language, Chinese by default, including section headings and field
labels. Keep verbatim and greppable: code identifiers, file paths, commands, log
and error text, OpenSpec filenames, and status tokens (`PASS`, `NOT RUN`,
`REVIEW_STATUS: CLEAN`). Do not translate an identifier into prose, and do not
restate in chat what the artifact already records.

## Tickets And Decomposition

Three split levels; use the smallest one that fits how the work gets executed:

| Level | Use when | Location |
| --- | --- | --- |
| Slice | Same session, shared module, single writer | OpenSpec `tasks.md` |
| Ticket | Independently accepted, cross-session, or multiple writers | OpenSpec task item plus bounded artifact |
| Change | Different release unit or independent outcome | Separate OpenSpec change |

OpenSpec `tasks.md` is the execution frontier. One change, one live writer unless
an explicit ticket handoff says otherwise. A task is complete only with executed
verification evidence in `artifacts/verification.md` (or the repository's
approved equivalent). Do not recreate `.workflow/tickets/` for new work.

## Acceptance And Archival

**The user accepts and archives. The agent never does it on its own initiative.**

- Once evidence is complete, the agent updates the OpenSpec change's verification
  artifact and stops in `awaiting-acceptance` in the change record/handoff.
- Moving a change to `openspec/archive/`, deleting compatibility pointers, or
  declaring final acceptance are the user's actions. The agent prints the command
  instead of running it unless the user explicitly asks in the current session.
- A failed verification is a normal transition: keep the failure evidence,
  update `tasks.md`, fix the implementation, and append a new verification round.
- Legacy `.workflow` `STATUS` is changed only when recovering that legacy task,
  never as a shadow status for new OpenSpec work.

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

OpenSpec is the canonical owner for new task facts. Store one fact in one
authoritative place; compatibility readers must not create a second state store.

| Artifact | Canonical owner | Purpose |
| --- | --- | --- |
| `proposal.md` | OpenSpec change | Why, scope, and user-visible intent |
| `specs/**/*.md` | OpenSpec change | Normative requirements and scenarios |
| `design.md` | OpenSpec change | Technical design, alternatives, compatibility, rollout |
| `tasks.md` | OpenSpec change | Ordered implementation work and checks |
| `artifacts/context.md` | OpenSpec change | Dispatch context and bounded file map |
| `artifacts/verification.md` | OpenSpec change | Actual delivery, evidence, review, deviations, remaining risk |
| `docs/adr/` | Project docs | Accepted hard-to-reverse decisions and rationale |
| `openspec/changes/archive/` | OpenSpec | Accepted immutable history, user-triggered only |
| `.workflow/` | Legacy reader/migrator | Recovery and explicit migration input only |
| `.trellis/` | Legacy reader | Historical read-only input only |
| Code and tests | Git | Executable implementation and behavioral proof |

## Legacy `.workflow` And `.trellis` Records

- Read legacy `.workflow` `prd.md`, `design.md`, `implement.md`, `context.md`,
  `outcome.md`, `STATUS`, and pointers when recovery is explicitly requested.
- Use `scripts/migrate_workflow_task.py` for an explicit, idempotent migration.
  It copies into an OpenSpec change, writes a migration report, and never deletes
  or mutates the source task.
- Never write new requirements, tasks, status, or evidence into `.workflow/` as a
  shadow of an OpenSpec change.
- Read `.trellis/` records only for historical recovery. Never execute a Trellis
  script, install an injector, or write into `.trellis/`.

## Legacy `.trellis/` Repositories

`.trellis/` is a read-only historical format. Read its records only for recovery;
never write into `.trellis/`, run its scripts, or install its injectors.

## Context Loading Contract

Use three context tiers:

| Tier | When loaded | Contents |
| --- | --- | --- |
| Project context | Session start | Project identity, workflow rules, and OpenSpec change index |
| Change selection | Session start or resume | Exactly one OpenSpec change id; legacy path only in recovery mode |
| Change package | Activation or dispatch | Inlined AC text, design decisions, invariants, file bounds, and exact checks |

The change package is derived from OpenSpec artifacts and is not a second durable
record. Refresh it after requirement clarification, plan approval, slice completion,
Inlining is the point: a fresh worker receives bounded conclusions and exact checks, not only a path list.
review findings, and cross-session resume. When a harness cannot bind a pointer to a
session, use explicit change ids and bounded artifact sections as the compatibility
mode and record the limitation.

Paths alone are only acceptable for files the worker genuinely has to open itself.
The package must carry the conclusions needed for a fresh worker to start cold.

## Routing Ownership

| Need | Primary capability | Destination |
| --- | --- | --- |
| Resume context | OpenSpec change id + status read | Existing OpenSpec change |
| Recover legacy context | compatibility reader | `.workflow` or `.trellis` read-only |
| Clarify intent | `clarify-requirements` + observable ACs | OpenSpec `proposal.md` and `specs/` |
| Model domain | domain modeling | OpenSpec specs/design or rare ADR |
| Design solution | `plan-solution` + relevant specialists | OpenSpec `design.md` |
| Plan execution | `plan-solution` + test strategy | OpenSpec `tasks.md` |
| Implement behavior | TDD workflow | Code and tests |
| Review independently | `review-implementation` + code review | `artifacts/review.md` or bounded review output |
| Verify and record | repository checks + risk-specific checks | `artifacts/verification.md` |
| Reduce complexity | Ponytail review | Code, then re-verification |
| Preserve learning | evidence promotion step | OpenSpec artifacts or project docs |

Do not run Matt `to-spec` or `to-tickets` as a parallel record system. Their output
belongs in the active OpenSpec change. Do not use Ponytail minimal checks to replace
required repository checks.

## Source Trust

When sources disagree, use this order:

1. Running code, tests, and externally verified behavior.
2. Project specs (`openspec/specs/`, or legacy `.workflow/spec/` / `.trellis/spec/`)
   and accepted ADRs.
3. Active OpenSpec proposal, specs, design, tasks, and verification artifacts.
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
