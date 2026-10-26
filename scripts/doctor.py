#!/usr/bin/env python3
"""Validate a my-engineering-workflow installation without mutating it."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path


from openspec_compat import TITLE_RULE_ANCHOR, detect_project_mode

SKILLS = (
    "run-engineering-workflow",
    "clarify-requirements",
    "plan-solution",
    "review-implementation",
    "finish-with-evidence",
    "archive-task",
)
AGENTS = ("workflow-planner", "workflow-implementer", "workflow-reviewer")
UPSTREAM_SKILLS = (
    "grill-with-docs",
    "tdd",
    "code-review",
    "ponytail-review",
    "domain-modeling",
)
HARNESS_CHOICES = ("Codex", "OMP", "Claude", "Pi", "Both", "All")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an engineering workflow installation.")
    parser.add_argument("--scope", choices=("User", "Project"), default="User")
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


def is_directory_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def check_shared_installation(harness: str, scope: str, project: Path | None, home: Path, errors: list[str]) -> None:
    shared = home / ".agents" / "skills"
    check_skills(shared, "shared", errors)
    helper = shared / "run-engineering-workflow" / "scripts" / "openspec_compat.py"
    if not helper.is_file():
        errors.append(f"Missing shared OpenSpec helper: {helper}")
    legacy = []
    if selected(harness, "Codex"):
        legacy.append(home / ".codex" / "skills")
        if scope == "Project" and project:
            legacy.append(project / ".agents" / "skills")
    if selected(harness, "OMP"):
        legacy.append(omp_user_root(home) / "skills")
        if scope == "Project" and project:
            legacy.append(project / ".omp" / "skills")
    if selected(harness, "Pi"):
        override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
        legacy.append((Path(override).expanduser() if override else home / ".pi" / "agent") / "skills")
        if scope == "Project" and project:
            legacy.extend((project / ".agents" / "skills", project / ".pi" / "skills"))
    if selected(harness, "Claude"):
        roots = [home / ".claude" / "skills"]
        if scope == "Project" and project:
            roots.append(project / ".claude" / "skills")
        for root in roots:
            for skill in SKILLS:
                entry = root / skill
                try:
                    valid = is_directory_link(entry) and entry.is_dir() and entry.resolve() == (shared / skill).resolve()
                except (OSError, RuntimeError):
                    valid = False
                if not valid:
                    errors.append(f"Invalid or missing Claude skill link: {entry}; expected {shared / skill}")
    # Overrides and ProjectPath=HOME can make a native root the shared root itself.
    shared_root = shared.resolve()
    for root in {path.resolve() for path in legacy} - {shared_root}:
        for skill in SKILLS:
            entry = root / skill
            if entry.exists() or is_directory_link(entry):
                errors.append(f"Legacy skill entry may shadow shared installation: {entry}")


def check_agents(root: Path, label: str, errors: list[str]) -> None:
    for agent in AGENTS:
        if not (root / f"{agent}.md").is_file():
            errors.append(f"Missing {label} agent: {agent}")


def skill_whitelist_entries(body: str) -> set[str]:
    match = re.search(r"(?ms)^skills:\s*^\s{2}includeSkills:\s*(.*?)(?=^\S|\Z)", body)
    if not match:
        return set()
    raw = re.findall(r"(?m)^\s*-\s+([^\s#]+)", match.group(1))
    return {re.sub(r'^["\']|["\']$', "", entry) for entry in raw}


def whitelist_covers(entries: set[str], skill: str) -> bool:
    # includeSkills holds glob patterns, so "*-tdd" and "*" both cover a skill.
    return any(fnmatch.fnmatchcase(skill, entry) for entry in entries)


def omp_user_root(home: Path) -> Path:
    override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return home / ".omp" / "agent"


def check_skill_whitelist(path: Path, label: str, errors: list[str]) -> None:
    """OMP hides skills that a non-empty includeSkills allowlist does not cover.
    An absent file, absent key, or empty list means "no filtering", which is healthy."""
    if not path.is_file():
        return
    included = skill_whitelist_entries(path.read_text(encoding="utf-8"))
    if not included:
        return
    for skill in SKILLS:
        if not whitelist_covers(included, skill):
            errors.append(f"OMP {label} skill whitelist is missing: {skill}")


def check_omp_overlay(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"Missing OMP workflow overlay: {path}")
        return
    body = path.read_text(encoding="utf-8")
    check_skill_whitelist(path, "overlay", errors)
    for required, label in (
        ('workflow-planner: "@plan"', "workflow-planner"),
        ('workflow-implementer: "@task"', "workflow-implementer"),
        ('workflow-reviewer: "@advisor"', "workflow-reviewer"),
        ('workflow-implementer: "off"', "agentPrewalk.workflow-implementer"),
        ("prewalk:\n  enabled: false", "prewalk.enabled: false"),
    ):
        if required not in body:
            errors.append(f"OMP overlay is missing required setting: {label}")
    if "trellis" in body.lower():
        errors.append("OMP overlay still references Trellis; the record system is .workflow/.")


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


def _check_proposal_title_rule(project: Path, warnings: list[str]) -> None:
    """Warn when an initialized project cannot produce readable change titles.

    `create_change` adds the rule for new changes, so this catches projects that
    were initialized before the rule existed and would keep writing `# Proposal`.
    """
    config = next(
        (path for path in (project / "openspec" / "config.yaml", project / "openspec" / "config.yml") if path.is_file()),
        None,
    )
    if config is None:
        return
    try:
        text = config.read_text(encoding="utf-8-sig")
    except OSError as exc:
        warnings.append(f"Could not read {config}: {exc}")
        return
    if TITLE_RULE_ANCHOR in text:
        return
    warnings.append(
        f"{config} has no proposal H1 title rule, so new changes keep landing as "
        "`# Proposal` and show up in listings as their English change id. Creating a "
        "change through `create_change` adds the rule; existing projects can add it to "
        "`rules.proposal` manually."
    )


def check_record_layout(project: Path, warnings: list[str], errors: list[str]) -> None:
    """Check the canonical OpenSpec record system and legacy read-only fallbacks."""
    has_openspec = any((project / "openspec" / name).is_file() for name in ("config.yaml", "config.yml"))
    if has_openspec:
        result = detect_project_mode(project)
        if result["mode"] != "openspec" or result["status"] == "blocked":
            errors.append(f"OpenSpec record system is not usable: {result.get('reason', 'unknown error')}")
            return
        if result["status"] == "unselected":
            candidates = result.get("available_changes") or []
            titles = result.get("change_titles") or {}
            if candidates:
                labelled = ", ".join(
                    f"{cid}（{titles[cid]}）" if titles.get(cid) not in (None, "", cid) else cid
                    for cid in candidates
                )
                warnings.append(
                    f"OpenSpec is initialized under {project}/openspec with unarchived changes "
                    f"{labelled}. The routing flow recommends one and asks for "
                    "confirmation; nothing is auto-selected."
                )
            else:
                warnings.append(
                    f"OpenSpec is initialized under {project}/openspec but has no active change selected."
                )
        _check_proposal_title_rule(project, warnings)
        return

    if (project / ".workflow").is_dir():
        tasks = project / ".workflow" / "tasks"
        if not tasks.is_dir():
            warnings.append(f"{project}/.workflow exists but has no tasks/ directory.")
        for task in sorted(p for p in tasks.glob("*") if p.is_dir()) if tasks.is_dir() else []:
            if not (task / "prd.md").is_file():
                warnings.append(f"Task without prd.md: {task}")
            if not (task / "STATUS").is_file():
                warnings.append(f"Task without STATUS (treated as planning): {task}")
        warnings.append(
            f"Legacy .workflow record found under {project}/.workflow. It is recoverable and read-only; "
            "new state must be written under OpenSpec after explicit migration."
        )
        return
    if (project / ".trellis" / "tasks").is_dir():
        warnings.append(
            f"Legacy Trellis record found under {project}/.trellis. Read-only mode applies; "
            "new state is written under OpenSpec and no Trellis script may run."
        )
    else:
        warnings.append(
            f"No durable record system under {project}. The workflow will ask for consent "
            "before creating OpenSpec records."
        )

def check_injectors(project: Path, warnings: list[str]) -> None:
    """Head-of-input per-turn injection destroys the prompt cache; flag it."""
    found = []
    for path in (
        project / ".omp" / "extensions" / "trellis",
        project / ".pi" / "extensions" / "trellis",
        project / ".claude" / "hooks" / "inject-workflow-state.py",
        project / ".claude" / "hooks" / "session-start.py",
    ):
        if path.exists():
            found.append(str(path))
    hooks = project / ".codex" / "hooks.json"
    if hooks.is_file():
        try:
            body = json.loads(hooks.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            body = {}
        if "UserPromptSubmit" in (body.get("hooks") or {}):
            found.append(str(hooks) + " (UserPromptSubmit)")
    for item in found:
        warnings.append(
            f"Per-turn context injector present: {item}. Content placed before the "
            "conversation history invalidates the prompt cache on every turn; read state "
            "on demand instead."
        )


def check_omp(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("omp", errors)
    root = project / ".omp" if scope == "Project" else omp_user_root(home)

    check_agents(root / "agents", "OMP", errors)
    if not (root / "start-engineering-workflow.py").is_file():
        errors.append(f"Missing OMP Python launcher: {root / 'start-engineering-workflow.py'}")
    check_omp_overlay(root / "engineering-workflow.yml", errors)
    # Plain `omp` discovers skills through the user config.yml allowlist; the overlay
    # only reaches sessions started by the launcher.
    check_skill_whitelist(omp_user_root(home) / "config.yml", "user config", errors)
    if scope == "Project" and project is not None:
        check_skill_whitelist(project / ".omp" / "config.yml", "project config", errors)
    check_review_gate(root, errors)
    if scope == "Project" and project is not None:
        candidates = (
            project / ".omp" / "skills",
            project / ".agents" / "skills",
            home / ".omp" / "agent" / "skills",
            home / ".agents" / "skills",
            home / ".codex" / "skills",
        )
        for upstream in UPSTREAM_SKILLS:
            if not any((candidate / upstream / "SKILL.md").is_file() for candidate in candidates):
                warnings.append(f"Recommended upstream skill was not found: {upstream}")


def check_claude(scope: str, project: Path | None, home: Path, errors: list[str]) -> None:
    executable_exists("claude", errors)
    root = project / ".claude" if scope == "Project" else home / ".claude"

    check_agents(root / "agents", "Claude", errors)
    for command in ("engineering-workflow", "archive-task"):
        if not (root / "commands" / f"{command}.md").is_file():
            errors.append(f"Missing Claude command: {command}")


def check_pi(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("pi", errors)
    override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
    pi_user_root = Path(override).expanduser() if override else home / ".pi" / "agent"
    root = project / ".pi" if scope == "Project" else pi_user_root
    check_agents(root / "agents", "Pi", errors)
    node_modules = pi_user_root / "npm" / "node_modules"
    subagent_pkgs = (node_modules / "@narumitw" / "pi-subagents", node_modules / "pi-subagents")
    if not any(pkg.is_dir() for pkg in subagent_pkgs):
        warnings.append(
            "Optional Pi package pi-subagents was not found. Planning, bounded "
            "implementation, and independent review will remain in the main Pi session.",
        )


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
            else:
                check_record_layout(project, warnings, errors)
                check_injectors(project, warnings)
    if args.scope == "Project" and project is None:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    home = Path.home()
    check_shared_installation(args.harness, args.scope, project, home, errors)
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
