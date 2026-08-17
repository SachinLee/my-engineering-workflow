---
name: clarify-requirements
description: Convert an ambiguous software request into scoped, observable acceptance criteria in the active Trellis task. Use before planning complex work, when business intent is unclear, or when another AI session needs a reliable requirement handoff.
---

# Clarify Requirements

Improve the active Trellis `prd.md`; do not create a second specification.
Combine codebase discovery, Matt-style grilling, and ECC-style observable
acceptance criteria.

## Clarify

1. Read the current request, active task, related code, tests, specs, and prior
   decisions before asking technical questions.
2. Separate discovered technical facts from product assumptions. Never infer a
   business rule only from code or naming.
3. Ask one question at a time. Ask only when the answer materially changes
   behavior, scope, risk, compatibility, or verification.
4. Challenge overloaded domain terms. If a stable glossary exists, use it; if
   a term is newly resolved, propose a focused `CONTEXT.md` update.
5. Stop questioning when the requested outcome is observable and the remaining
   assumptions are safe to record.

## Write The PRD

Maintain these sections in `prd.md`:

- Goal
- Current behavior and problem
- In scope
- Out of scope
- Actors and affected systems
- Assumptions and constraints
- Domain terms, when relevant
- Acceptance criteria
- Open or blocking decisions

Write acceptance criteria as `AC-001`, `AC-002`, and so on. Each criterion must
name the scenario, action, expected observable result, prohibited side effect
when meaningful, and verification method.

Example:

```markdown
### AC-001: Reject unauthorized export

- Scenario: a signed-in user requests another account's export
- Action: submit the export request
- Expected: return the repository's standard forbidden response
- Must not: disclose whether the other account exists
- Verification method: API integration test
```

## Escalate By Risk

- Use PRD-only planning for a small, well-understood change.
- Add `design.md` when interfaces, data flow, compatibility, security, rollout,
  or meaningful alternatives need an explicit decision.
- Add `implement.md` when ordering, checkpoints, validation commands, or rollback
  steps matter.
- Add an ADR only for a hard-to-reverse, surprising decision made through a real
  tradeoff. Link it from `design.md`; do not duplicate its rationale.

## Finish

Report confirmed requirements, recorded assumptions, and any blockers. Do not
start risky or irreversible implementation while a blocking decision remains.
