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

test("workflow policies define one owner for every durable artifact", () => {
  const ownership = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );

  for (const artifact of [
    "prd.md",
    "design.md",
    "implement.md",
    "outcome.md",
    ".trellis/spec/",
    ".trellis/workspace/",
    "CONTEXT.md",
    "docs/adr/",
  ]) {
    assert.match(ownership, new RegExp(artifact.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }

  assert.match(ownership, /Trellis.*canonical/i);
  assert.match(ownership, /do not duplicate/i);
});

test("router preserves Trellis state and delegates quality work", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");

  assert.match(router, /\.trellis\/workflow\.md/);
  assert.match(router, /planning/);
  assert.match(router, /in_progress/);
  assert.match(router, /clarify-requirements/);
  assert.match(router, /plan-solution/);
  assert.match(router, /tdd-workflow/);
  assert.match(router, /trellis-check/);
  assert.match(router, /review-implementation/);
  assert.match(router, /finish-with-evidence/);
  assert.match(router, /workflow-planner/);
  assert.match(router, /trellis-implement/);
  assert.match(router, /workflow-reviewer/);
  assert.match(router, /py -3/);
  assert.match(router, /WindowsApps alias/);
  assert.match(router, /Never use the `eval` Python kernel/);
  assert.match(router, /Never mutate `sys\.platform`/);
});

test("solution planning separates design decisions from execution steps", () => {
  const skill = read("skills/plan-solution/SKILL.md");

  assert.match(skill, /prd\.md/);
  assert.match(skill, /design\.md/);
  assert.match(skill, /implement\.md/);
  assert.match(skill, /alternatives/i);
  assert.match(skill, /data flow/i);
  assert.match(skill, /rollback/i);
  assert.match(skill, /test seam/i);
  assert.match(skill, /AC-001/);
  assert.match(skill, /do not implement/i);
});

test("clarification writes observable acceptance criteria into Trellis", () => {
  const skill = read("skills/clarify-requirements/SKILL.md");

  assert.match(skill, /prd\.md/);
  assert.match(skill, /AC-001/);
  assert.match(skill, /in scope/i);
  assert.match(skill, /out of scope/i);
  assert.match(skill, /verification method/i);
  assert.match(skill, /one question at a time/i);
});

test("finish skill records actual evidence without inventing results", () => {
  const skill = read("skills/finish-with-evidence/SKILL.md");

  assert.match(skill, /outcome\.md/);
  assert.match(skill, /RED.*GREEN/s);
  assert.match(skill, /git diff/);
  assert.match(skill, /do not invent/i);
  assert.match(skill, /trellis-update-spec/);
  assert.match(skill, /Independent Review/);
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
  const reviewer = read(".omp/agents/workflow-reviewer.md");

  assert.match(config, /includeSkills:/);
  assert.match(config, /workflow-planner: "@plan"/);
  assert.match(config, /trellis-implement: "@task"/);
  assert.match(config, /trellis-check: "@advisor"/);
  assert.match(config, /workflow-reviewer: "@advisor"/);
  assert.match(config, /prewalk:[\s\S]*enabled: false/);
  assert.match(planner, /model: "@plan"/);
  assert.match(planner, /autoloadSkills:.*plan-solution/);
  assert.match(planner, /autoloadSkills:.*trellis-brainstorm/);
  assert.match(reviewer, /model: "@advisor"/);
  assert.match(reviewer, /autoloadSkills:.*review-implementation/);
  assert.doesNotMatch(reviewer, /tools:.*(?:write|edit)/);
});

test("Claude Code plugin maps planning and review without replacing Trellis agents", () => {
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
  assert.match(command, /trellis-implement/);
  assert.match(command, /trellis-check/);
  assert.match(command, /workflow-reviewer/);
  assert.match(command, /Active task:/);
});

