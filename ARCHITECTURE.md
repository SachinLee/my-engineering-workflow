# Architecture

## Layers

1. Trellis is the kernel for task state, scoped context, specifications, and
   session continuity.
2. Matt-style practices improve requirements, domain language, module seams,
   and Spec-versus-Standards review.
3. ECC supplies TDD, specialist analysis, security, and verification.
4. Ponytail supplies a final pressure against unnecessary complexity.
5. This repository supplies routing, ownership, profiles, independent review,
   OMP and Claude Code role adapters, and the evidence format.

## Design Rules

- Store one fact in one authoritative place.
- Pass file paths between AI sessions instead of copying full context.
- Treat conversations and generated memories as leads, not policy.
- Select quality checks by consequence and change shape.
- Preserve proof of what ran, including failures and unavailable checks.
- Prefer wrappers and adapters over upstream forks.

## Workflow

```text
request
  -> Trellis task
  -> clarify requirements
  -> plan solution in design.md and implement.md
  -> ECC TDD inside Trellis execution
  -> Trellis and ECC verification
  -> independent correctness/security/complexity review
  -> remediation and re-verification
  -> outcome evidence
  -> spec update and Trellis finish
```

## OMP Roles

```text
main @default
  -> planning agent @plan
  -> Trellis implementation agent @task
  -> Trellis check agent @advisor
  -> review agent @advisor
  -> escalation @default or @slow
```

The OMP overlay limits skill candidates. Custom planning/review agents use
`autoloadSkills`; the Trellis implement dispatch explicitly reads
`skill://tdd-workflow` while preserving Trellis context injection.
Provider-specific model IDs remain user config.

## Claude Code Roles

```text
main configured model
  -> workflow-planner (opus)
  -> native Trellis trellis-implement
  -> native Trellis trellis-check
  -> workflow-reviewer (opus, read-only)
  -> main-session remediation and evidence
```

The custom Claude agents are plugin-owned. Trellis implementation/check agents
and hooks remain project-owned so `implement.jsonl` / `check.jsonl` context
injection continues to work. Starting the main session with Sonnet creates a
Sonnet implementation plus Opus planning/review split; an Opus main session
provides context separation but not model separation.
