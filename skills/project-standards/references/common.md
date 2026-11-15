# Common Project Standards

This reference covers rules that apply regardless of stack. It is deliberately
small; project documentation replaces it wherever they differ.

## Discover Before Deciding

- Read `AGENTS.md`, contribution guidance, and the nearest project instructions.
- Read build and dependency manifests before assuming a language version, a
  framework, a data-access library, or a test runner.
- Find the real verification commands in build files, CI, or contributor docs.
  Do not substitute a generic command that the project does not run.
- Identify generated and vendored paths, then leave them untouched.
- Record the selected rule sources and revisions in the standards brief.

## Change Shape

- Make the smallest coherent change that satisfies the accepted criteria.
- Preserve public behavior, interfaces, data formats, and error contracts unless
  the slice explicitly changes them.
- Match the local naming, package layout, error type, and logging style.
- Prefer deletion and reuse over new abstraction. Do not add a layer for a single
  call site.
- Do not upgrade dependencies, reformat unrelated files, or migrate tooling as a
  side effect.

## Correctness And Boundaries

- Validate untrusted input at the boundary where the project expects it.
- Keep authorization and tenant/data-scope checks on the backend; never trust a
  client-provided scope or ordering decision.
- Preserve transaction boundaries and failure behavior. Surface partial-failure
  risk rather than hiding it with a broad retry.
- Keep secrets, credentials, private identifiers, and production data out of
  code, fixtures, logs, and shared references.
- Treat concurrency claims as hypotheses until a test, constraint, or database
  behavior supports them.

## Verification And Evidence

- Add or update a test at the project's existing seam before relying on the
  change.
- Run the narrowest relevant checks first, then the project's prescribed broader
  check when the slice or handoff asks for it.
- Record the exact command and result. Distinguish `PASS`, `FAIL`, and
  `UNVERIFIED`; never present an unexecuted check as evidence.
- Prefer observable evidence over prose: test name, assertion, query plan,
  constraint, log, or reproducible command.
- Report gaps, skipped checks, and residual risk in the handoff.

## Standards Brief Template

```text
Selected sources: <absolute paths and revision/commit>
Project facts: <runtime, framework, data access, build and test commands>
Required rules: <short, slice-specific list>
Project overrides: <where the repository differs from a reference>
Verification: <commands and evidence required>
Unknowns: <UNVERIFIED items>
```
