# Design

## Context

The approved proposal makes OpenSpec the canonical record for new work while this repository keeps its own quality gates. The installed OpenSpec CLI is `1.14.1`, requires Node `v22.14.0` in this environment, and exposes structured JSON for `list`, `status`, `instructions`, and `validate`. Its `spec-driven` schema recognizes only `proposal`, `specs`, `design`, and `tasks`; repository-specific `context.md` and `verification.md` therefore belong under the change-local `artifacts/` directory.

## Goals / Non-Goals

**Goals:**

- Resolve one explicit OpenSpec change without guessing from arbitrary directories.
- Return deterministic structured results for canonical, legacy, unconfigured, and blocked states.
- Migrate a legacy `.workflow` task by copy-transform-verify while leaving all source bytes unchanged.
- Make doctor and contract tests able to exercise the same compatibility boundary without user directories or shell interpolation.
- Preserve existing quality routing and user-controlled archive semantics.

**Non-Goals:**

- Reimplement the OpenSpec CLI or vendor its commands and skills.
- Automatically initialize OpenSpec or migrate every historical task.
- Make `.workflow` a second writable task system or make `.trellis` writable.
- Infer an active task by scanning arbitrary change directories when the CLI reports ambiguity.

## Decisions

### Use a small Python adapter around structured CLI calls

`openspec_compat.py` will own executable discovery, version comparison, bounded subprocess execution, JSON parsing, project-mode detection, active-change selection, and migration. Calls use `subprocess.run` with an argument list, a project-root working directory, a finite timeout, and no shell. This reuses the repository's existing Python diagnostics surface and avoids duplicating the adapter in four client-specific installers.

Alternative rejected: parsing human-readable CLI output. It is unstable and would make status routing dependent on formatting. Alternative rejected: Node-only implementation. The existing doctor and filesystem validation are Python, and Python gives a direct test seam without adding a package dependency.

### Resolve project state with explicit precedence

The adapter first checks for an OpenSpec root (`openspec/config.yaml` or the CLI's resolved root), then uses `openspec list --json` and `openspec status --change <id> --json`. An explicit change id always wins. Without one, zero active changes is canonical-but-unselected, one active change is selected, and multiple active changes are `BLOCKED`. If an OpenSpec root exists but the executable or JSON contract is unavailable, the result is `BLOCKED`; it must not silently create a new `.workflow` task.

If no OpenSpec root exists, the adapter checks `.workflow` pointers/tasks before `.trellis/tasks`. Legacy modes are read-only. An unconfigured project is reported as unconfigured so the caller can ask for explicit initialization consent.

### Make migration transactional and idempotent

Migration accepts a source task directory and a target change directory under the project OpenSpec changes root. It validates that source and target are inside their expected roots, refuses an existing target unless its migration report matches the same source hash, reads source files as UTF-8, writes all converted artifacts into a sibling temporary directory, validates required outputs, then renames the completed directory into place. It never deletes, renames, or writes the source.

The report records source path, source SHA-256, mapping version, target change id, and result. Repeating the same migration returns the existing successful result; a target with different source metadata is blocked. A failure removes only the temporary target.

### Keep repository-specific artifacts outside OpenSpec's graph

The standard OpenSpec artifact graph remains authoritative for proposal/specs/design/tasks. `artifacts/context.md`, `artifacts/verification.md`, and `artifacts/migration-report.md` hold bounded dispatch and evidence required by this repository. The router and agents reference the selected change id and these paths; they do not create `.workflow/tasks/` for new work.

## Risks / Trade-offs

- [OpenSpec JSON schema changes] -> Require a minimum CLI version, validate required keys, and return `BLOCKED` on incompatible output instead of guessing.
- [A change is created but has no tasks] -> Treat `no-tasks` as planning/incomplete and rely on OpenSpec status before apply.
- [Migration loses semantics from free-form legacy Markdown] -> Preserve original artifacts in the report/context, mark converted requirements as migrated, and require human review before archive.
- [Windows path and encoding differences] -> Use `pathlib`, UTF-8 with explicit error handling, and temporary directories under the target project root.
- [Existing in-progress user changes] -> Keep modifications scoped to declared adapter, tests, docs, skills, and the selected OpenSpec change; do not reset unrelated files.

## Migration Plan

1. Add the adapter and contract tests with temporary project fixtures.
2. Update router, governance, agents, doctor, and installer checks.
3. Run OpenSpec validation, Node contracts, Python adapter tests, and OMP startup tests.
4. Record actual results in `artifacts/verification.md` and stop at `awaiting-acceptance`.
5. Only after explicit user acceptance may the OpenSpec archive command be run.

Rollback is a source-level revert of the adapter/router/installer changes. Existing `.workflow` and `.trellis` directories are not modified by the migration implementation, so legacy recovery remains available during rollback.
