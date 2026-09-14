# Architecture

## Layers

1. `.workflow/` is the record system: task state, requirements, design, plan,
   context read list, evidence, and journal. It is a file convention with no
   code, no CLI, and no automatic injection.
2. Matt-style practices improve requirements, domain language, module seams,
   TDD, and Spec-versus-Standards review.
3. Ponytail supplies a final pressure against unnecessary complexity.
4. This repository supplies routing, ownership, profiles, independent review,
   Codex, OMP, Claude Code, and Pi adapters, and the evidence format.

## Design Rules

- Store one fact in one authoritative place.
- Pass file paths between AI sessions instead of copying full context.
- Load state with reads, never with head-of-input injection. An injector that
  places volatile content before the conversation history invalidates the
  prompt cache for the entire session on every turn; the measured cost of one
  phase-change injection was a full re-bill of a 140k-token history to deliver a
  few hundred tokens of state.
- Treat conversations and generated memories as leads, not policy.
- Select quality checks by consequence and change shape.
- Preserve proof of what ran, including failures and unavailable checks.
- Prefer wrappers and adapters over upstream forks.
- Every durable artifact must be readable by a fresh session that knows only the
  pointer file. If a fact cannot be found on disk, it was never decided.

## Workflow

```text
request
  -> read .workflow/CURRENT.md or by-session pointer
  -> create or resume task directory
  -> clarify requirements (prd.md with checkboxed ACs)
  -> plan solution in design.md, implement.md, and context.md
  -> user approval, STATUS -> in_progress
  -> Matt TDD (main session by default, workflow-implementer when critical)
  -> repository verification + Matt code-review
  -> independent correctness/security/complexity review
  -> remediation and re-verification
  -> outcome evidence (one row per AC)
  -> STATUS -> done, journal line, archive, clear pointer
```

## Record Layout

See `skills/run-engineering-workflow/references/workflow-governance.md` for the
authoritative `.workflow/` tree and the legacy `.trellis/` read-only mapping.

## OMP Roles

```text
main @default
  -> planning agent @plan
  -> implementation agent @task
  -> review agent @advisor
  -> escalation @default or @slow
```

The OMP overlay limits skill candidates, and `autoloadSkills` gives each agent
its method skills because nothing is injected from the project any more.
Provider-specific model IDs remain user config.

## Claude Code Roles

```text
main configured model
  -> workflow-planner (opus)
  -> workflow-implementer (sonnet, critical only)
  -> workflow-reviewer (opus, read-only)
  -> main-session remediation and evidence
```

All three agents are plugin-owned. Dispatch carries the task path, the
`context.md` read list, and the approved RED/GREEN slices, since no project hook
injects them. Starting the main session with Sonnet creates a Sonnet
implementation plus Opus planning/review split; an Opus main session provides
context separation but not model separation.

## Pi Roles

```text
main configured model
  -> workflow-planner via blocking subagent (optional pi-subagents package)
  -> workflow-implementer via blocking subagent (critical or justified slices)
  -> workflow-reviewer via blocking subagent (optional, read-only)
  -> main-session remediation and evidence
```

The workflow installs only its five skills and three provider-independent Pi
agents. Pi agents omit a fixed `model` and inherit the active Pi model; they
never use OMP `@role` aliases. If `@narumitw/pi-subagents` is not installed,
planning, bounded implementation, and independent review fall back to the main
session and must disclose the loss of fresh-context review.
