# Java Project Standards

Read the project's build files and `AGENTS.md` first. Use the JDK, framework,
formatter, linter, and dependency versions the project already declares; this
reference does not prescribe an upgrade or a default stack.

## Baseline

- Confirm the compiler release and any toolchain configuration before using newer
  language features.
- Follow the project's formatter/linter configuration. Do not reformat unrelated
  code.
- Keep package layout, visibility, and naming consistent with nearby code.
- Do not add a dependency when the JDK or an existing library covers the need.
- Leave generated sources and generated SQL/mapper artifacts untouched unless the
  slice owns their source of truth.

## Persistence Boundaries

- Use the persistence technology already present. Do not default to JPA, and do
  not add an extra Repository layer when the project queries its mapper or
  existing boundary directly.
- When MyBatis-Plus is present, read `spring-mybatis-plus.md`; it is the authority
  for wrappers, partial updates, pagination, logical delete, and SQL fragments.
- Keep database constraints and migrations consistent with the code. A service
  check does not replace a unique or foreign-key constraint when one is possible.

## Types, Nulls, And Errors

- Prefer explicit types at API boundaries; avoid raw collections and `null`
  returns that callers cannot distinguish from absence.
- Treat nullable columns and wrapper types deliberately. Do not silently convert
  missing data to `0`, `""`, or a default timestamp.
- Throw the project's domain or framework exception with context. Do not catch an
  exception and continue as if the operation succeeded.
- Do not log secrets, full request bodies, credentials, or personal data.
- Preserve exception contracts that callers and transactions rely on.

## Concurrency And Transactions

- Do not add a lock or a synchronized block without a stated contention scenario,
  ownership rule, timeout, and failure path.
- Prefer database constraints, optimistic versions, and short transactions over
  process-wide locks.
- Keep remote calls, file I/O, and user interaction out of a transaction when the
  project allows it.
- Test the claimed behavior with a real or project-approved database when the
  slice changes transactional, locking, or constraint behavior.

## Tests

- Use the project's existing test framework, naming, fixtures, and database
  strategy.
- Assert observable behavior rather than implementation wiring.
- For persistence changes, include evidence of the generated SQL or database
  result when the slice changes query or update semantics; otherwise state why
  that evidence is unavailable.
- Run the project's formatter, compiler, and focused tests; report the exact
  commands and outcomes.
