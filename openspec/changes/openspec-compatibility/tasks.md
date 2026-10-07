# Tasks

## 1. Freeze the compatibility boundary

- [x] 1.1 Add the Python OpenSpec adapter with bounded `list --json` and `status --json` execution, version checks, required-key validation, and deterministic canonical/legacy/blocked results; verify with adapter unit tests using fake executables and temporary project roots.
- [x] 1.2 Add explicit migration from a legacy `.workflow` task using copy-transform-verify, source hashing, idempotency checks, and failure cleanup; verify source bytes remain unchanged after success, repeat, and failure cases.

## 2. Lock contracts before routing changes

- [x] 2.1 Extend `tests/contracts.test.js` and add Python adapter tests for canonical selection, multiple active changes, missing CLI, malformed JSON, legacy `.workflow`, legacy `.trellis`, unconfigured projects, and forbidden Trellis mutation; verify `npm test` and the Python test command pass.
- [x] 2.2 Add the OpenSpec change-local `artifacts/context.md` dispatch package and keep the OpenSpec proposal/spec/design/tasks graph valid; verify `openspec status --change openspec-compatibility --json` reports all standard artifacts done and `openspec validate openspec-compatibility --json` passes.

## 3. Route the workflow through OpenSpec

- [x] 3.1 Update the main workflow skill and governance reference to use the selected OpenSpec change as the new-task source of truth, preserve legacy recovery, and reject ambiguous or unavailable OpenSpec state; verify static contracts cover `OPENSPEC_STATUS: BLOCKED`, explicit change selection, and no new `.workflow/tasks` creation.
- [x] 3.2 Update planning, implementation, review, evidence, and archive skills plus all owned agent definitions to use change-local `artifacts/context.md` and `artifacts/verification.md`, while preserving TDD, independent review, and user-controlled acceptance; verify the agent and skill contracts pass.

## 4. Integrate clients and diagnostics

- [x] 4.1 Update `scripts/doctor.py`, `scripts/doctor.ps1`, and `scripts/install.ps1` to check OpenSpec availability/version and project initialization without silently running `openspec init`; verify WhatIf and diagnostic checks return actionable blocked output.
- [x] 4.2 Update OMP, Claude Code, Pi, and Codex entrypoint metadata/configuration to expose the OpenSpec workflow without provider-specific model coupling; verify installation and OMP startup tests pass.

## 5. Document and verify delivery

- [x] 5.1 Update README and behavior fixtures with canonical source, legacy migration, Trellis read-only, rollback, and acceptance rules; verify documented commands and fixture names match the implementation.
- [x] 5.2 Run OpenSpec validation, Node contracts, Python adapter tests, OMP startup tests, and a final diff review; write real command results, review findings, and residual risks to `artifacts/verification.md`, then set the task to `awaiting-acceptance`.

## Workflow follow-up

- After the user explicitly accepts the verified implementation, archive the OpenSpec change with `openspec archive openspec-compatibility`.
- Do not archive automatically and do not write a new `.workflow` task for this implementation.
