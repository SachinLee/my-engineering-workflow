# Specialist Routing

This file is the single shared reference for how the main agent coordinates
specialists. [quality-profiles.md](quality-profiles.md) owns acceptance criteria,
evidence, risk profiles and the single review budget; the host owns scheduling,
model choice and tool availability. This file adds scheduling guidance only.

## Route By Task Shape

The main agent coordinates, integrates, and owns the evidence trail. It selects
one or more of these modes by task shape; this is not a mandatory stage pipeline,
and no mode runs merely because a stage template lists it:

- `explore`: read-only investigation of an unfamiliar seam. Read-only exploration
  may precede a formal change; it creates no task or plan state.
- `research`: external documentation, upstream sources, or API contracts that
  the current session cannot settle locally.
- `implement`: a bounded write slice on the host's preferred writer.
- `consult`: a second opinion on a decision the main agent is unsure about.
  Consultation is not an additional review gate and does not spend the review
  budget.
- `review`: the one independent final review required by the delivery budget.

When the main agent already holds the context — a small scoped edit, a
documentation change, a targeted fix it just investigated, or a context-heavy
document update — it does the work directly. Delegation buys fresh context or
parallelism; it is not a ceremony. Read-only exploration may come before a
formal change exists, but formal implementation and the final independent
review keep the OpenSpec handoff: the inlined context package, `May modify:` /
`Verification:` for writers, `Review mode:` / `Review scope:` / `Evidence:` for
review, and one review budget. On-demand routing must not weaken, bypass, or
replace the independent review, and the main session's self-check never stands
in for it. If no independent `workflow-reviewer` can be invoked, record
`UNVERIFIED` and report the gap.

## Pi

Pi's specialists come from pi-subagents. Activation and discovery are separate
from dispatch. When the live tool list already contains `subagent`, use it
directly and do not call a loader. Only when `subagent` is absent and
`subagents_enable` is present — a fresh, unrestricted session on a model that
accepts a new tool mid-conversation — call `subagents_enable({})`: it starts no
work and exposes `subagent`, `bg_wait`, and `subagent_supervisor` on the next
model request. Other models start with `subagent` active and no loader. A
session whose recorded history predates the extension may expose neither, and
installing plus reloading alone does not add them; inspect the live tool list
instead of assuming delegation.

Per-launch parameters follow the installed pi-subagents runtime schema:
`agent`, `task`, and `output` are top-level fields; `agentScope`, `context`,
and `timeoutMs` are `options` keys (for example `options.agentScope: "both"`
and `options.context: "fresh"`). `output` is a top-level field, not an option:
the runtime rejects `options.output` with `'output' is a top-level field, not
an option.` Give it a path to persist findings to an authorized artifact, or
`false` to return them to the main session. Pass
`options.context: "fresh"` for explore, research, implement, and review so the
specialist sees only the bounded handoff rather than the parent conversation.
`oracle` has `defaultContext: fork`; an explicit
fresh context always wins and is required for an independent second opinion.
`async` is the default: wait for the completion event or report once. A failed
run is a terminal status to record; never silently switch execution mode,
re-run the slice, or downgrade the review.

Native helpers have their own boundaries:

- `scout` includes `bash` and `write`, so it is not a hard read-only role. Its
  default output is `context.md`; give it an explicit write boundary.
- `researcher` needs the pi-web-access provider (`web_search`,
  `fetch_content`, `get_search_content`, `source_check`) and defaults to
  `research.md`; without that provider, research is unavailable rather than
  silently local.
- `oracle` declares a read-only acceptance role, but that is a prompt and
  acceptance constraint, not a sandbox: its toolset still includes `bash` and
  file reads. Give it a bounded read scope, and never treat its advice as the
  formal independent review.

Direct output to the main session or to the active change's authorized
artifacts. Never let a specialist write `context.md`, `plan.md`, or
`research.md` as shadow state outside that change. If `subagent`, a trusted
project definition, or the independent reviewer is unavailable, keep
implementation and deterministic checks in the main session and report
`UNVERIFIED`; the main agent's self-review cannot claim an independent review.

## Claude Code

Project agents under `agents/` supply `workflow-planner`,
`workflow-implementer`, and `workflow-reviewer` natively. Use them on demand
for formal slices; the single review budget and the bounded handoff are
unchanged.

## OpenCode

The Slim orchestrator is the only scheduler. It may dispatch `explorer`,
`designer`, `fixer`, and `oracle` on demand. Formal implementation routes
through Slim `fixer`, and the one independent review routes through Slim
`oracle`; the active preset supplies their models. Each specialist prompt
carries the repository procedure plus the bounded OpenSpec handoff (`Active
change:`, slice, context package, and `May modify:` / `Verification:` or
`Review mode:` / `Review scope:` / `Evidence:`). Native workflow agents remain
available for explicit or manual use, but model-free parent inheritance is not
evidence that Slim's role model ran; never copy a preset model ID into a
managed agent. Record `UNVERIFIED` when the role or its effective model cannot
be observed.

## Codex

Codex shares this repository's skills. An installed agent file or an enabled
feature does not prove runtime discovery or invocation: native role support is
conditional on the installed CLI version and that project's configuration.
Only report native role capability after discovery and a real invocation are
verified in that client version. Otherwise the main session may implement
directly under its documented limits, but it must record `UNVERIFIED` for the
missing independent review; the main agent's self-review never stands in for
it. There is no `codex exec --agent` command; never invent a flag to force role
routing. Skills-only loading is not a claim that native subagents run.
