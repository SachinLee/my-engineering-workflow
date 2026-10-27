# Architecture

## Layers

1. `openspec/` is the canonical record system for new changes: proposal, specs, design, tasks, bounded context, verification, and archive status. It is a file convention backed by the OpenSpec CLI, with no automatic injection.
2. `.workflow/` remains a recoverable legacy record system; `.trellis/` remains read-only historical input. Neither is a new-work authority.
3. Matt-style practices improve requirements, domain language, module seams, TDD, and Spec-versus-Standards review.
4. Ponytail supplies a final pressure against unnecessary complexity.
5. This repository supplies routing, ownership, profiles, independent review, Codex, OpenCode, OMP, Claude Code, and Pi adapters, plus migration and evidence tooling.

## Design Rules

- The shared quality contract owns delivery rules: acceptance criteria, evidence, risk profiles, and the review budget. The host owns scheduling, model choice, and tool availability. Adapters map roles; they never restate quality.
- Store one fact in one authoritative place: OpenSpec for formal work; eligible fast work creates no task state, legacy records only for recovery.
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
  -> classify current request before discovery (quality-profiles.md#simple-work-fast-path)
     -> eligible: host-native edit -> diff + smallest relevant checks -> report in conversation
        (no task records; scope/risk grows -> stop, preserve diff/checks, confirm formal change)
     -> formal: continue below; selected change continuation keeps its record
  -> read openspec/config.yaml and discover unarchived changes (openspec_compat
     list_changes, read-only; environment errors are blocked states, not "no match")
  -> match session intent against the candidates; recommend create or reuse and
     stop for an explicit user confirmation before creating or reusing
  -> if absent, recover .workflow or .trellis read-only records without writing them
  -> clarify requirements (proposal.md with checkboxed ACs and specs/*.md)
  -> plan solution in design.md, tasks.md, and artifacts/context.md
  -> user approval, OpenSpec change -> in_progress (task frontier when split)
  -> Matt TDD with an inlined 上下文包 (host's preferred writer, or main session
     when the host has no specialist policy; workflow-implementer when critical)
  -> repository verification (budget: quality-profiles.md)
  -> one independent workflow-reviewer for Standards / Spec and
     correctness/security/complexity (standard and critical)
  -> batch blocking repairs, affected checks, at most one focused follow-up
     (remaining blockers or expanded scope -> user decision, not an automatic loop)
  -> artifacts/verification.md evidence reuse (finish adds no tests or reviewers)
  -> OpenSpec change -> awaiting-acceptance, hand the verification list to the user
  -> user verify, or bounce back to in_progress with a new verification round
  -> (user) accept, then archive via /archive-task
```

## Record Layout

See `skills/run-engineering-workflow/references/workflow-governance.md` for the
canonical OpenSpec tree and the `.workflow`/`.trellis` legacy read-only mappings.
## Shared Installation

`skills/` owns canonical source. The installer publishes six skills and the assembled
OpenSpec helper once to `~/.agents/skills/`, regardless of Scope or Harness. Codex,
OMP, Pi, and OpenCode discover that directory natively; Claude uses per-skill directory links
(junctions on Windows, symlinks elsewhere). Scope defaults to User and controls
only harness adapters: agents, commands, OMP config, launcher, review gate, and
the OpenCode agent/command set.
Project scope shares skill versions across projects. Both remains Codex + OMP.

Selected harness legacy copies, including target-project copies in Project scope,
are backed up outside skill discovery under `~/.agents/backups/my-engineering-workflow/`
before removal. Shared updates preserve changed content there too. Unknown links
and linked parents fail preflight; correct Claude links and unchanged published
content are idempotent. Other projects require their own explicit migration.
Doctor checks the shared helper, Claude link destinations, legacy shadow entries,
and the scope-specific adapters. OpenSpec records stay project-local.

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
agents. Pi agents omit a fixed `model` and inherit the active Pi model; user or
trusted-project overrides can differ per agent. They never use OMP `@role` aliases.
If `@narumitw/pi-subagents` is not installed, planning, bounded implementation,
and independent review fall back to the main session and must disclose the loss of
fresh-context review.

## OpenCode Roles

```text
Slim Orchestrator (sole orchestrator, sole scheduler)
  -> explorer (bounded read-only investigation)
  -> designer (UI, layout, visual hierarchy)
  -> fixer (bounded implementation of an approved slice)
  -> oracle (second opinion on material uncertainty)
  -> workflow-planner / workflow-implementer / workflow-reviewer
     (strict formal slices and the single independent review only)
  -> main-session remediation, evidence, and the delivery claim
```

Slim is the only orchestrator. The workflow agents are specialists it may call,
not a parallel control plane; adding a second orchestrator or a second review pass
breaks the per-slice writer rule and the one-review-budget rule. Review still comes
from the single budget in `quality-profiles.md`.
Formal implementation is routed through Slim `fixer` and the single independent
review through Slim `oracle`; those roles select models from the active OMO-Slim
preset. The model-free workflow agent files are procedures, not model bindings.
If a role cannot be invoked or its effective model cannot be verified, report
`UNVERIFIED` instead of treating parent-model inheritance as role routing.

## Adapter Capabilities And Ownership

The six canonical skills are installer-managed and shared; adapters add managed
links or native discovery and never fork the bodies. Model selection stays
user-owned: Claude agent definitions carry `opus` and `sonnet` labels a user may
remap, Pi and OpenCode agents omit `model` so user overrides can differ, and OMP roles resolve
through the user's `modelRoles`. Codex and OpenCode consume the shared skills directory, and
subagent capability is asserted only after independent verification for that client
version. No adapter may promise independent review a client cannot provide; report
`UNVERIFIED` with the precise gap instead.
