---
name: plan-solution
description: Design a traceable technical solution and execution plan for an active Trellis task. Use after requirements are clarified and before implementation, especially for behavior changes, multi-file work, public interfaces, data flow, migrations, security-sensitive work, or tasks another AI session must execute.
---

# Plan Solution

Turn an accepted Trellis `prd.md` into an implementation-ready solution. Keep
technical decisions in `design.md` and ordered execution in `implement.md`.
Do not implement production code while using this skill.

When OMP is available, run this skill in the `workflow-planner` agent on the
`@plan` role. In Claude Code, use this repository's `workflow-planner` agent on
Opus. Requirement questions still return to the interactive main session; the
planning agent must not guess product intent.

## Confirm Readiness

1. Read `prd.md`, related code and tests, applicable `.trellis/spec/`, and prior
   ADRs before designing.
2. Verify that the goal, in scope, out of scope, assumptions, and acceptance
   criteria are explicit.
3. If a decision still changes required behavior or scope, return to
   `clarify-requirements`. Do not hide a requirement question inside a technical
   plan.
4. Select the `lightweight`, `standard`, or `critical` quality profile.

## Find The Smallest Sound Design

Before proposing new code, check in order:

1. Existing project behavior, helpers, modules, and conventions.
2. Standard library and native platform capabilities.
3. Already-installed dependencies.
4. The smallest new module or interface that owns the behavior correctly.

Use Matt-style deep-module reasoning when a boundary is changing: identify the
public interface, invariants, error modes, and test seam. Prefer one deep module
over multiple pass-through layers. Simplicity cannot remove required security,
data integrity, compatibility, observability, accessibility, or rollback.

## Write design.md

For standard work, create `design.md` when the task changes an interface, data
flow, module boundary, persistence model, or meaningful technical decision.
For critical work, `design.md` is required.

Include only applicable sections:

- Context and current behavior
- Proposed solution and change boundary
- Components and responsibilities
- Public interfaces and invariants
- Data flow and state transitions
- Error handling and failure modes
- Security and privacy considerations
- Compatibility and migration
- Observability
- Alternatives considered and rejection reasons
- Rollout and rollback
- Open technical risks

Do not copy acceptance criteria into `design.md`; reference their IDs. Create an
ADR only for a hard-to-reverse and surprising decision produced by a real
tradeoff, then link it instead of duplicating its rationale.

## Write implement.md

For standard and critical work, create an ordered `implement.md`. Organize work
as vertical slices that leave the repository verifiable after each slice.

Use this shape:

```markdown
### Slice 1: AC-001 - Reject unauthorized export

- Behavior: observable result delivered by this slice
- Code boundary: modules or interfaces expected to change
- Test seam: public boundary used to prove behavior
- RED: targeted test and intended failure
- Implementation: minimum production change
- GREEN: targeted passing command
- Validation: lint, typecheck, integration, build, or manual check
- Dependencies: prerequisite slices or external decisions
- Rollback: how to remove or disable this slice safely
```

#### Subagent Handoff

Every slice dispatched through OMP or another agent-capable harness must include:

```markdown
Active task: .trellis/tasks/<task-id>/
Assigned slice: Slice N / AC-XXX
Phase: implement

Required artifacts:
- prd.md#AC-XXX
- design.md#relevant-section
- implement.md#slice-N

Allowed files:
- path/to/production-file
- path/to/test-file

Forbidden files:
- unrelated paths
- global task state

Invariants:
- behavior or contract that must remain true

Verification commands:
- focused test command
- required lint, typecheck, integration, or build command

Escalation conditions:
- decision or change outside the approved boundary

Evidence to return:
- files changed
- RED/GREEN commands and outcomes
- remaining risks or unavailable checks
```

The main session supplies the task path and slice. The subagent must not search all
Trellis tasks, choose a different slice, change `CURRENT TASK`, or create another
handoff record. If the task path or assigned slice is missing or unreadable, the
subagent returns an invalid status and does not edit production code.

Map every required acceptance criterion to at least one slice or an explicit
non-code verification step. Do not use `AC-001` as a placeholder when the PRD
has different IDs.

## Lightweight Planning

For documentation, configuration, or an isolated low-risk change, Trellis may
remain PRD-only. Record an explicit solution sketch, affected files, runnable
check, and the reason `design.md` / `implement.md` are unnecessary in `prd.md`.
Skipping files is allowed; skipping the planning decision is not.

## Review The Plan

Before handing off:

- Confirm every required AC has implementation or verification coverage.
- Confirm expected changed files are inside the declared scope.
- Confirm test seams exercise public behavior rather than internals.
- Confirm dependency ordering, migration, rollout, and rollback where relevant.
- Challenge speculative abstractions, dependencies, configuration, and fallback
  paths through Ponytail's simplicity ladder.
- Record unresolved technical risk instead of presenting guesses as decisions.

Finish by summarizing the selected profile, artifacts written, major decisions,
and whether the task is ready to enter Trellis `in_progress`.
