# Project AGENTS Entry Template

Copy the relevant sections into the target repository's `AGENTS.md`, replacing
placeholders with verifiable facts. Keep only rules that are true for that
project; delete the rest. Do not include credentials, private identifiers,
customer data, or business source.

```markdown
# Project Engineering Rules

## Scope
This file governs <repository or module>. Read the nearest nested `AGENTS.md`
before changing that area.

## Stack Baseline
- Language/runtime and version: <from manifest>
- Framework and data access: <from manifest>
- Build, format, lint, and test commands: <exact commands>
- Generated or vendored paths that must not be edited: <paths>

## Workflow
- Canonical workflow skills: <install command or shared location>
- Project standards selection: read the project standards brief for this slice;
  load only relevant references.
- Verification: <focused command> then <broader command required by the project>
- Database or environment evidence: <how to run it safely>

## Project-Specific Rules
- <rule with a source and an observable check>
- <override where this repository intentionally differs from a generic standard>

## Boundaries
- Do not add dependencies, lock mechanisms, or framework migrations unless the
  accepted slice requires them.
- Do not log secrets or personal data; do not copy private project code into
  shared artifacts.
- Report missing or conflicting rules instead of inventing them.
```

Keep the entry short enough to stay accurate. Link to detailed project documents
by relative path rather than duplicating them.
