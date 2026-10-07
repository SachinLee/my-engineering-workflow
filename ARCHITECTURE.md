# Architecture

## Layers

1. `openspec/` is the canonical record system for new changes: proposal, specs, design, tasks, bounded context, verification, and archive status. It is a file convention backed by the OpenSpec CLI, with no automatic injection.
2. `.workflow/` remains a recoverable legacy record system; `.trellis/` remains read-only historical input. Neither is a new-work authority.
3. Matt-style practices improve requirements, domain language, module seams, TDD, and Spec-versus-Standards review.
4. Ponytail supplies a final pressure against unnecessary complexity.
5. This repository supplies routing, ownership, profiles, independent review, Codex, OMP, Claude Code, and Pi adapters, plus migration and evidence tooling.

## Design Rules

- Store one fact in one authoritative place: OpenSpec for new work, legacy records only for recovery.
- Pass bounded context packages between AI sessions instead of copying full context or passing path lists alone.
- Load state with reads, never with head-of-input injection. An injector that places volatile content before the conversation history invalidates the prompt cache for the entire session.
- Treat conversations and generated memories as leads, not policy.
- Select quality checks by consequence and change shape.
- Preserve proof of what ran, including failures and unavailable checks.
- Prefer wrappers and adapters over upstream forks.
- Every durable artifact must be readable by a fresh session that knows only the active change pointer. If a fact cannot be found on disk, it was never decided.
- Write human-facing artifacts in the user's language, Chinese by default; keep identifiers, paths, commands, log text, OpenSpec filenames, and status tokens English.
- A dispatch is ready only when its 上下文包 inlines what the main session already concluded. Paths alone push the survey onto the worker.
- Split at the smallest level that matches execution: 切片 and task items inside a change, then multiple changes for separately shippable outcomes.

## Workflow

```text
request
  -> read openspec/config.yaml and discover unarchived changes (openspec_compat
     list_changes, read-only; environment errors are blocked states, not "no match")
  -> match session intent against the candidates; recommend create or reuse and
     stop for an explicit user confirmation before creating or reusing
  -> if absent, recover .workflow or .trellis read-only records without writing them
  -> clarify requirements (proposal.md with checkboxed ACs and specs/*.md)
  -> plan solution in design.md, tasks.md, and artifacts/context.md
  -> user approval, OpenSpec change -> in_progress (task frontier when split)
  -> Matt TDD with an inlined 上下文包 (main session by default,
     workflow-implementer when critical)
  -> repository verification + Matt code-review
  -> independent correctness/security/complexity review
  -> remediation and re-verification
  -> artifacts/verification.md evidence (one row per AC)
  -> OpenSpec change -> awaiting-acceptance, hand the verification list to the user
  -> user verify, or bounce back to in_progress with a new verification round
  -> (user) accept, then archive via /archive-task
```

## Record Layout

See `skills/run-engineering-workflow/references/workflow-governance.md` for the
canonical OpenSpec tree and the `.workflow`/`.trellis` legacy read-only mappings.
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

The workflow installs only its six skills and three provider-independent Pi
agents. Pi agents omit a fixed `model` and inherit the active Pi model; they
never use OMP `@role` aliases. If `@narumitw/pi-subagents` is not installed,
planning, bounded implementation, and independent review fall back to the main
session and must disclose the loss of fresh-context review.
