# Engineering Workflow Development

This repository is a thin orchestration layer. Keep upstream Trellis, Matt
Pocock skills, and Ponytail content in their own repositories.

Rules:

- Keep canonical skills under `skills/`.
- Do not vendor upstream skill bodies. Route to them by capability name.
- Trellis is the canonical owner of project task state and durable records.
- Add or change contract tests before changing workflow behavior.
- Keep skill bodies concise; put shared governance in
  `skills/run-engineering-workflow/references/` so installed skills retain it.
- Keep OMP agents provider-independent by referring to `@role` aliases.
- Keep Pi agents provider-independent by omitting `model`; Pi then inherits the
  active/default model unless the user or project supplies an override.
- Keep Claude Code plugin agents under root `agents/`; current Claude discovers
  that directory by convention, so do not add obsolete per-file `agents`
  entries to `.claude-plugin/plugin.json`.
- Never overwrite Trellis `trellis-implement` or `trellis-check` agents. Their
  project files and hooks own Claude context injection.
- Preserve `Both` as Codex + OMP for compatibility; use `All` for Codex + OMP +
  Claude Code + Pi.
- Keep implementation and final review in separate model contexts when the
  active harness supports it.
- Update `manifests/upstreams.lock.json` only after reviewing upstream changes.
- Never weaken correctness, security, accessibility, or required verification
  to satisfy a minimalism rule.