test("workflow behavior cases cover every state transition and failure gate", () => {
  const fixture = JSON.parse(read("evals/workflow-cases.json"));
  const stages = new Set(fixture.cases.map((entry) => entry.expected_stage));

  assert.equal(fixture.schema_version, 1);
  assert.equal(fixture.cases.length, 7);
  for (const stage of [
    "clarify-requirements",
    "plan-solution",
    "tdd-implementation",
    "review-implementation",
    "remediate-and-reverify",
    "finish-with-evidence",
    "report-unavailable-and-follow-local-workflow",
  ]) {
    assert.ok(stages.has(stage), `missing behavior case for ${stage}`);
  }

  const implementation = fixture.cases.find(
    (entry) => entry.name === "approved-plan-ready-for-tdd",
  );
  const review = fixture.cases.find(
    (entry) => entry.name === "implementation-needs-independent-review",
  );
  assert.equal(implementation.omp_role, "@task");
  assert.equal(review.omp_role, "@advisor");
});

test("tooling supports synchronized install, diagnosis, and Python OMP launch", () => {
  const installer = read("scripts/install.ps1");
  const doctor = read("scripts/doctor.ps1");
  const launcher = read("scripts/start-omp.py");

  assert.match(installer, /SupportsShouldProcess/);
  assert.match(installer, /Remove-Item -LiteralPath \$target -Recurse -Force/);
  assert.match(installer, /engineering-workflow\.yml/);
  assert.match(installer, /"Claude"/);
  assert.match(installer, /"All"/);
  assert.match(installer, /Join-Path \$project "\.claude"/);
  assert.match(installer, /Join-Path \$claudeRoot "skills"/);
  assert.match(installer, /Join-Path \$claudeRoot "agents"/);
  assert.match(installer, /Join-Path \$claudeRoot "commands"/);
  assert.match(doctor, /trellis-implement: \"@task\"/);
  assert.match(doctor, /trellis\\workflow\.md/);
  assert.match(doctor, /claude.*--version/is);
  assert.match(doctor, /Missing Claude agent/);
  assert.match(doctor, /Missing Trellis Claude agent/);
  assert.match(doctor, /Missing OMP Python launcher/);
  assert.match(installer, /start-engineering-workflow\.py/);
  assert.match(installer, /start-engineering-workflow\.ps1/);
  assert.match(launcher, /shutil\.which\("omp"\)/);
  assert.match(launcher, /project \/ "\.omp" \/ OVERLAY_NAME/);
  assert.match(launcher, /"--cwd", str\(project\), "--config", str\(overlay\)/);
});

test("upstream manifest pins auditable revisions and licenses", () => {
  const manifest = JSON.parse(read("manifests/upstreams.lock.json"));

  assert.deepEqual(
    Object.keys(manifest.sources).sort(),
    ["ecc", "mattpocock-skills", "ponytail", "trellis"],
  );

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
  assert.match(readme, /^## 需要安装什么$/m);
  assert.match(readme, /^## 安装本仓库的 Skill$/m);
  assert.match(readme, /^## 使用方法$/m);
  assert.match(readme, /npm install -g @mindfoldhq\/trellis@latest/);
  assert.match(readme, /codex plugin add ecc@ecc/);
  assert.match(readme, /\$run-engineering-workflow/);
  assert.match(readme, /\$clarify-requirements/);
  assert.match(readme, /\$plan-solution/);
  assert.match(readme, /\$review-implementation/);
  assert.match(readme, /\$finish-with-evidence/);
  assert.match(readme, /^## OMP 多模型工作流$/m);
  assert.match(readme, /^## Claude Code 工作流$/m);
  assert.match(readme, /^## 完整使用指南$/m);
  assert.match(readme, /^### 各客户端入口$/m);
  assert.match(readme, /^### 跨客户端和新会话续接$/m);
  assert.match(readme, /^### 其他客户端$/m);
  assert.match(readme, /trellis init --codex --claude --omp/);
  assert.match(readme, /start-engineering-workflow\.py.*--project-path/s);
  assert.match(readme, /-Harness Claude/);
  assert.match(readme, /-Harness All/);
  assert.match(readme, /claude --model sonnet/);
  assert.match(readme, /trellis-implement.*`@task`/s);
  assert.match(readme, /skills\.includeSkills/);
  assert.match(readme, /doctor\.ps1/);
});
