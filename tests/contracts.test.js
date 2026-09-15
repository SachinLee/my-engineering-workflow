const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const skillNames = [
  "run-engineering-workflow",
  "clarify-requirements",
  "plan-solution",
  "review-implementation",
  "finish-with-evidence",
  "archive-task",
];
const agentNames = [
  "workflow-planner.md",
  "workflow-implementer.md",
  "workflow-reviewer.md",
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

test("skills have valid names, useful descriptions, and UI prompts", () => {
  for (const name of skillNames) {
    const skill = read(`skills/${name}/SKILL.md`);
    const metadata = read(`skills/${name}/agents/openai.yaml`);

    assert.match(skill, new RegExp(`^name: ${name}$`, "m"));
    assert.match(skill, /^description: .{40,}$/m);
    assert.doesNotMatch(skill, /TODO|\[TODO/i);
    assert.match(metadata, new RegExp(`\\$${name}\\b`));
  }
});

test("workflow has no Trellis runtime dependency", () => {
  const forbidden =
    /trellis-implement|trellis-check|trellis_subagent|trellis init|trellis update|trellis mem|get_context\.py|task\.py|trellis-before-dev|trellis-brainstorm|trellis-update-spec|trellis-session-insight|\.trellis\/workflow\.md/;
  const targets = [
    ...skillNames.map((name) => `skills/${name}/SKILL.md`),
    "skills/run-engineering-workflow/references/workflow-governance.md",
    "skills/run-engineering-workflow/references/quality-profiles.md",
    "commands/engineering-workflow.md",
    "config/omp-workflow.yml",
    "scripts/doctor.py",
    "scripts/install.ps1",
    ...agentNames.map((file) => `agents/${file}`),
    ...agentNames.map((file) => `.omp/agents/${file}`),
    ...agentNames.map((file) => `.pi/agents/${file}`),
  ];

  for (const target of targets) {
    assert.doesNotMatch(read(target), forbidden, `${target} still depends on Trellis`);
  }
});

test("legacy .trellis records are read-only and never executed", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );

  assert.match(router, /\.trellis\/tasks\//);
  assert.match(router, /never run a Trellis\n   script|never execute a Trellis script/i);
  assert.match(governance, /## Legacy `\.trellis\/` Repositories/);
  assert.match(governance, /read-only historical format/i);
  assert.match(governance, /never\s+write into `\.trellis\/`/i);
  assert.match(governance, /implement\.jsonl|check\.jsonl/);
});

test("task state is read on demand, never injected per turn", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const architecture = read("ARCHITECTURE.md");
  const agents = read("AGENTS.md");

  assert.match(router, /Never install or emulate a per-turn context injector/);
  assert.match(router, /invalidates the cache for the whole session/);
  assert.match(governance, /## Prompt Cache Constraint/);
  assert.match(governance, /head-of-request\ninjection|head-of-request injection/);
  assert.match(architecture, /never with head-of-input injection/i);
  assert.match(agents, /Never reintroduce head-of-input state injection/);
});

test("workflow policies define one owner for every durable artifact", () => {
  const ownership = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );

  for (const artifact of [
    "prd.md",
    "design.md",
    "implement.md",
    "context.md",
    "STATUS",
    "outcome.md",
    ".workflow/spec/",
    ".workflow/journal.md",
    "by-session/",
    "archive/",
    "CONTEXT.md",
    "docs/adr/",
  ]) {
    assert.match(ownership, new RegExp(artifact.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  assert.match(ownership, /\.workflow\/` is the canonical owner/i);
  assert.match(ownership, /do not duplicate/i);
});

test("router preserves .workflow state and delegates quality work", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");

  assert.match(router, /\.workflow\/CURRENT\.md/);
  assert.match(router, /by-session/);
  assert.match(router, /planning/);
  assert.match(router, /in_progress/);
  assert.match(router, /clarify-requirements/);
  assert.match(router, /plan-solution/);
  assert.match(router, /Matt `tdd`/);
  assert.match(router, /diagnosing-bugs/);
  assert.match(router, /`code-review`/);
  assert.match(router, /review-implementation/);
  assert.match(router, /finish-with-evidence/);
  assert.match(router, /workflow-planner/);
  assert.match(router, /workflow-implementer/);
  assert.match(router, /workflow-reviewer/);
  assert.match(router, /lightweight.*main session/s);
  assert.match(router, /standard.*main session/s);
  assert.match(router, /critical.*full gated path/s);
  assert.match(router, /at most one live writer/);
  assert.match(router, /After 10 minutes without progress/);
  assert.match(router, /Do not automatically re-dispatch/);
  assert.match(router, /do not poll `hub jobs`, `hub list`/);
  assert.match(router, /no CLI, no daemon, and no script interpreter dependency/);
  assert.match(router, /do not initialize one silently/i);
});

test("acceptance and archival belong to the user", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const finish = read("skills/finish-with-evidence/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const architecture = read("ARCHITECTURE.md");
  const agents = read("AGENTS.md");

  assert.match(governance, /## Acceptance And Archival/);
  assert.match(
    governance,
    /The user accepts and archives\. The agent never does it on its own initiative/
  );
  assert.match(governance, /awaiting-acceptance/);
  assert.match(governance, /phase: done` means "the user accepted"/);
  assert.match(finish, /## Hand It Back For Acceptance/);
  assert.match(finish, /You do not accept the work, and you do not archive it/);
  assert.match(finish, /phase: awaiting-acceptance/);
  assert.match(finish, /do not write `phase: done`/);
  assert.match(finish, /复验轮次/);
  assert.match(router, /does not set `phase: done`/);
  assert.match(router, /print the commands instead of running them/);
  assert.match(
    router,
    /Do not archive a task, set `phase: done`, or clear pointers/
  );
  assert.match(architecture, /\(user\) accept, then archive/);
  assert.match(agents, /Acceptance and archival belong to the user/);
  assert.match(governance, /archive-task` command performs these steps/);
});

test("archive-task is gated on user acceptance and owns the move", () => {
  const skill = read("skills/archive-task/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const command = read("commands/archive-task.md");
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const finish = read("skills/finish-with-evidence/SKILL.md");
  const overlay = read("config/omp-workflow.yml");
  const installer = read("scripts/install.ps1");
  const doctor = read("scripts/doctor.py");

  assert.match(skill, /^name: archive-task$/m);
  assert.match(skill, /## Verify Acceptance First/);
  assert.match(skill, /phase: awaiting-acceptance/);
  assert.match(skill, /ARCHIVE_STATUS: REFUSED/);
  assert.match(skill, /ARCHIVE_STATUS: ARCHIVED/);
  assert.match(skill, /ARCHIVE_STATUS: PARTIAL/);
  assert.match(skill, /Do\nnot run extra checks to earn the archive|do not run extra checks to earn the archive/i);
  assert.match(skill, /then move the task directory into/);
  assert.match(skill, /Committing, pushing, publishing, and deleting an archived task stay out of/);
  assert.match(command, /\/archive-task|archive-task/);
  assert.match(command, /\$ARGUMENTS/);

  // both entry points delegate; neither duplicates the procedure
  assert.match(router, /invoke `archive-task`/);
  assert.match(finish, /invoke `archive-task`/);
  assert.match(overlay, /^    - archive-task$/m);
  assert.match(installer, /"archive-task"/);
  assert.match(installer, /"archive-task\.md"/);
  assert.match(doctor, /"archive-task",/);
  assert.match(skill, /Ensure `\.workflow\/archive\/` exists/);
  assert.match(skill, /rename the source instead of moving it/);
  assert.match(skill, /force UTF-8/);
  assert.match(governance, /New-Item -ItemType Directory -Force -Path \.workflow\\archive/);
  assert.match(governance, /AppendAllText/);
});

test("solution planning separates design decisions from execution steps", () => {
  const skill = read("skills/plan-solution/SKILL.md");

  assert.match(skill, /prd\.md/);
  assert.match(skill, /design\.md/);
  assert.match(skill, /implement\.md/);
  assert.match(skill, /## Write context\.md/);
  assert.match(skill, /备选方案/);
  assert.match(skill, /数据流/);
  assert.match(skill, /回滚/);
  assert.match(skill, /测试接缝/);
  assert.match(skill, /AC-001/);
  assert.match(skill, /do not implement/i);
});

test("clarification writes observable acceptance criteria into the task record", () => {
  const skill = read("skills/clarify-requirements/SKILL.md");

  assert.match(skill, /prd\.md/);
  assert.match(skill, /AC-001/);
  assert.match(skill, /- \[ \] AC-001/);
  assert.match(skill, /范围内/);
  assert.match(skill, /范围外/);
  assert.match(skill, /验证方法/);
  assert.match(skill, /one question at a time/i);
  assert.match(skill, /STATUS/);
  assert.match(skill, /by-session/);
});

test("finish skill records actual evidence without inventing results", () => {
  const skill = read("skills/finish-with-evidence/SKILL.md");

  assert.match(skill, /outcome\.md/);
  assert.match(skill, /RED.*GREEN/s);
  assert.match(skill, /git diff/);
  assert.match(skill, /do not invent/i);
  assert.match(skill, /\.workflow\/spec\//);
  assert.match(skill, /one row for every `- \[ \] AC-NNN`/);
  assert.match(skill, /## 独立复核/);
  assert.match(skill, /workflow-reviewer/);
});

test("profiles provide lightweight, standard, and critical gates", () => {
  const profiles = read(
    "skills/run-engineering-workflow/references/quality-profiles.md",
  );
  for (const profile of ["Lightweight", "Standard", "Critical"]) {
    assert.match(profiles, new RegExp(`^## ${profile}$`, "m"));
  }
  assert.match(profiles, /independent review/i);
  assert.match(profiles, /@task/);
  assert.match(profiles, /Do not run both by default/);
});

test("independent review leads with evidence-backed findings", () => {
  const review = read("skills/review-implementation/SKILL.md");

  assert.match(review, /fresh context/i);
  assert.match(review, /acceptance criterion/i);
  assert.match(review, /CRITICAL/);
  assert.match(review, /file and tight line reference/i);
  assert.match(review, /must not commit/i);
  assert.match(review, /must not.*claim final delivery/is);
});

test("OMP adapter limits skills and separates model roles", () => {
  const config = read("config/omp-workflow.yml");
  const planner = read(".omp/agents/workflow-planner.md");
  const implementer = read(".omp/agents/workflow-implementer.md");
  const reviewer = read(".omp/agents/workflow-reviewer.md");

  assert.match(config, /includeSkills:/);
  assert.match(config, /workflow-planner: "@plan"/);
  assert.match(config, /workflow-implementer: "@task"/);
  assert.match(config, /workflow-reviewer: "@advisor"/);
  assert.match(config, /workflow-implementer: "off"/);
  assert.doesNotMatch(config, /workflow-implementer:\s*false/);
  assert.match(config, /- diagnosing-bugs/);
  assert.match(config, /- grill-with-docs/);
  assert.match(config, /- tdd/);
  assert.match(config, /- code-review/);
  assert.match(config, /prewalk:[\s\S]*enabled: false/);
  assert.match(config, /maxConcurrency: 4/);
  assert.doesNotMatch(config, /maxRuntimeMs:/);
  assert.doesNotMatch(config, /agentIdleTtlMs:/);
  assert.doesNotMatch(config, /softRequestBudget:/);
  assert.doesNotMatch(config, /\*-code-review/);

  assert.match(planner, /model: "@plan"/);
  assert.match(planner, /autoloadSkills:.*plan-solution/);
  assert.match(implementer, /model: "@task"/);
  assert.match(implementer, /autoloadSkills:.*tdd/);
  assert.match(implementer, /IMPLEMENT_STATUS: INVALID/);
  assert.match(implementer, /May modify:/);
  assert.match(reviewer, /model: "@advisor"/);
  assert.match(reviewer, /autoloadSkills:.*review-implementation/);
  assert.doesNotMatch(reviewer, /tools:.*(?:write|edit)/);
  assert.match(reviewer, /REVIEW_STATUS: CLEAN/);
  assert.match(reviewer, /REVIEW_STATUS: INVALID/);
});

test("Pi adapter uses native agents without OMP role aliases", () => {
  const planner = read(".pi/agents/workflow-planner.md");
  const implementer = read(".pi/agents/workflow-implementer.md");
  const reviewer = read(".pi/agents/workflow-reviewer.md");
  const router = read("skills/run-engineering-workflow/SKILL.md");

  assert.match(planner, /^name: workflow-planner$/m);
  assert.match(planner, /^tools: .*\bedit\b.*\bwrite\b/m);
  assert.match(planner, /^thinkingLevel: high$/m);
  assert.match(planner, /capabilityManifest:/);
  assert.doesNotMatch(planner, /^model:/m);

  assert.match(implementer, /^name: workflow-implementer$/m);
  assert.match(implementer, /^tools: .*\bedit\b.*\bwrite\b/m);
  assert.match(implementer, /IMPLEMENT_STATUS: COMPLETE/);
  assert.doesNotMatch(implementer, /^model:/m);

  assert.match(reviewer, /^name: workflow-reviewer$/m);
  assert.match(reviewer, /^tools: read, grep, find, ls$/m);
  assert.match(reviewer, /verificationRoles: \[independent-review\]/);
  assert.doesNotMatch(reviewer, /^model:/m);
  assert.doesNotMatch(reviewer, /^tools:.*(?:bash|edit|write)/m);

  assert.match(router, /^## Pi Roles$/m);
  assert.match(router, /workflow-implementer/);
  assert.match(router, /agentScope.*both/i);
  assert.match(router, /does not use OMP `@role` aliases/i);
});

test("Claude agents own implementation without a foreign record system", () => {
  const implementer = read("agents/workflow-implementer.md");
  const planner = read("agents/workflow-planner.md");
  const reviewer = read("agents/workflow-reviewer.md");

  assert.match(implementer, /^model: sonnet$/m);
  assert.match(implementer, /^tools: Read, Write, Edit, Bash, Grep, Glob$/m);
  assert.match(implementer, /IMPLEMENT_STATUS: BLOCKED/);
  assert.match(planner, /^model: opus$/m);
  assert.match(reviewer, /^model: opus$/m);
  assert.doesNotMatch(reviewer, /^tools:.*(?:Write|Edit)/m);
});

test("OMP dispatches carry a bounded, explicit task handoff", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const planner = read(".omp/agents/workflow-planner.md");
  const implementer = read(".omp/agents/workflow-implementer.md");
  const reviewer = read(".omp/agents/workflow-reviewer.md");

  for (const field of ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]) {
    assert.match(router, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(router, /\.workflow\/tasks\/<task-id>\//);
  assert.match(router, /requested_model/);
  assert.match(router, /effective_model/);
  assert.match(router, /fallback/);
  for (const field of ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]) {
    assert.match(planner, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(planner, /PLANNING_STATUS: INVALID/);
  assert.match(planner, /do not[\s\S]{0,40}scan all task directories/i);
  for (const field of ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "May modify:", "Verification:"]) {
    assert.match(implementer, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  for (const field of ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "Review scope:", "Evidence:"]) {
    assert.match(reviewer, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(reviewer, /REVIEW_STATUS: INVALID/);
  assert.match(reviewer, /do not[\s\S]{0,40}scan all task directories/i);
});

test("OMP overlay preserves the full quality skill baseline", () => {
  const config = read("config/omp-workflow.yml");
  for (const skill of ["tdd", "code-review", "ponytail-review"]) {
    assert.match(config, new RegExp(`^    - ${skill}$`, "m"));
  }
  assert.match(config, /context mode|Context mode/);
});

test("behavior cases cover bounded context and fallback observability", () => {
  const fixture = JSON.parse(read("evals/workflow-cases.json"));
  assert.equal(fixture.schema_version, 3);
  const allowedHandoffFields = new Set([
    "Active task:",
    "Assigned slice:",
    "Phase:",
    "Read:",
    "Must preserve:",
    "May modify:",
    "Verification:",
    "Review scope:",
    "Evidence:",
  ]);
  for (const entry of fixture.cases) {
    assert.equal(typeof entry.name, "string");
    assert.equal(typeof entry.state, "string");
    assert.equal(typeof entry.expected_stage, "string");
    if (entry.required_handoff) {
      assert.ok(entry.required_handoff.length > 0);
      for (const field of entry.required_handoff) {
        assert.ok(allowedHandoffFields.has(field), `unknown handoff field: ${field}`);
      }
    }
  }
  const expectedHandoffs = new Map([
    ["planner-with-explicit-task", ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]],
    ["implementation-with-one-slice", ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "May modify:", "Verification:"]],
    ["review-with-diff-evidence", ["Active task:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "Review scope:", "Evidence:"]],
  ]);
  for (const [name, requiredFields] of expectedHandoffs) {
    const entry = fixture.cases.find((candidate) => candidate.name === name);
    assert.deepEqual(entry.required_handoff, requiredFields);
  }

  for (const name of [
    "no-current-task",
    "resume-existing-task",
    "planner-with-explicit-task",
    "implementation-with-one-slice",
    "review-with-diff-evidence",
    "missing-task-path",
    "named-task-context-unavailable",
    "model-fallback",
    "repository-without-records",
    "legacy-trellis-task",
    "per-turn-injector-proposed",
    "pointer-and-task-disagree",
    "await-acceptance-after-evidence",
    "user-acceptance-defect-bounces-task",
    "archive-request-without-acceptance",
    "archive-request-after-acceptance",
    "incomplete-ac-table-blocks-close",
    "dispatch-without-context-package",
    "multi-ticket-frontier",
  ]) {
    assert.ok(fixture.cases.some((entry) => entry.name === name), `missing behavior case for ${name}`);
  }
});

test("Claude Code plugin maps planning, implementation, and review", () => {
  const manifest = JSON.parse(read(".claude-plugin/plugin.json"));
  const planner = read("agents/workflow-planner.md");
  const reviewer = read("agents/workflow-reviewer.md");
  const command = read("commands/engineering-workflow.md");

  assert.equal(manifest.name, "my-engineering-workflow");
  assert.deepEqual(manifest.skills, ["./skills/"]);
  assert.deepEqual(manifest.commands, ["./commands/"]);
  assert.equal(manifest.agents, undefined);

  assert.match(planner, /^model: opus$/m);
  assert.match(planner, /^tools: .*Write.*Edit/m);
  assert.match(planner, /^skills:[\s\S]*run-engineering-workflow[\s\S]*plan-solution/m);
  assert.match(planner, /design\.md/);
  assert.match(planner, /implement\.md/);
  assert.match(planner, /Do not write production code/i);

  assert.match(reviewer, /^model: opus$/m);
  assert.match(reviewer, /^tools: Read, Bash, Grep, Glob$/m);
  assert.match(reviewer, /^skills:[\s\S]*review-implementation/m);
  assert.doesNotMatch(reviewer, /^tools:.*(?:Write|Edit)/m);
  assert.match(reviewer, /fresh context/i);

  assert.match(command, /\$ARGUMENTS/);
  assert.match(command, /workflow-planner/);
  assert.match(command, /workflow-implementer/);
  assert.match(command, /code-review/);
  assert.match(command, /workflow-reviewer/);
  assert.match(command, /Active task:/);
  assert.match(command, /\.workflow\/archive\//);
});

test("workflow behavior cases cover every state transition and failure gate", () => {
  const fixture = JSON.parse(read("evals/workflow-cases.json"));
  const stages = new Set(fixture.cases.map((entry) => entry.expected_stage));

  assert.equal(fixture.schema_version, 3);
  assert.ok(fixture.cases.length >= 12);
  for (const stage of [
    "clarify-requirements",
    "plan-solution",
    "tdd-implementation",
    "review-implementation",
    "remediate-and-reverify",
    "report-existing-independent-review",
    "finish-with-evidence",
    "report-unavailable-and-follow-local-workflow",
    "await-user-acceptance",
    "close-record",
    "resolve-pointer-conflict-before-implementing",
  ]) {
    assert.ok(stages.has(stage), `missing behavior case for ${stage}`);
  }

  const implementation = fixture.cases.find(
    (entry) => entry.name === "approved-plan-ready-for-tdd",
  );
  const review = fixture.cases.find(
    (entry) => entry.name === "implementation-needs-independent-review",
  );
  assert.equal(implementation.omp_agent, "workflow-implementer");
  assert.equal(implementation.omp_role, "@task");
  assert.equal(review.omp_role, "@advisor");
});

test("tooling supports synchronized install, diagnosis, and Python OMP launch", () => {
  const installer = read("scripts/install.ps1");
  const doctor = read("scripts/doctor.py");
  const doctorWrapper = read("scripts/doctor.ps1");
  const launcher = read("scripts/start-omp.py");

  assert.match(installer, /SupportsShouldProcess/);
  assert.match(installer, /Remove-Item -LiteralPath \$target -Recurse -Force/);
  assert.match(installer, /engineering-workflow\.yml/);
  assert.match(installer, /"Claude"/);
  assert.match(installer, /"Pi"/);
  assert.match(installer, /"All"/);
  assert.match(installer, /Join-Path \$project "\.claude"/);
  assert.match(installer, /Join-Path \$claudeRoot "skills"/);
  assert.match(installer, /Join-Path \$claudeRoot "agents"/);
  assert.match(installer, /Join-Path \$claudeRoot "commands"/);
  for (const agent of ["workflow-planner.md", "workflow-implementer.md", "workflow-reviewer.md"]) {
    assert.match(installer, new RegExp(`"${agent}"`, "g"));
  }
  assert.match(doctor, /workflow-implementer/);
  assert.match(doctor, /\.workflow/);
  assert.match(doctor, /def check_record_layout/);
  assert.match(doctor, /def check_injectors/);
  assert.match(doctor, /Per-turn context injector/);
  assert.match(doctor, /claude.*--version|executable_exists\("claude"/is);
  assert.match(doctor, /Missing Claude agent|"Claude", errors/);
  assert.match(doctor, /Missing .* agent: /);
  assert.match(installer, /PI_CODING_AGENT_DIR/);
  assert.match(installer, /Join-Path \$HOME "\.pi\\agent"/);
  assert.match(installer, /Join-Path \$piRoot "agents"/);
  assert.match(installer, /\.pi\\agents\\\$fileName/);
  assert.match(doctorWrapper, /doctor\.py/);
  assert.match(doctorWrapper, /& py -3/);
  assert.match(doctor, /executable_exists\("pi"/);
  assert.match(doctor, /"Pi", errors/);
  assert.match(doctor, /"@narumitw" \/ "pi-subagents"/);
  assert.match(doctor, /Missing OMP Python launcher/);
  assert.match(doctor, /OMP overlay skill whitelist is missing/);
  assert.match(doctor, /workflow-review-gate/);
  assert.doesNotMatch(doctor, /omp config list/);
  assert.match(installer, /start-engineering-workflow\.py/);
  assert.match(installer, /start-engineering-workflow\.ps1/);
  assert.match(installer, /omp-extensions/);
  assert.match(installer, /workflow-review-gate/);
  assert.match(launcher, /which\("ompweb" if web else "omp"\)/);
  assert.match(launcher, /def find_executable/);
  assert.match(launcher, /"--web"/);
  assert.match(launcher, /build_launch_command/);
  assert.match(launcher, /"--cwd", str\(project\), "--config", str\(overlay\)/);
  assert.match(launcher, /"--omp-config", str\(overlay\)/);
  assert.match(launcher, /single ompweb service/);
});

test("upstream manifest pins auditable revisions and retires Trellis", () => {
  const manifest = JSON.parse(read("manifests/upstreams.lock.json"));

  assert.deepEqual(
    Object.keys(manifest.sources).sort(),
    ["mattpocock-skills", "ponytail"],
  );
  assert.deepEqual(Object.keys(manifest.retired_sources), ["trellis"]);
  assert.ok(manifest.retired_sources.trellis.reason);
  assert.ok(manifest.retired_sources.trellis.retired);

  for (const source of Object.values(manifest.sources)) {
    assert.match(source.revision, /^[0-9a-f]{40}$/);
    assert.ok(source.license);
    assert.ok(source.local_path);
    assert.doesNotMatch(source.local_path, /^[A-Za-z]:[\\/]/);
    assert.ok(source.role);
  }
});

test("Chinese README explains purpose, usage, and extension tiers", () => {
  const readme = read("README.md");

  assert.match(readme, /[\u4e00-\u9fff]/);
  assert.match(readme, /^## 这个仓库是做什么的$/m);
  assert.match(readme, /^## 核心产物$/m);
  assert.match(readme, /^## 为什么不自动注入任务上下文$/m);
  assert.match(readme, /^## 子代理拿到的上下文包$/m);
  assert.match(readme, /^## 任务怎么拆$/m);
  assert.match(readme, /^## 产物用什么语言$/m);
  assert.match(readme, /^## 需要安装什么$/m);
  assert.match(readme, /^### 不需要安装：记录系统$/m);
  assert.match(readme, /^## 安装本仓库的 Skill$/m);
  assert.match(readme, /^## 使用方法$/m);
  assert.match(readme, /\.workflow\/tasks\/<task>\/context\.md/);
  assert.match(readme, /STATUS/);
  assert.doesNotMatch(readme, /npm install -g @mindfoldhq\/trellis|trellis init/);
  assert.match(readme, /grill-with-docs/);
  assert.match(readme, /\$run-engineering-workflow/);
  assert.match(readme, /\$clarify-requirements/);
  assert.match(readme, /\$plan-solution/);
  assert.match(readme, /\$review-implementation/);
  assert.match(readme, /\$finish-with-evidence/);
  assert.match(readme, /workflow-implementer/);
  assert.match(readme, /^## OMP 多模型工作流$/m);
  assert.match(readme, /^## Pi 工作流$/m);
  assert.match(readme, /^## Claude Code 工作流$/m);
  assert.match(readme, /^## 完整使用指南$/m);
  assert.match(readme, /^### 各客户端入口$/m);
  assert.match(readme, /^### 跨客户端和新会话续接$/m);
  assert.match(readme, /^### 其他客户端$/m);
  assert.match(readme, /start-engineering-workflow\.py.*--project-path/s);
  assert.match(readme, /-Harness Claude/);
  assert.match(readme, /-Harness Pi/);
  assert.match(readme, /-Harness All/);
  assert.match(readme, /~\/\.pi\/agent\/skills/);
  assert.match(readme, /\/skill:run-engineering-workflow/);
  assert.match(readme, /claude --model sonnet/);
  assert.match(readme, /skills\.includeSkills/);
  assert.match(readme, /普通 `omp`.*默认设置/s);
  assert.match(readme, /ompw.*显式指定项目 overlay/s);
  assert.match(readme, /workflow-review-gate/);
  assert.match(readme, /Active task \+ review profile \+\s*worktree snapshot/);
  assert.match(readme, /doctor\.ps1/);
});

test("task artifacts are written in the user's language", () => {
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const clarify = read("skills/clarify-requirements/SKILL.md");
  const plan = read("skills/plan-solution/SKILL.md");
  const finish = read("skills/finish-with-evidence/SKILL.md");

  assert.match(governance, /## Artifact Language/);
  assert.match(governance, /`STATUS` keys \(`phase`, `updated`\)/);
  assert.match(router, /written in the user's language/);
  for (const body of [clarify, plan, finish]) {
    assert.match(body, /Chinese by default/);
  }
  assert.match(clarify, /- \[ \] AC-001: 拒绝越权导出/);
  assert.match(plan, /### 切片 N：AC-XXX/);
  assert.match(finish, /# 交付结果/);
  assert.match(finish, /NOT RUN/);
});

test("dispatch carries an inlined context package, not a path list", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const plan = read("skills/plan-solution/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const implementers = [
    read("agents/workflow-implementer.md"),
    read(".omp/agents/workflow-implementer.md"),
    read(".pi/agents/workflow-implementer.md"),
  ];

  assert.match(plan, /## Write The Context Package/);
  assert.match(plan, /已内联上下文/);
  assert.match(plan, /需要新打开/);
  assert.match(router, /上下文包/);
  assert.match(router, /must not redo research/);
  assert.match(governance, /Inlining is the point/);
  for (const implementer of implementers) {
    assert.match(implementer, /上下文包/);
  }
});

test("decomposition exposes slices, tickets, and a recomputable frontier", () => {
  const plan = read("skills/plan-solution/SKILL.md");
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const finish = read("skills/finish-with-evidence/SKILL.md");
  const planner = read("agents/workflow-planner.md");

  assert.match(plan, /## Decompose The Work/);
  assert.match(plan, /blocked_by: \[T1\]/);
  assert.match(governance, /## Tickets And Decomposition/);
  assert.match(governance, /frontier is the set of `ready` tickets/);
  assert.match(router, /recompute the frontier/);
  assert.match(finish, /tickets\//);
  assert.match(planner, /tickets\/NN-<slug>\.md/);
});
