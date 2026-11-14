#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const exists = (relative) => fs.existsSync(path.join(root, relative));

const governancePath = "skills/run-engineering-workflow/references/workflow-governance.md";
const planSolutionPath = "skills/plan-solution/SKILL.md";
const casesPath = "evals/planning-ablation-cases.json";
const protocolPath = "evals/planning-ablation-protocol.md";

const evidenceBasedPlanning = () => {
  const text = read(governancePath);
  const heading = "## Evidence-Based Planning";
  const start = text.indexOf(heading);
  assert.notEqual(start, -1, "shared governance must retain Evidence-Based Planning");
  const end = text.indexOf("\n## ", start + heading.length);
  return text.slice(start, end === -1 ? undefined : end);
};

test("shared governance keeps a counterfactual deletion criterion for defensive mechanisms", () => {
  const ebp = evidenceBasedPlanning();
  const criterion = ebp.split(/\n(?=- )/).find((block) => /counterfactual|反事实/i.test(block));
  assert.ok(criterion, "Evidence-Based Planning must state a counterfactual deletion test");
  assert.match(criterion, /remov|delet|omit|drop/i, "counterfactual test must decide whether to remove a mechanism");
  assert.match(criterion, /\bAC\b|acceptance|不变量|invariant/i, "counterfactual must be anchored to an explicit AC or invariant");
  assert.match(criterion, /reachable|可达/i, "counterfactual must reference a reachable scenario");
  assert.match(criterion, /risk|风险/i, "dropped mechanisms must fall back to a recorded risk");
});

test("shared governance still requires necessary safeguards without per-line error checklists", () => {
  const ebp = evidenceBasedPlanning();
  for (const required of [
    /security|安全/i,
    /data integrity|数据完整性/i,
    /concurrency|并发/i,
    /resource cleanup|资源清理/i,
  ]) {
    assert.match(ebp, required, `Evidence-Based Planning must preserve ${required}`);
  }
  assert.match(ebp, /must preserve required/i, "simplicity must require preserving necessary safeguards");
  assert.match(ebp, /do not create another checklist\s+or require a separate justification for every ordinary error-handling line/i, "ordinary error handling must not become a per-line checklist");
});

test("plan-solution review step points to the shared counterfactual criterion", () => {
  const skill = read(planSolutionPath);
  const idx = skill.indexOf("Check proposed extra mechanisms");
  assert.ok(idx > -1, "plan-solution must keep its extra-mechanism review step");
  const region = skill.slice(idx, idx + 700);
  assert.match(region, /Evidence-Based Planning/, "review step must reference the shared Evidence-Based Planning rule");
  assert.match(region, /counterfactual|反事实/i, "review step must reference the counterfactual deletion test");
});

test("ablation case set parses, holds 10 sanitized cases, and covers every risk category", () => {
  assert.ok(exists(casesPath), `${casesPath} is missing`);
  const raw = JSON.parse(read(casesPath));
  assert.ok(Array.isArray(raw.cases), "cases must be an array");
  assert.equal(raw.cases.length, 10, "ablation set must freeze exactly 10 cases");
  const seen = new Set();
  for (const c of raw.cases) {
    assert.ok(c && typeof c === "object", "each case must be an object");
    assert.match(c.name, /^[a-z0-9-]+$/, `case name must be a slug: ${c.name}`);
    assert.ok(!seen.has(c.name), `duplicate case name: ${c.name}`);
    seen.add(c.name);
    assert.equal(c.source, "synthetic", `case ${c.name} must be marked synthetic (sanitized)`);
    assert.ok(c.risk_category, `case ${c.name} must declare a risk_category`);
    assert.ok(typeof c.prompt === "string" && c.prompt.length > 20, `case ${c.name} needs a real prompt`);
    assert.ok(Array.isArray(c.temptations) && c.temptations.length > 0, `case ${c.name} needs candidate defensive mechanisms`);
    assert.ok(Array.isArray(c.necessary_safeguards) && c.necessary_safeguards.length > 0, `case ${c.name} needs necessary safeguards`);
  }
  const categories = new Set(raw.cases.map((c) => c.risk_category));
  for (const required of ["simple", "ordinary", "high"]) {
    assert.ok(categories.has(required), `case set must include risk_category ${required}`);
  }
  assert.doesNotMatch(read(casesPath), /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/, "cases must not contain email-like identifiers");
});

test("ablation protocol defines a blind paired A/B run with a 4-axis rubric and NOT RUN rule", () => {
  const protocol = read(protocolPath);
  assert.match(protocol, /A\/B|对照|配对/i, "protocol must describe a paired A/B comparison");
  assert.match(protocol, /blind|盲|hidden|隐藏/i, "protocol must hide the arm during scoring");
  assert.match(protocol, /independent|独立/i, "protocol must use independent sessions");
  assert.match(protocol, /same model|固定模型|同一模型/i, "protocol must fix the model");
  assert.match(protocol, /NOT RUN/, "protocol must define the NOT RUN fallback");
  for (const axis of [/无依据机制|unfounded|无依据/i, /AC|不变量|覆盖/i, /可验证性|verifi/i, /实现工作量|effort|workload/i]) {
    assert.match(protocol, axis, `rubric must cover ${axis}`);
  }
  assert.match(protocol, /counterfactual|反事实|隔离/i, "protocol must confine high-risk checks to counterfactual/isolated validation");
  assert.match(protocol, /方向性|directional|不宣称|not significant|significan/i, "protocol must mark the pilot as directional, not statistically significant");
});

test("ablation protocol freezes a pre-change baseline and keeps scoring hints out of generation", () => {
  const protocol = read(protocolPath);
  assert.match(protocol, /变更前/, "A must be frozen before the candidate rule is introduced");
  assert.match(protocol, /完整提示.*差异/, "both prompts and their sole treatment difference must be retained");
  assert.match(protocol, /实际加载.*skill.*指令/i, "the baseline must account for injected instructions");
  assert.match(protocol, /temptations.*necessary_safeguards/, "scoring references must be reserved for blind evaluation");
});