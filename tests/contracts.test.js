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

test("simple work eligibility is centralized without weakening formal gates", () => {
  const profiles = read("skills/run-engineering-workflow/references/quality-profiles.md");
  const fast = profiles.split("## Simple Work Fast Path")[1]?.split("## Lightweight")[0];
  assert.ok(fast, "missing shared simple-work eligibility");
  assert.match(fast, /all.*conditions/is);
  assert.match(fast, /non-behavioral.*local.*low-risk/is);
  assert.match(fast, /same.*session.*no.*(?:handoff|delegation)/is);
  assert.match(fast, /explicit.*OpenSpec.*selected change/is);
  assert.match(fast, /stricter project.*(?:record|rule)/is);
  assert.match(fast, /behavior.*Standard.*Critical/is);
  assert.match(fast, /dependenc/i);
  assert.match(fast, /CLI.*(?:error|failure).*not.*(?:qualif|eligib)/is);
});

test("router chooses the fast path before discovery and preserves formal routing", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const start = router.indexOf("## Choose Fast Or Formal");
  const locate = router.indexOf("## Start");
  assert.ok(start >= 0 && start < locate, "fast decision must precede canonical discovery");
  const fast = router.slice(start, locate);
  assert.match(fast, /quality-profiles\.md#simple-work-fast-path/);
  assert.match(fast, /before.*(?:discovery|CLI)/is);
  assert.match(fast, /without.*(?:creat|record)/is);
  assert.match(fast, /return.*(?:skip|do not enter).*formal/is);
  assert.match(router.slice(locate), /formal.*(?:only|branch)/is);
  assert.match(router.slice(locate), /never create, reuse, or select without explicit confirmation/);
  for (const file of [
    "commands/engineering-workflow.md",
    "skills/run-engineering-workflow/references/workflow-governance.md",
  ]) {
    const body = read(file);
    assert.match(body, /quality-profiles\.md#simple-work-fast-path/, file);
    assert.match(body, /before.*discovery/is, file);
    assert.match(body, /formal.*(?:confirmation|confirm)/is, file);
  }
  for (const file of ["README.md", "ARCHITECTURE.md"]) {
    assert.match(read(file), /quality-profiles\.md#simple-work-fast-path/, file);
    assert.doesNotMatch(read(file), /主路由会先询问是否创建 `\.workflow\//, file);
  }
  assert.match(read("skills/run-engineering-workflow/agents/openai.yaml"), /fast.*formal/is);
});

test("current README guides do not reintroduce legacy creation before fast routing", () => {
  const readme = read("README.md");
  for (const stale of [
    /先询问是否创建\s*`\.workflow\/`/,
    /主路由会先读取\s*`\.workflow\/CURRENT\.md`/,
    /新状态一律写入 `\.workflow\/`/,
    /按 `\.workflow\/` 中的任务阶段/,
    /通过同一个工作树和 `\.workflow\/` 共享上下文/,
    /任务记录目录 `\.workflow\/` 由主路由/,
    /进入主路由[^\n]*读取 `\.workflow\/CURRENT\.md`/,
    /票写到 `\.workflow\/tasks\//,
    /项目 `AGENTS\.md` 和 `\.workflow\/spec\/`/,
  ]) assert.doesNotMatch(readme, stale, "current guide must not route new work through legacy records");
  const guide = readme.split("## 完整使用指南")[1].split("## Pi 工作流")[0];
  assert.match(guide, /quality-profiles\.md#simple-work-fast-path/);
  assert.match(guide, /简单任务.*不.*(?:建档|记录)/s);
  assert.match(guide, /### 一次正式任务的阶段/);
  assert.match(guide, /显式 legacy 恢复/);
  const finish = readme.split("### 6. 完成和记录证据")[1].split("### 7.")[0];
  assert.match(finish, /快速通道.*对话.*不.*verification/s);
  assert.match(finish, /仅.*正式.*change.*记录/s);
});

test("proposal-based risk assessment applies only after fast/formal selection", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const assessIndex = router.indexOf("## Assess Profile First");
  assert.ok(assessIndex > router.indexOf("## Choose Fast Or Formal"));
  const assess = router.slice(assessIndex).split("\n## ")[0];
  assert.match(assess, /Formal branch only/);
  assert.match(assess, /after.*fast.*formal.*(?:selection|decision)/is);
  assert.doesNotMatch(assess, /Before any routing/);
  assert.match(assess, /selected OpenSpec `proposal\.md`/);
});
test("simple work routing fixtures cover eligibility and explicit formal intent", () => {
  const cases = JSON.parse(read("evals/workflow-cases.json")).cases;
  for (const [name, stage] of [
    ["simple-docs-with-existing-changes", "fast-execute"],
    ["simple-work-without-cli", "fast-execute"],
    ["small-behavior-fix-requires-change", "discover-and-confirm"],
    ["strict-project-requires-change", "discover-and-confirm"],
    ["selected-change-small-edit", "resume-selected-change"],
    ["explicit-openspec-small-edit", "discover-and-confirm"],
  ]) {
    const scenario = cases.find((item) => item.name === name);
    assert.ok(scenario, `missing routing scenario: ${name}`);
    assert.equal(scenario.expected_stage, stage, name);
    assert.ok(scenario.forbidden?.length, `${name}: missing negative boundary`);
  }
});

test("planning and finish return from an already selected fast path before formal artifacts", () => {
  for (const [file, formalHeading] of [
    ["skills/plan-solution/SKILL.md", "## Confirm Readiness"],
    ["skills/finish-with-evidence/SKILL.md", "## Consume Evidence"],
  ]) {
    const body = read(file);
    const start = body.indexOf("## Fast Path Exit");
    const formal = body.indexOf(formalHeading);
    assert.ok(start >= 0 && start < formal, `${file}: missing early fast-path exit`);
    const fast = body.slice(start, formal);
    assert.match(fast, /main router.*already selected/is, file);
    assert.match(fast, /quality-profiles\.md#simple-work-fast-path/, file);
    assert.match(fast, /return.*main (?:router|session)/is, file);
    assert.match(fast, /(?:no|without|do not).*creat.*(?:record|artifact)/is, file);
    assert.match(fast, /formal.*(?:not|never).*downgrad/is, file);
  }
  assert.match(read("skills/finish-with-evidence/agents/openai.yaml"), /fast.*formal/is);
  assert.match(read("skills/plan-solution/SKILL.md"), /For.*formal.*lightweight/is);
});

test("fast work retains verification and stops before expanding its scope", () => {
  const profiles = read("skills/run-engineering-workflow/references/quality-profiles.md");
  const fast = profiles.split("## Simple Work Fast Path")[1]?.split("## Lightweight")[0];
  assert.match(fast, /diff.*smallest.*checks.*project/is);
  assert.match(fast, /commands\/results.*NOT RUN.*conversation/is);
  assert.match(fast, /failed.*not.*success.*CLEAN/is);
  assert.match(fast, /stop.*implementation.*Preserve.*diffs.*checks.*formal.*confirmation/is);
  assert.match(fast, /do not auto-create.*discard edits/is);
  assert.match(fast, /replacement task\/status records.*retroactive artifacts/is);
  const cases = JSON.parse(read("evals/workflow-cases.json")).cases;
  for (const [name, stage] of [
    ["fast-scope-expands", "stop-and-confirm-change"],
    ["fast-verification-fails", "report-verification-failure"],
    ["fast-finish-no-record", "report-fast-evidence"],
  ]) {
    const scenario = cases.find((item) => item.name === name);
    assert.ok(scenario, `missing fast exit scenario: ${name}`);
    assert.equal(scenario.expected_stage, stage, name);
    assert.ok(scenario.forbidden?.length, `${name}: missing negative boundary`);
  }
});

test("review budget is centralized and consistent across workflow entry points", () => {
  const profiles = read("skills/run-engineering-workflow/references/quality-profiles.md");
  const lightweight = profiles.split("## Lightweight")[1].split("## Standard")[0];
  const standard = profiles.split("## Standard")[1].split("## Critical")[0];
  const critical = profiles.split("## Critical")[1];
  assert.match(lightweight, /no default independent reviewer/i);
  assert.match(standard, /exactly one independent.*workflow-reviewer/is);
  assert.match(standard, /Standards.*Spec/s);
  assert.match(standard, /implementation delegation.*explicit.*authorization/is);
  assert.match(critical, /no additional\s+final reviewer/i);
  for (const file of [
    "skills/run-engineering-workflow/SKILL.md",
    "skills/run-engineering-workflow/references/workflow-governance.md",
    "commands/engineering-workflow.md",
    "README.md",
    "ARCHITECTURE.md",
  ]) {
    const body = read(file);
    assert.match(body, /quality-profiles\.md/, `${file}: missing budget source`);
    assert.doesNotMatch(body, /then Matt `code-review`|then `code-review`, then|either Matt `code-review`|先运行仓库自身检查与 Matt `code-review`|`code-review` 与独立 review 二选一|code-review \+ 仓库检查/, `${file}: duplicate or optional default review`);
  }
  const command = read("commands/engineering-workflow.md");
  assert.match(command, /lightweight.*no.*dispatch/is);
  assert.match(command, /standard.*critical.*exactly one/is);
  assert.match(command, /planning delegation.*explicitly requested/is);
});

test("workspace review and finish reuse a complete independent result", () => {
  const review = read("skills/review-implementation/SKILL.md");
  const finish = read("skills/finish-with-evidence/SKILL.md");
  for (const body of [review, finish]) {
    assert.match(body, /Standards/);
    assert.match(body, /Spec/);
    assert.match(body, /staged.*unstaged.*untracked/is);
    assert.match(body, /same.change.*same.material/is);
    assert.match(body, /appending.*(?:report|evidence).*not.*invalidate/is);
    assert.match(body, /UNVERIFIED/);
  }
  assert.match(review, /fixed\s+point.*nonempty.*committed/is);
  assert.match(review, /one controlled.*INVALID/is);
  assert.doesNotMatch(finish, /Run Matt `code-review`|after\s+`code-review`/);
  for (const file of ["agents/workflow-reviewer.md", ".omp/agents/workflow-reviewer.md", ".pi/agents/workflow-reviewer.md"]) {
    const body = read(file);
    assert.match(body, /Standard.*Critical/is, file);
    assert.match(body, /Standards.*Spec/s, file);
    assert.match(body, /staged.*unstaged.*untracked/is, file);
    assert.match(body, /do not.*nested dispatch/is, file);
    assert.doesNotMatch(body, /Only dispatch for critical/);
  }
  assert.doesNotMatch(read(".omp/agents/workflow-reviewer.md"), /autoloadSkills:.*"code-review"/);
});

test("delivery review budget bounds rounds rather than only reviewer count", () => {
  const profiles = read("skills/run-engineering-workflow/references/quality-profiles.md");
  const budget = profiles.split("## Delivery Review Budget")[1];
  assert.ok(budget, "missing delivery-level budget");
  assert.match(budget, /exactly one full review and at most one focused follow-up/i);
  assert.match(budget, /original blocking findings.*repair diff.*directly affected/is);
  assert.match(budget, /non-blocking.*(?:do not|never).*trigger/is);
  assert.match(budget, /resume.*snapshot.*do not reset/is);
  assert.match(budget, /blocked.*user.*(?:decide|decision)/is);
  assert.match(budget, /user approval.*(?:new full review|restart)/is);
  assert.match(budget, /one controlled.*INVALID.*no valid report/is);
  assert.match(budget, /artifacts\/review\.md.*artifacts\/verification\.md/is);
  assert.doesNotMatch(profiles, /after material fixes,[\s\S]{0,90}review the new snapshot/i);
});

test("routing reviews the delivery scope once and never adds code-reviewer", () => {
  for (const file of ["skills/run-engineering-workflow/SKILL.md", "commands/engineering-workflow.md"]) {
    const body = read(file);
    assert.match(body, /delivery scope.*complete.*full review/is, file);
    assert.match(body, /(?:slice|slices).*checks.*not.*full review/is, file);
    assert.match(body, /code-reviewer/, file);
    assert.match(body, /focused.*follow-up/is, file);
    assert.match(body, /main (?:session|router).*only.*schedul/is, file);
    assert.doesNotMatch(body, /snapshot changes require a new review|checks, and a new final review|Review again after material fixes/i, file);
  }
});

test("behavior fixtures distinguish focused repair, exhaustion, scope drift and finish reuse", () => {
  const cases = JSON.parse(read("evals/workflow-cases.json")).cases;
  for (const [name, stage] of [
    ["remediated-diff-needs-focused-follow-up", "focused-review"],
    ["review-budget-exhausted", "handoff-review-blocker"],
    ["nonblocking-review-suggestions", "finish-with-evidence"],
    ["review-resume-preserves-budget", "handoff-review-blocker"],
    ["review-scope-drift-needs-user-decision", "request-review-reauthorization"],
    ["finish-evidence-gap-returns-to-router", "return-verification-gap"],
    ["slice-complete-not-delivery-complete", "targeted-checks"],
    ["valid-review-no-extra-code-reviewer", "finish-with-evidence"],
  ]) {
    const entry = cases.find((candidate) => candidate.name === name);
    assert.ok(entry, `missing scenario ${name}`);
    assert.equal(entry.expected_stage, stage);
    assert.ok(entry.forbidden.length > 0, `${name}: missing negative boundary`);
  }
  assert.ok(!cases.some((entry) => entry.name === "remediated-diff-needs-fresh-final-review"));
});

test("review procedure and all reviewer adapters distinguish full and focused modes", () => {
  const review = read("skills/review-implementation/SKILL.md");
  assert.match(review, /Review mode:.*full.*focused/is);
  assert.match(review, /focused.*original blocking findings.*repair diff.*directly affected/is);
  assert.match(review, /Blocking:.*yes.*no/is);
  assert.match(review, /REVIEW_STATUS: CLEAN.*no blocking/is);
  assert.doesNotMatch(review, /Changes to those inputs require.*a new review/is);
  for (const file of ["agents/workflow-reviewer.md", ".omp/agents/workflow-reviewer.md", ".pi/agents/workflow-reviewer.md"]) {
    const body = read(file);
    assert.match(body, /Review mode:.*full.*focused/is, file);
    assert.match(body, /code-reviewer/, file);
    assert.match(body, /focused.*(?:repair|findings)/is, file);
    assert.doesNotMatch(body, /material input changes\s+require fresh review/i, file);
  }
});

test("finish consumes evidence and returns gaps without scheduling or running checks", () => {
  const finish = read("skills/finish-with-evidence/SKILL.md");
  assert.match(finish, /## Consume Evidence/);
  assert.match(finish, /do not dispatch.*do not.*run.*verification/is);
  assert.match(finish, /(?:missing|stale).*main router/is);
  assert.match(finish, /(?:full|focused).*round/is);
  assert.doesNotMatch(finish, /\d\. Run relevant repository verification|fixes, affected checks and one new review|Re-run affected checks after substantive simplification/i);
  assert.match(finish, /awaiting-acceptance/);
  const metadata = read("skills/finish-with-evidence/agents/openai.yaml");
  assert.match(metadata, /consume.*(?:existing|recorded).*evidence/i);
});

test("vocabulary ownership preserves legacy files and OpenSpec context", () => {
  const governance = read("skills/run-engineering-workflow/references/workflow-governance.md");
  const clarify = read("skills/clarify-requirements/SKILL.md");
  const finish = read("skills/finish-with-evidence/SKILL.md");
  const archive = read("skills/archive-task/SKILL.md");
  assert.match(governance, /`GLOSSARY\.md`.*new project/i);
  assert.match(governance, /`CONTEXT\.md`.*legacy-compatible/i);
  assert.match(governance, /ask before writing/i);
  assert.match(governance, /`GLOSSARY-MAP\.md`/);
  assert.match(governance, /do not migrate, rename, or mirror.*implicitly/i);
  assert.match(governance, /`artifacts\/context\.md`.*never/);
  for (const body of [clarify, finish, archive]) {
    assert.match(body, /`GLOSSARY\.md`/);
    assert.match(body, /existing `CONTEXT\.md`/);
  }
  assert.match(finish, /`openspec\/specs\/`/);
});

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
    /trellis-implement|trellis-check|trellis_subagent|trellis init|trellis update|trellis mem|get_context\.py|(?:^|[\\/\\])task\.py|trellis-before-dev|trellis-brainstorm|trellis-update-spec|trellis-session-insight|\.trellis\/workflow\.md/;
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

  assert.match(router, /\.trellis\//);
  assert.match(router, /never run a\s+Trellis script|never execute a Trellis script/i);
  assert.match(governance, /## Legacy `\.trellis\/` Repositories/);
  assert.match(governance, /read-only historical format/i);
  assert.match(governance, /never\s+write into `\.trellis\/`/i);
  assert.match(governance, /read-only historical format|historical recovery/);
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
    "proposal.md",
    "design.md",
    "tasks.md",
    "artifacts/context.md",
    "artifacts/verification.md",
    "openspec/changes/archive/",
    ".workflow/",
    ".trellis/",
    "docs/adr/",
  ]) {
    assert.ok(ownership.includes(artifact), `missing artifact ownership: ${artifact}`);
  }

  assert.match(ownership, /OpenSpec is the canonical owner/i);
  assert.match(ownership, /do not dual-write/i);
});

test("router selects OpenSpec and keeps legacy recovery read-only", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");

  assert.match(router, /openspec\/config\.(?:yaml|yml)/);
  assert.match(router, /openspec list --json/);
  assert.match(router, /Active change: openspec\/changes/);
  assert.match(router, /legacy.*recoverable|recoverable.*legacy/i);
  assert.match(router, /do not write new state into `\.workflow\/?`/i);
  assert.match(router, /never run a Trellis script/i);
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
  assert.doesNotMatch(router, /After (?:10|15) minutes without progress/);
  assert.match(router, /Do not interrupt or terminate a worker solely because a duration threshold/);
  assert.match(router, /stop only on explicit failure, cancellation, or user instruction/);
  assert.match(router, /Do not add call-level runtime deadlines/);
  assert.match(router, /Do not automatically re-dispatch/);
  assert.match(router, /do not poll `hub jobs`, `hub list`/);
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
  assert.match(governance, /Moving a change to `openspec\/archive\//);
  assert.match(finish, /## Hand Off For Acceptance/);
  assert.match(finish, /do not archive the OpenSpec change/);
  assert.match(finish, /awaiting-acceptance/);
  assert.match(finish, /do not archive the OpenSpec change/);
  assert.match(finish, /复验轮次/);
  assert.match(router, /does not archive (?:the )?(?:OpenSpec )?change/);
  assert.match(router, /print the command(?:s)? instead of running it|print the command(?:s)? instead of running them/i);
  assert.match(
    router,
    /Do not archive an OpenSpec change or clear pointers/
  );
  assert.match(architecture, /\(user\) accept, then archive/);
  assert.match(agents, /Acceptance and archival belong to the user/);
  assert.match(router, /invoke `archive-task`/);
});

test("routing recommends and requires confirmation before creating or reusing", () => {
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const governance = read(
    "skills/run-engineering-workflow/references/workflow-governance.md",
  );
  const command = read("commands/engineering-workflow.md");
  const compat = read("scripts/openspec_compat.py");
  const doctor = read("scripts/doctor.py");
  const installer = read("scripts/install.ps1");

  assert.match(router, /## Match And Confirm Before Creating Or Reusing/);
  assert.match(router, /never create, reuse, or select without explicit confirmation/);
  assert.match(router, /是否创建 XXX 任务/);
  assert.match(router, /已经存在 XXX 任务，是否复用/);
  assert.match(router, /Never order candidates by recency, name, or model\s+preference/);
  assert.match(router, /Related but\s+different goals are not a match/);
  assert.match(router, /create_change/);
  assert.match(router, /list_changes/);
  assert.doesNotMatch(router, /select exactly one active change/);
  assert.match(governance, /not even when exactly one change exists/);
  assert.match(governance, /Rejecting reuse is not consent to create/);
  assert.match(governance, /environment errors are never reported as "no match"/);
  assert.match(command, /read-only discovery of unarchived changes/);
  assert.match(command, /stop for an explicit user\s+confirmation/);
  assert.match(compat, /def list_changes\(/);
  assert.match(compat, /def create_change\(/);
  assert.match(compat, /Change id must contain lowercase letters, numbers, and hyphens only/);
  assert.match(doctor, /nothing is auto-selected/);
  assert.match(installer, /scripts\\openspec_compat\.py/);
  assert.match(installer, /\$sharedSkills = Join-Path \$HOME '\.agents\/skills'/);
  assert.match(installer, /-IncludeCompat:\(\$name -eq 'run-engineering-workflow'\)/);
  assert.doesNotMatch(installer, /\$(codexSkills|ompSkills|piSkills)\s*=/);
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
  assert.match(skill, /awaiting-acceptance/);
  assert.match(skill, /ARCHIVE_STATUS: REFUSED/);
  assert.match(skill, /ARCHIVE_STATUS: ARCHIVED/);
  assert.match(skill, /ARCHIVE_STATUS: PARTIAL/);
  assert.match(skill, /do not run extra checks to earn the archive/i);
  assert.match(skill, /Move the change directory to `openspec\/changes\/archive/);
  assert.match(skill, /Committing, pushing, publishing, and deleting an archived change stay out of/);
  assert.match(command, /\/archive-task|archive-task/);
  assert.match(command, /\$ARGUMENTS/);

  // both entry points delegate; neither duplicates the procedure
  assert.match(router, /invoke `archive-task`/);
  assert.match(finish, /invoke `archive-task`/);
  assert.match(overlay, /^    - archive-task$/m);
  assert.match(installer, /"archive-task"/);
  assert.match(installer, /"archive-task\.md"/);
  assert.match(doctor, /"archive-task",/);
  assert.match(doctor, /def check_skill_whitelist/);
  assert.match(doctor, /OMP \{label\} skill whitelist is missing/);
  assert.match(skill, /openspec\/changes\/archive/);
  assert.match(skill, /verify/i);
  assert.match(skill, /Write OpenSpec text/);
  assert.match(governance, /openspec\/changes\/archive/);
  assert.match(governance, /user-triggered only/);
  assert.match(read("commands/engineering-workflow.md"), /Only `\/archive-task`.*after acceptance/s);
});



test("finish skill records actual evidence without inventing results", () => {
  const skill = read("skills/finish-with-evidence/SKILL.md");

  assert.match(skill, /artifacts\/verification\.md/);
  assert.match(skill, /RED.*GREEN/s);
  assert.match(skill, /git diff/);
  assert.match(skill, /do not invent/i);
  assert.match(skill, /openspec\/specs\//);
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
  assert.match(config, /^  maxRuntimeMs: 0$/m);
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

  for (const agent of [planner, implementer, reviewer]) {
    assert.match(agent, /^timeoutMs: 2147483647$/m);
  }

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

  for (const field of ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]) {
    assert.ok(router.includes(field), `router missing ${field}`);
  }
  assert.match(router, /openspec\/changes\/<change-id>\//);
  assert.match(router, /requested_model/);
  assert.match(router, /effective_model/);
  assert.match(router, /fallback/);
  for (const field of ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]) {
    assert.ok(planner.includes(field), `planner missing ${field}`);
  }
  assert.match(planner, /PLANNING_STATUS: INVALID/);
  assert.match(planner, /do not[\s\S]{0,40}scan all change directories/i);
  for (const field of ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "May modify:", "Verification:"]) {
    assert.match(implementer, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  for (const field of ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "Review mode:", "Review scope:", "Evidence:"]) {
    assert.match(reviewer, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(reviewer, /REVIEW_STATUS: INVALID/);
  assert.match(reviewer, /do not[\s\S]{0,40}scan all change directories/i);
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
    "Active change:",
    "Assigned slice:",
    "Phase:",
    "Read:",
    "Must preserve:",
    "May modify:",
    "Verification:",
    "Review mode:",
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
    ["planner-with-explicit-task", ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:"]],
    ["implementation-with-one-slice", ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "May modify:", "Verification:"]],
    ["review-with-diff-evidence", ["Active change:", "Assigned slice:", "Phase:", "Read:", "Must preserve:", "Review mode:", "Review scope:", "Evidence:"]],
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
  assert.match(planner, /tasks\.md/);
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
  assert.match(command, /Active change:/);
  assert.match(command, /`awaiting-acceptance`|awaiting-acceptance/);
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
  assert.match(installer, /Backup-ManagedPath -Path \$target/);
  assert.match(installer, /Assert-SafeParents/);
  assert.match(installer, /Install-SharedLink/);
  assert.match(installer, /engineering-workflow\.yml/);
  assert.match(installer, /"Claude"/);
  assert.match(installer, /"Pi"/);
  assert.match(installer, /"All"/);
  assert.match(installer, /Join-Path \$project "\.claude"/);
  assert.match(installer, /\$claudeLinkRoots/);
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
  assert.match(doctor, /check_agents\(root \/ "agents", "Pi", errors\)/);
  assert.match(doctor, /def check_shared_installation/);
  assert.match(doctor, /Missing shared OpenSpec helper/);
  assert.match(doctor, /Claude skill link/);
  assert.match(doctor, /Legacy skill entry/);
  assert.match(doctor, /"@narumitw" \/ "pi-subagents"/);
  assert.match(doctor, /Missing OMP Python launcher/);
  assert.match(doctor, /check_skill_whitelist\(path, "overlay", errors\)/);
  assert.match(doctor, /workflow-review-gate/);
  assert.match(doctor, /def skill_whitelist_entries/);
  assert.match(doctor, /"user config"/);
  assert.match(installer, /Add-OmpSkillWhitelist/);
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

  assert.equal(
    manifest.sources["mattpocock-skills"].revision,
    "49dd158d1076134a641b33efb035946536778336",
  );
  assert.equal(manifest.sources["mattpocock-skills"].version_hint, "1.3.1");
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
  assert.match(readme, /^### 记录系统$/m);
  assert.match(readme, /^## 安装本仓库的 Skill$/m);
  assert.match(readme, /^## 使用方法$/m);
  assert.match(readme, /openspec\/changes\/<change-id>\//);
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
  assert.match(readme, /skill whitelist is missing/);
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
  assert.match(governance, /OpenSpec `proposal\.md`|OpenSpec artifacts/);
  assert.match(router, /written in the user's language/);
  for (const body of [clarify, plan, finish]) {
    assert.match(body, /Chinese by default/);
  }
  assert.match(clarify, /- \[ \] AC-001: 拒绝越权导出/);
  assert.match(plan, /### 切片 N：AC-XXX/);
  assert.match(finish, /# 交付验证/);
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
  assert.match(router, /context package|上下文 package/);
  assert.match(router, /must not redo research/);
  assert.match(governance, /Inlining is the point/);
  for (const implementer of implementers) {
    assert.match(implementer, /context package|上下文 package/);
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
  assert.match(governance, /execution frontier|execution frontier/);
  assert.match(router, /recompute the frontier/);
  assert.match(finish, /tasks\.md/);
  assert.match(planner, /tasks\.md/);
});

test("OpenSpec changes carry a readable Chinese title in listings and routing", () => {
  const config = read("openspec/config.yaml");
  const propose = read(".pi/skills/openspec-propose/SKILL.md");
  const compat = read("scripts/openspec_compat.py");
  const router = read("skills/run-engineering-workflow/SKILL.md");
  const doctor = read("scripts/doctor.py");

  assert.match(config, /# 提案：<中文短标题>/);
  assert.match(config, /## Why` and `## What Changes` in English/);
  assert.match(propose, /# 提案：<中文短标题>/);
  assert.match(propose, /Never leave the H1 as `# Proposal` or a bare change id/);
  assert.match(compat, /def _change_titles\(/);
  assert.match(compat, /TITLE_RE = re\.compile/);
  assert.match(compat, /change_titles=titles/);
  assert.doesNotMatch(compat, /"change", "list"/);
  assert.doesNotMatch(compat, /\["show", name\]/);
  assert.match(router, /change_titles/);
  assert.match(doctor, /change_titles/);
});

test("A human can list changes with readable titles without the agent", () => {
  const compat = read("scripts/openspec_compat.py");
  const skill = read("skills/run-engineering-workflow/SKILL.md");

  assert.match(compat, /def _main\(argv: Sequence\[str\]\) -> int:/);
  assert.match(compat, /add_parser\("list"/);
  assert.match(compat, /def _safe_print\(/);
  assert.match(compat, /raise SystemExit\(_main\(sys\.argv\[1:\]\)\)/);
  assert.doesNotMatch(compat, /raise SystemExit\("Import this module/);
  // The CLI must stay read-only: no create/update/archive command may appear.
  assert.doesNotMatch(compat, /add_parser\("(create|update|archive|apply)"/);
  assert.match(skill, /openspec_compat\.py list/);
});

test("The proposal title rule is installed into new projects, not only this repo", () => {
  const compat = read("scripts/openspec_compat.py");
  const doctor = read("scripts/doctor.py");

  // A fresh project's config only carries commented examples, so the rule has to
  // be written by the workflow itself; otherwise new changes land as `# Proposal`.
  assert.match(compat, /def ensure_proposal_title_rule\(/);
  assert.match(compat, /TITLE_RULE_ANCHOR/);
  assert.match(compat, /title_rule = ensure_proposal_title_rule\(root\)/);
  // Text-based insertion keeps the template's comment block and user rules.
  assert.doesNotMatch(compat, /import yaml/);
  assert.match(compat, /config\.read_bytes\(\)\.decode\("utf-8-sig"\)/);
  assert.match(doctor, /TITLE_RULE_ANCHOR, detect_project_mode/);
  assert.match(doctor, /def _check_proposal_title_rule\(/);
  assert.match(doctor, /_check_proposal_title_rule\(project, warnings\)/);
});
