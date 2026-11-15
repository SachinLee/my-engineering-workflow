#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const exists = (relative) => fs.existsSync(path.join(root, relative));

const skill = "project-standards";
const references = [
  "references/common.md",
  "references/java.md",
  "references/spring-mybatis-plus.md",
  "references/project-agents-template.md",
];

assert.ok(exists(`skills/${skill}/SKILL.md`), "project-standards SKILL.md is missing");
for (const reference of references) {
  assert.ok(exists(`skills/${skill}/${reference}`), `${reference} is missing`);
}

const body = read(`skills/${skill}/SKILL.md`);
assert.match(body, /^---\nname: project-standards\ndescription:/m);
assert.match(body, /project/i, "skill must state that project rules take precedence");
assert.match(body, /Select only|select only|选择/, "skill must select only relevant references");
assert.match(body, /Go|Rust|Python|Vue/, "deferred language scope must be explicit");
assert.match(body, /absolute path/i, "fresh-child handoff must use absolute paths for new reads");
assert.match(body, /inline|内联/i, "handoff must inline applicable rules");

const common = read(`skills/${skill}/references/common.md`);
assert.match(common, /AGENTS\.md/);
assert.match(common, /manifest/i);
assert.match(common, /UNVERIFIED/);

const java = read(`skills/${skill}/references/java.md`);
assert.match(java, /JDK/);
assert.match(java, /JPA/, "JPA guidance must defer to project dependencies");
assert.match(java, /Repository/, "extra repository layer must not be mandated");
assert.match(java, /MyBatis-Plus/);

const mybatis = read(`skills/${skill}/references/spring-mybatis-plus.md`);
for (const required of [
  /#\{/,
  /\$\{/,
  /\{0\}/,
  /last/,
  /ALWAYS/,
  /PaginationInnerInterceptor/,
  /TableLogic|logical delete/i,
  /@Transactional/,
  /@Version|optimistic/i,
  /actual database|real database|真实数据库/i,
  /https:\/\/baomidou\.com\/en\/guides\/wrapper\//,
  /block-attack/,
]) {
  assert.match(mybatis, required, `MyBatis-Plus reference missing ${required}`);
}
assert.match(mybatis, /(never|do not|不要|禁止)[^.]{0,80}(global|全局)[^.]{0,80}ALWAYS/i, "must forbid a global ALWAYS strategy");
assert.match(mybatis, /do not|never|must not|不要|禁止/i);

const template = read(`skills/${skill}/references/project-agents-template.md`);
assert.match(template, /<project|\[project|占位|placeholder/i);
assert.doesNotMatch(template, /csgops/i);

const notice = read(`skills/${skill}/NOTICE.md`);
assert.match(notice, /25278e7d7b6cf6e6a4e7a6c8e10f14ff22f0eb5b/);
assert.match(notice, /MIT/);
assert.match(notice, /Copyright \(c\) 2026 Affaan Mustafa/);

for (const relative of [
  "scripts/install.ps1",
  "scripts/doctor.py",
  "config/omp-workflow.yml",
]) {
  assert.match(read(relative), /project-standards/, `${relative} must manage the seventh skill`);
}

const router = read("skills/run-engineering-workflow/SKILL.md");
assert.match(router, /project-standards/);
assert.match(router, /七|seven/);

const planner = read("skills/plan-solution/SKILL.md");
assert.match(planner, /project-standards|project standards/i);
assert.match(planner, /absolute\s+paths?/i);

const reviewer = read("skills/review-implementation/SKILL.md");
assert.match(reviewer, /project-standards|project standards/i);
assert.match(reviewer, /Standards/i);

for (const relative of [
  "agents/workflow-planner.md",
  "agents/workflow-reviewer.md",
  ".omp/agents/workflow-planner.md",
  ".omp/agents/workflow-reviewer.md",
  ".pi/agents/workflow-planner.md",
  ".pi/agents/workflow-reviewer.md",
]) {
  assert.match(read(relative), /project standards|project-standards/i, `${relative} must carry standards guidance`);
}

const installer = read("scripts/install.ps1");
assert.match(installer, /seven|七/i, "installer prose must agree on seven canonical skills");

for (const relative of ["README.md", "ARCHITECTURE.md"]) {
  assert.doesNotMatch(read(relative), /六个 canonical skill|六个 skill|six canonical skills|six skills/i, `${relative} still claims six skills`);
  assert.match(read(relative), /七个|seven/, `${relative} must document seven skills`);
}

console.log("project standards contracts passed");
