# Spring + MyBatis-Plus Standards

Use this reference only when the project already uses Spring and MyBatis-Plus.
Read the project's MyBatis-Plus version, Spring Boot version, JDK, migrations,
and existing mapper style first. The project's version and configuration win.
Official references:

- Wrapper and condition construction: <https://baomidou.com/en/guides/wrapper/>
- Block-attack plugin: <https://baomidou.com/plugins/block-attack/>

Do not introduce JPA, an extra Repository layer, a new plugin, or a dependency
upgrade to satisfy this reference.

## Trusted Query Scope

- Build wrappers from backend-controlled fields. Never concatenate a request
  parameter into SQL text, a column name, an `orderBy`, an `apply` fragment, or
  `last`.
- `${}` substitutes text directly and is an injection risk; `#{}` binds a
  parameter. Use parameter binding for every value.
- `{0}` inside wrapper fragments such as `apply` is still a bound parameter
  placeholder, not string interpolation. Keep the fragment itself constant and
  backend-controlled; `apply("date_format(created_at,'%Y-%m-%d') = {0}", day)` is
  acceptable only when the expression is fixed and `day` is bound.
- `last` appends a raw final SQL segment. Use it only for a constant,
  backend-controlled clause that cannot be expressed otherwise. Never pass user
  input, and never use it to append `;` or a second statement.
- Prefer lambda method references for compile-time checks of Java property
  references. Explicit column constants reduce scattered strings but do not
  validate database column names; verify those through SQL or database checks.
  Whitelist sortable/filterable columns instead of accepting client names.
- Keep tenant, organization, and data-scope predicates in the backend. Do not
  offer a client toggle that removes them.
- Select only needed columns for wide tables or read paths; avoid `SELECT *` when
  the project already uses explicit projections.

## Partial Updates And Null Semantics

- `updateById` and entity-based updates skip `null` fields under the default
  field strategy. That is useful for partial updates but cannot clear a column.
- To set a column to SQL `NULL`, use an explicit update wrapper such as
  `update(null, Wrappers.<Entity>lambdaUpdate().eq(Entity::getId, id).set(Entity::getNote, null))`
  (or the project's equivalent), and verify the generated SQL. Do not rely on an
  entity with a null field.
- Empty strings, zero, and `null` are different states. Decide and test which one
  the API means; do not normalize them silently.
- Field-level `@TableField(updateStrategy = FieldStrategy.ALWAYS)` is acceptable
  only for a specific justified field with tests proving the intended writes.
  Never set a global `field-strategy`/update strategy of `ALWAYS`, and do not
  apply it blanket-wide: it makes accidental null overwrites easy and weakens
  partial-update safety.
- Include the intended optimistic version or update predicate in the `WHERE`
  clause. Do not update by a broad predicate when one row is intended.
- Audit fields need an explicit policy: who fills them, on insert or update, and
  whether a logical delete or restore updates them. Do not assume a fill handler
  runs for every custom SQL path.

## SQL Fragments And Reuse

- Keep reusable fragments small and parameterized. A fragment that accepts raw
  column names or ordering is not reusable safely.
- Do not move business authorization into a shared fragment that callers can
  bypass.
- Prefer wrapper composition over string concatenation. If XML is the project's
  convention, follow its namespace, result-map, and parameter conventions.
- Check generated SQL in a test or project logging when a wrapper becomes
  non-trivial.

## Pagination

- Use MyBatis-Plus pagination (`Page`/`IPage`) with the project's configured
  `PaginationInnerInterceptor`; do not hand-build `LIMIT` from request values.
- Set and verify a maximum page size, overflow behavior, and a deterministic
  order. Unordered pagination is not stable evidence.
- Treat total-count queries as potentially expensive; use the project's count
  optimization or a separate count only when the existing configuration supports
  it.
- Test the first page, a middle page, the last/empty page, and an oversized page
  request when the slice changes list behavior.

## Audit And Logical Delete

- Follow the project's existing `@TableLogic`/logic-delete field. Reads, updates,
  and uniqueness rules must account for the deleted marker.
- Understand whether unique indexes include the delete marker; a logical delete
  can otherwise block re-creation. Prefer a database constraint that matches the
  intended behavior.
- Use the framework's delete methods or an explicit wrapper. Do not bypass logical
  delete with raw SQL unless the slice explicitly owns a restore/purge operation.
- Record audit timestamps/operators through the project's fill mechanism, and
  verify custom updates that bypass entity fill.
- A purge or restore path needs its own authorization, audit, and transaction
  evidence; it is not a normal delete.

## Transactions And Concurrency

- Put `@Transactional` on the public service boundary that owns the unit of work.
  Remember that self-invocation bypasses the proxy; move the call to another bean
  or use the project's established pattern.
- Declare rollback behavior for checked exceptions when the project relies on it.
  Do not swallow an exception and commit a partial write.
- Keep transactions short; avoid remote calls, file I/O, and waits inside them
  when the project permits.
- Prefer a unique constraint and a narrow update predicate for races. Use
  `@Version` with `OptimisticLockerInnerInterceptor` only when the table already
  has a version column and the project uses that pattern; handle the zero-row
  update as a conflict.
- Do not add process-wide, distributed, or table locks by default. A lock needs a
  named contention scenario, timeout, ownership rule, and failure behavior.
- Do not add the block-attack plugin or another interceptor as a blanket policy.
  If the project already uses it, keep it configured; if the slice needs
  full-table update/delete protection, treat that as a scoped project decision
  with tests.

## Verification And Database Evidence

- Prefer actual database evidence: a real database, the project's database, or its
  approved container/test database, rather than mocks, for SQL semantics. If that
  is unavailable, mark the claim
  `UNVERIFIED` instead of inferring it from a mock.
- Cover the changed behavior directly: trusted predicates, partial update and
  explicit null clearing, logical delete, pagination boundaries, audit fill,
  optimistic conflict, and rollback.
- Capture actual SQL or database state only with project-approved logging. Do not
  enable verbose SQL logging in production configuration for a test.
- Check migrations, indexes, and constraints that the behavior depends on. A
  passing unit test does not prove a missing unique index.
- Report the exact test/command and its result; distinguish unit, integration,
  and manual database evidence.
