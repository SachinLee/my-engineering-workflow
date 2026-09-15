# Engineering Workflow Development

This repository is a thin orchestration layer. Keep upstream Matt Pocock skills
and Ponytail content in their own repositories.

Rules:

- Keep canonical skills under `skills/`.
- Do not vendor upstream skill bodies. Route to them by capability name.
- `.workflow/` is the canonical owner of project task state and durable
  records. It is a file convention, not a program: no CLI, no hooks, no
  per-turn context injection.
- Never reintroduce head-of-input state injection. Task state reaches the model
  through file reads, which keep the prompt-cache prefix stable.
- `.trellis/` is a read-only legacy record format. Never call Trellis scripts,
  write into `.trellis/`, or install its injectors from this workflow.
- Write human-facing task artifacts (prd/design/implement/context/outcome/journal/
  and tickets) in the user's language, Chinese by default, including headings and
  field labels. Keep identifiers, paths, commands, log text, `STATUS` keys, and
  status tokens in English so they stay greppable.
- Planning writes a 上下文包 per dispatchable slice into `implement.md`. A handoff
  that only lists paths is not dispatch-ready; complete the package instead of
  letting a subagent redo the survey.
- Split at the smallest level that matches execution: 切片 inside one session,
  `tickets/` across sessions or writers, multiple task directories for separately
  shippable outcomes.
- Add or change contract tests before changing workflow behavior.
- Keep skill bodies concise; put shared governance in
  `skills/run-engineering-workflow/references/` so installed skills retain it.
- Keep OMP agents provider-independent by referring to `@role` aliases.
- Keep Pi agents provider-independent by omitting `model`; Pi then inherits the
  active/default model unless the user or project supplies an override.
- Keep Claude Code plugin agents under root `agents/`; current Claude discovers
  that directory by convention, so do not add obsolete per-file `agents`
  entries to `.claude-plugin/plugin.json`.
- All three agents (`workflow-planner`, `workflow-implementer`,
  `workflow-reviewer`) are owned and installed by this repository. Keep their
  root, `.omp/`, and `.pi/` definitions in sync through `scripts/install.ps1`.
- Preserve `Both` as Codex + OMP for compatibility; use `All` for Codex + OMP +
  Claude Code + Pi.
- Keep implementation and final review in separate model contexts when the
  active harness supports it.
- Update `manifests/upstreams.lock.json` only after reviewing upstream changes.
- Never weaken correctness, security, accessibility, or required verification
  to satisfy a minimalism rule.
