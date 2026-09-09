# Workflow Governance

Read this reference when routing a task, resolving conflicts between extensions,
or deciding where durable information belongs.

## Artifact Ownership

Trellis is the canonical owner of task state and durable delivery records. Store
one fact in one authoritative place. Do not duplicate task facts across
workflow systems.

| Artifact | Canonical owner | Purpose |
| --- | --- | --- |
| `prd.md` | Active Trellis task | Requirements, scope, assumptions, acceptance criteria |
| `design.md` | Active Trellis task | Technical design, alternatives, compatibility, rollout |
| `implement.md` | Active Trellis task | Ordered execution and validation plan |
| `outcome.md` | Active Trellis task | Actual delivery, evidence, review, deviations, remaining risk |
| `.trellis/spec/` | Trellis project knowledge | Durable conventions and prevention rules |
| `.trellis/workspace/` | Trellis developer journal | Session summaries and task pointers |
| `CONTEXT.md` | Domain glossary | Stable business vocabulary only |
| `docs/adr/` | Architecture decisions | Hard-to-reverse decisions and rationale |
| Code and tests | Git | Executable implementation and behavioral proof |

## Context Loading Contract

Use three context tiers:

| Tier | When loaded | Contents |
| --- | --- | --- |
| Project context | Session start | Project identity, workflow rules, and relevant spec index |
| Task pointer | Session start or resume | One task path, phase, status, and short summary |
| Task package | Activation or dispatch | Role- and slice-scoped artifact sections, file bounds, invariants, and checks |

The task package is derived from the active Trellis artifacts and is not a second
durable record. Refresh it after requirement clarification, plan approval, slice
completion, review findings, and cross-session resume. When Trellis cannot resolve a
named task package, use explicit task paths and bounded artifact sections as the
compatibility mode and record the limitation.

Issue trackers may link to a Trellis task, but must not duplicate its design and
implementation record.

## Routing Ownership

| Need | Primary capability | Destination |
| --- | --- | --- |
| Resume context | Trellis start/continue/session insight | Existing task |
| Clarify intent | Matt-style grilling + observable ACs | `prd.md` |
| Model domain | Matt domain modeling | `CONTEXT.md`, rare ADR |
| Design solution | `plan-solution` + relevant specialists | `design.md` |
| Plan execution | `plan-solution` + test strategy | `implement.md` |
| Implement behavior | Trellis before-dev + ECC TDD | Code and tests |
| Review independently | `review-implementation` | Findings returned to main session |
| Verify and record | Trellis check + risk-specific checks | `outcome.md` |
| Reduce complexity | Ponytail review | Code, then re-verification |
| Preserve learning | Trellis update-spec | `.trellis/spec/` |

Do not call Matt `to-spec`, `to-tickets`, or `implement` when Trellis already
owns the task. Do not use Ponytail minimal checks to replace required ECC or
repository checks.

## Source Trust

When sources disagree, use this order:

1. Running code, tests, and externally verified behavior.
2. Trellis project specs and accepted ADRs.
3. Active task PRD, design, implementation plan, and outcome.
4. Git history and reviewed issue references.
5. Trellis journals and explicit handoffs.
6. Raw AI conversations and generated memory entries.

Promote reusable knowledge only after checking code, tests, or the user.

## OMP Model Roles

Use role aliases so the workflow remains provider-independent:

| Responsibility | OMP role | Reason |
| --- | --- | --- |
| Main orchestration and user questions | `@default` | Holds task context and user interaction |
| Solution planning | `@plan` | Dedicated architecture/planning role |
| Trellis `trellis-implement` | `@task` | Cost-effective coding subagent under a reviewed plan |
| Trellis `trellis-check` | `@advisor` | Different model/context performs quality remediation |
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

Keep Trellis `trellis-implement` and `trellis-check` definitions native to the
project created by `trellis init --claude`. Replacing them would bypass or
weaken Trellis hook injection, `implement.jsonl` / `check.jsonl` loading, and
their fallback context protocol. TDD for the Claude implementation agent is
therefore enforced through reviewed RED/GREEN slices in `implement.md`, the
dispatch prompt, Trellis checking, and independent review; do not state that it
automatically loads an ECC skill when its tool list does not include `Skill`.

Launching the main session with `claude --model sonnet` normally separates the
implementation model from the Opus planning/review agents. When the main
session is Opus, subagent review is still a fresh context but not cross-model.

## Review Independence

For standard behavior changes and every critical task, the final reviewer must
use a fresh context and, when available, a different model role from the
implementer. The reviewer reports findings; the main session owns remediation,
re-verification, and the final delivery claim. A model never approves its own
unverified work merely because no separate reviewer is available.
