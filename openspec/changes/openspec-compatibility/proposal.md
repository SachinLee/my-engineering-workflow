# Proposal

## Why

The repository currently treats `.workflow/` as the canonical task and delivery record, while OpenSpec is now the requested specification and change lifecycle. Without a single canonical OpenSpec change, new work can split state across two systems, make recovery ambiguous, and weaken the existing review and acceptance gates.

## What Changes

- **BREAKING** Make `openspec/` the canonical source for new task proposals, requirement deltas, designs, implementation tasks, and archive lifecycle.
- Add a structured compatibility adapter for OpenSpec capability/status checks and explicit legacy migration.
- Route new work through an explicitly selected OpenSpec change and return `OPENSPEC_STATUS: BLOCKED` for missing, invalid, or ambiguous OpenSpec state.
- Preserve old `.workflow/` records as read-only recoverable history until explicitly migrated.
- Preserve old `.trellis/` records as read-only historical input; never execute Trellis scripts or write the directory.
- Keep this repository's risk routing, TDD, independent review, verification evidence, and user-controlled acceptance gates.
- Add contract coverage and installer/doctor checks for Codex, Claude Code, OMP, and Pi.

## Capabilities

### New Capabilities

- `workflow-compatibility`: Resolve canonical OpenSpec state, recover legacy records safely, and migrate legacy workflow tasks without source mutation or dual writes.

### Modified Capabilities

- None.

## Impact

Affected surfaces include `skills/run-engineering-workflow`, workflow governance and quality skills, planner/implementer/reviewer agents, `scripts/doctor.py`, `scripts/install.ps1`, OMP/Pi/Claude entrypoints, contract tests, behavior fixtures, and new files under `openspec/` plus the change-local `artifacts/` directory. The implementation consumes the installed OpenSpec CLI but does not vendor it or modify user legacy records.
