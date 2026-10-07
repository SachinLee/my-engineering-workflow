# Spec Delta

## Purpose

Provides one reliable compatibility boundary for OpenSpec-first engineering work, so new tasks have one canonical change while historical workflow records remain recoverable without unsafe writes or ambiguous state.

## ADDED Requirements

### Requirement: Resolve one canonical task mode
The system SHALL resolve the current project into exactly one mode: OpenSpec canonical, legacy workflow recovery, legacy Trellis read-only, unconfigured, or blocked.

#### Scenario: OpenSpec project with one selected change
- **WHEN** an OpenSpec root exists and the requested change status is valid
- **THEN** the system returns OpenSpec canonical mode with that change as the source of truth

#### Scenario: Multiple active changes without an explicit selection
- **WHEN** OpenSpec reports more than one active change and no change identifier was supplied
- **THEN** the system returns `OPENSPEC_STATUS: BLOCKED` and lists the available change identifiers

#### Scenario: OpenSpec dependency is unavailable
- **WHEN** a new task is requested but the OpenSpec executable is missing, too old, or returns invalid structured output
- **THEN** the system returns `OPENSPEC_STATUS: BLOCKED` with an actionable installation or repair message and does not create a new `.workflow` task

### Requirement: Preserve legacy workflow recovery
The system SHALL read existing `.workflow` pointers and task artifacts for recovery without treating them as the canonical source for newly created work.

#### Scenario: Existing legacy workflow task
- **WHEN** no OpenSpec canonical change is selected and a valid `.workflow/CURRENT.md` or task directory exists
- **THEN** the system returns legacy workflow mode, identifies the task path, and permits read-only recovery

#### Scenario: Explicit migration of a legacy task
- **WHEN** the user explicitly requests migration for a legacy workflow task
- **THEN** the system creates one OpenSpec change containing mapped requirements, design, tasks, context, verification, and a migration report

#### Scenario: Migration fails
- **WHEN** any source artifact is unreadable, the target change is invalid, or verification fails during migration
- **THEN** the system reports a blocked migration, leaves every source artifact byte-for-byte unchanged, and does not claim the migration succeeded

### Requirement: Keep Trellis historical records read-only
The system SHALL allow inspection of legacy `.trellis` artifacts but SHALL never execute Trellis scripts, install Trellis injectors, or write under `.trellis`.

#### Scenario: Legacy Trellis task without workflow records
- **WHEN** `.trellis/tasks/` exists and no canonical OpenSpec change or `.workflow` task is selected
- **THEN** the system returns legacy Trellis read-only mode and exposes same-name historical artifacts for inspection

#### Scenario: Attempted Trellis mutation
- **WHEN** a route, installer, migration, or archive action would execute a Trellis script or write `.trellis`
- **THEN** the operation is rejected with a deterministic failure and the Trellis directory remains unchanged

### Requirement: Expose structured status for all modes
The system SHALL expose machine-readable mode, source, change identifier, blocking reason, and migration status without requiring prompt injection or human-readable CLI parsing.

#### Scenario: Status query succeeds
- **WHEN** a caller requests compatibility status for a project
- **THEN** the result contains stable keys for `mode`, `source`, `change`, `status`, and `reason` where applicable

#### Scenario: Status query is ambiguous or malformed
- **WHEN** the project state cannot be safely classified
- **THEN** the result uses a blocking status and includes enough structured detail for the caller to request a specific change or repair action
