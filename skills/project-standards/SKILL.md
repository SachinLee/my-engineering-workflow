---
name: project-standards
description: Select and carry the target project's own standards and stack-specific references into planning, implementation, and review without inventing policy or adding gates.
---

# Project Standards

Use this skill when a workflow slice needs project or technology rules for
implementation or review. It supplies a selection method and portable
references; it does not replace the target project's documentation, tooling, or
executable checks.

## Precedence And Sources

Apply rules in this order:

1. The user's explicit instruction and the target platform's requirements.
2. The target repository's `AGENTS.md`, contribution guide, architecture notes,
   specs, and accepted decisions.
3. A relevant reference from this skill.
4. Generic workflow defaults.

Read the project's manifests and configuration before choosing a reference:
language and runtime version, framework, data-access library, compiler and
formatter settings, test commands, and migration tooling. The repository's
written rules and checks win over a reference example. When a source is missing,
conflicting, or unreadable, report the gap; do not invent a rule or claim the
standards were loaded. Never copy private project code or identifiers into a
shared skill.

## Select only what applies

1. Derive the actual change surfaces from the acceptance criteria: language,
   framework, persistence layer, UI, infrastructure, and test environment.
2. Always read `references/common.md`.
3. Read `references/java.md` only for JVM work.
4. Read `references/spring-mybatis-plus.md` only when the project already uses
   Spring and MyBatis-Plus. Do not introduce JPA, an extra repository layer, or a
   new persistence framework to satisfy a reference.
5. Go, Rust, Python, and Vue have no detailed reference in this first phase.
   Use the target project's conventions and tooling for them, and state that this
   skill adds no stack-specific rules.
6. Do not load every reference by default. Record which sources and revisions
   were selected, or mark the selection as incomplete.

## Produce A Bounded Standards Brief

Before dispatching implementation or review, turn the selection into a short
brief for the handoff:

- Inline the rules that apply to this slice; do not make a fresh child read a
  whole reference to recover them.
- Give absolute paths to any file the child must open for new information.
- Name project overrides and the evidence that proves them (config keys,
  dependency versions, scripts).
- Name the verification commands and the database evidence the slice requires.
- Separate required rules from suggestions, and mark unknown facts as
  `UNVERIFIED`.

A fresh child may not inherit the parent's project or skill context, so the brief
must stand alone. Keep it proportional to the slice; a path list alone is not a
brief.

## Apply In The Workflow

- **Plan:** add the selected brief to the slice context package, test seam, and
  verification plan.
- **Implement:** follow the selected rules and report deliberate deviations with
  their reason and evidence.
- **Review:** check the same selected rules under the existing Standards axis;
  do not create a separate review, model route, or additional review round.

## Limits

This skill adds no scheduler, agent role, model choice, coverage quota, or
independent review gate. It does not authorize blanket database locks, global
plugins, or project-wide migrations. If project rules conflict with a reference,
follow the project and surface the conflict; never weaken correctness, security,
accessibility, or required verification to match a generic rule.
