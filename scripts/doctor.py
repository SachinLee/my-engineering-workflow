#!/usr/bin/env python3
"""Validate a my-engineering-workflow installation without mutating it."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SKILLS = (
    "run-engineering-workflow",
    "clarify-requirements",
    "plan-solution",
    "review-implementation",
    "finish-with-evidence",
)
HARNESS_CHOICES = ("Codex", "OMP", "Claude", "Pi", "Both", "All")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an engineering workflow installation.")
    parser.add_argument("--scope", choices=("User", "Project"), default="Project")
    parser.add_argument("--harness", choices=HARNESS_CHOICES, default="Both")
    parser.add_argument("--project-path")
    return parser.parse_args()


def selected(harness: str, name: str) -> bool:
    return name == harness or harness == "All" or (harness == "Both" and name in {"Codex", "OMP"})


def executable_exists(name: str, errors: list[str]) -> None:
    if shutil.which(name) is None:
        errors.append(f"{name} was not found on PATH.")


def check_skills(root: Path, label: str, errors: list[str]) -> None:
    for skill in SKILLS:
        if not (root / skill / "SKILL.md").is_file():
            errors.append(f"Missing {label} skill: {skill}")


def check_agents(root: Path, agents: tuple[str, ...], label: str, errors: list[str]) -> None:
    for agent in agents:
        if not (root / f"{agent}.md").is_file():
            errors.append(f"Missing {label} agent: {agent}")


def overlay_skill_names(body: str) -> set[str]:
    match = re.search(r"(?ms)^skills:\s*^\s{2}includeSkills:\s*(.*?)(?=^\S|\Z)", body)
    if not match:
        return set()
    return set(re.findall(r"(?m)^\s*-\s+([^\s#]+)", match.group(1)))


def check_omp_overlay(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing OMP workflow overlay: {path}")
        return
    body = path.read_text(encoding="utf-8")
    included = overlay_skill_names(body)
    for skill in SKILLS:
        if skill not in included:
            errors.append(f"OMP overlay skill whitelist is missing: {skill}")
    for required, label in (
        ('workflow-planner: "@plan"', "workflow-planner"),
        ('trellis-implement: "@task"', "trellis-implement"),
        ('trellis-check: "@advisor"', "trellis-check"),
        ('workflow-reviewer: "@advisor"', "workflow-reviewer"),
        ("prewalk:\n  enabled: false", "prewalk.enabled: false"),
    ):
        if required not in body:
            errors.append(f"OMP overlay is missing required setting: {label}")


def check_review_gate(root: Path, errors: list[str]) -> None:
    gate = root / "extensions" / "workflow-review-gate"
    entry = gate / "index.ts"
    core = gate / "lib" / "review-gate-core.js"
    tests = gate / "tests" / "review-gate.test.js"
    for path in (entry, core, tests):
        if not path.is_file():
            errors.append(f"Missing OMP workflow review gate file: {path}")
    if entry.is_file() and 'pi.on("tool_call"' not in entry.read_text(encoding="utf-8"):
        errors.append("OMP workflow review gate does not register a tool_call handler.")
    node = shutil.which("node")
    if node is None:
        errors.append("node was not found on PATH; cannot verify the OMP workflow review gate.")
    elif tests.is_file():
        result = subprocess.run(
            [node, "--test", str(tests)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            errors.append("OMP workflow review gate contract tests failed.")


def check_omp(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("omp", errors)
    root = project / ".omp" if scope == "Project" else home / ".omp" / "agent"
    check_skills(root / "skills", "OMP", errors)
    agents = ("workflow-planner", "workflow-reviewer")
    if scope == "Project":
        agents += ("trellis-implement", "trellis-check")
    check_agents(root / "agents", agents, "OMP", errors)
    if not (root / "start-engineering-workflow.py").is_file():
        errors.append(f"Missing OMP Python launcher: {root / 'start-engineering-workflow.py'}")
    check_omp_overlay(root / "engineering-workflow.yml", errors)
    check_review_gate(root, errors)
    if scope == "Project" and project is not None:
        candidates = (project / ".omp" / "skills", project / ".agents" / "skills", home / ".omp" / "agent" / "skills", home / ".codex" / "skills")
        for upstream in ("trellis-before-dev", "grill-with-docs", "tdd", "code-review", "ponytail-review"):
            if not any((candidate / upstream / "SKILL.md").is_file() for candidate in candidates):
                warnings.append(f"Recommended upstream skill was not found: {upstream}")


def check_claude(scope: str, project: Path | None, home: Path, errors: list[str]) -> None:
    executable_exists("claude", errors)
    root = project / ".claude" if scope == "Project" else home / ".claude"
    check_skills(root / "skills", "Claude", errors)
    check_agents(root / "agents", ("workflow-planner", "workflow-reviewer"), "Claude", errors)
    if not (root / "commands" / "engineering-workflow.md").is_file():
        errors.append("Missing Claude command: engineering-workflow")
    if scope == "Project":
        check_agents(root / "agents", ("trellis-implement", "trellis-check"), "Trellis Claude", errors)


def check_pi(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("pi", errors)
    pi_user_root = Path(os.environ.get("PI_CODING_AGENT_DIR", home / ".pi" / "agent")).expanduser()
    root = project / ".pi" if scope == "Project" else pi_user_root
    skills_root = project / ".agents" / "skills" if scope == "Project" else root / "skills"
    check_skills(skills_root, "Pi", errors)
    check_agents(root / "agents", ("workflow-planner", "workflow-reviewer"), "Pi", errors)
    if not (pi_user_root / "npm" / "node_modules" / "@narumitw" / "pi-subagents").is_dir():
        warnings.append("Optional Pi package @narumitw/pi-subagents was not found. Planning and independent review will remain in the main Pi session.")
    if scope != "Project" or project is None:
        return
    check_agents(root / "agents", ("trellis-implement", "trellis-check"), "Trellis Pi", errors)
    if not (root / "extensions" / "trellis" / "index.ts").is_file():
        errors.append("Missing Trellis Pi extension: .pi\\extensions\\trellis\\index.ts. Run trellis init --pi or trellis update.")
    settings_path = root / "settings.json"
    if not settings_path.is_file():
        errors.append("Missing Pi project settings: .pi\\settings.json. Run trellis init --pi or trellis update.")
        return
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Could not parse Pi project settings: {exc.msg}")
        return
    if "./extensions/trellis/index.ts" not in settings.get("extensions", []):
        errors.append("Pi project settings do not load the Trellis extension.")
    if "./prompts" not in settings.get("prompts", []):
        errors.append("Pi project settings do not load Trellis prompts.")


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    project: Path | None = None
    if args.scope == "Project":
        if not args.project_path:
            errors.append("ProjectPath is required when Scope is Project.")
        else:
            project = Path(args.project_path).expanduser().resolve()
            if not project.is_dir():
                errors.append(f"Project path was not found: {project}")
            elif not (project / ".trellis" / "workflow.md").is_file():
                errors.append(f"Trellis workflow was not found under {project}\\.trellis.")
    if args.scope == "Project" and project is None:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    home = Path.home()
    if selected(args.harness, "Codex"):
        root = project / ".agents" / "skills" if args.scope == "Project" and project else home / ".codex" / "skills"
        check_skills(root, "Codex", errors)
    if selected(args.harness, "OMP"):
        check_omp(args.scope, project, home, errors, warnings)
    if selected(args.harness, "Claude"):
        check_claude(args.scope, project, home, errors)
    if selected(args.harness, "Pi"):
        check_pi(args.scope, project, home, errors, warnings)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Workflow installation is healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
