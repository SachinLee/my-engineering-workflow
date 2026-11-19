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
import sys
from pathlib import Path

try:  # Python 3.11+; 3.9/3.10 use the flat-role scanner below instead of a dependency.
    import tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.9/3.10 and by tests
    tomllib = None  # type: ignore[assignment]


from openspec_compat import TITLE_RULE_ANCHOR, detect_project_mode

SKILLS = (
    "run-engineering-workflow",
    "clarify-requirements",
    "plan-solution",
    "review-implementation",
    "finish-with-evidence",
    "archive-task",
    "project-standards",
)
AGENTS = ("workflow-planner", "workflow-implementer", "workflow-reviewer")
AGENT_FILES = tuple(f"{agent}.md" for agent in AGENTS)
CODEX_AGENT_FILES = tuple(f"{agent}.toml" for agent in AGENTS)
CODEX_AGENT_FIELDS = ("name", "description", "developer_instructions")
UPSTREAM_SKILLS = (
    "grill-with-docs",
    "tdd",
    "code-review",
    "ponytail-review",
    "domain-modeling",
)
HARNESS_CHOICES = ("Codex", "OMP", "Claude", "Pi", "OpenCode", "Both", "All")


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


def pi_skill_link_roots(scope: str, project: Path | None, home: Path) -> list[Path]:
    """Return the native Pi skill roots the installer manages as shared links."""
    override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
    roots = [(Path(override).expanduser() if override else home / ".pi" / "agent") / "skills"]
    if scope == "Project" and project:
        roots.append(project / ".pi" / "skills")
    shared = home / ".agents" / "skills"
    try:
        shared_key = shared.resolve()
    except (OSError, RuntimeError):
        shared_key = shared
    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        try:
            key = root.resolve()
        except (OSError, RuntimeError):
            key = root
        if key == shared_key or key in seen:
            continue
        seen.add(key)
        unique.append(root)
    return unique


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
        # Pi loads <agent-dir>/skills and .pi/skills natively; the installer keeps
        # a managed link from each root to the shared tree instead of a copy.
        for root in pi_skill_link_roots(scope, project, home):
            for skill in SKILLS:
                entry = root / skill
                try:
                    valid = is_directory_link(entry) and entry.is_dir() and entry.resolve() == (shared / skill).resolve()
                except (OSError, RuntimeError):
                    valid = False
                if not valid:
                    errors.append(f"Invalid or missing Pi skill link: {entry}; expected {shared / skill}")
        if scope == "Project" and project:
            legacy.append(project / ".agents" / "skills")
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
    if selected(harness, "OpenCode"):
        # OpenCode discovers ~/.agents/skills and .agents/skills natively, so a
        # copy under its own skills root would shadow the shared tree.
        legacy.append(opencode_user_root(home) / "skills")
        if scope == "Project" and project:
            legacy.append(project / ".agents" / "skills")
            legacy.append(project / ".opencode" / "skills")
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


def opencode_user_root(home: Path) -> Path:
    override = os.environ.get("OPENCODE_CONFIG_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return home / ".config" / "opencode"


def repo_source_root() -> Path | None:
    """Return the repository that ships the templates, or None when doctor runs alone."""
    candidate = Path(__file__).resolve().parents[1]
    return candidate if (candidate / "skills").is_dir() else None


def check_managed_drift(
    source: Path,
    installed: Path,
    names: tuple[str, ...],
    label: str,
    warnings: list[str],
) -> None:
    """Report installed files whose content no longer matches the shipped template.

    Drift is a warning, not an error: a local edit may be intentional, and the
    installer keeps such edits in the shared backup directory when it refreshes.
    """
    for name in names:
        template = source / name
        target = installed / name
        if not template.is_file() or not target.is_file():
            continue
        try:
            same = template.read_bytes() == target.read_bytes()
        except OSError as exc:
            warnings.append(f"Could not compare {label} file {target}: {exc}")
            continue
        if not same:
            warnings.append(
                f"{label} file differs from the shipped template: {target}. "
                "Re-run the installer to refresh it; a local edit is preserved in "
                "~/.agents/backups/my-engineering-workflow/."
            )


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
            errors.append(f"OMP {label} skill whitelist is missing: {skill} ({path})")


def check_omp_overlay(path: Path, errors: list[str], warnings: list[str]) -> None:
    if not path.is_file():
        warnings.append(
            f"Optional OMP workflow overlay is missing: {path}. "
            "The default `omp` command uses the regular OMP configuration."
        )
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
    launcher = root / "start-engineering-workflow.py"
    if not launcher.is_file():
        warnings.append(
            f"Optional OMP Python launcher is missing: {launcher}. "
            "Plain `omp` runs without it; only the launcher wrapper needs it."
        )
    check_omp_overlay(root / "engineering-workflow.yml", errors, warnings)
    source = repo_source_root()
    if source is not None:
        check_managed_drift(source / ".omp" / "agents", root / "agents", AGENT_FILES, "OMP agent", warnings)
    check_skill_whitelist(omp_user_root(home) / "config.yml", "user config", errors)
    if scope == "Project" and project is not None:
        check_skill_whitelist(project / ".omp" / "config.yml", "project config", errors)
    # Static checks cannot observe a real session, so dispatch is always unproven here.
    warnings.append(
        "OMP runtime dispatch and skill loading: UNVERIFIED "
        "(static checks only; confirm with a live `omp` session.)"
    )
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


def check_claude(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("claude", errors)
    root = project / ".claude" if scope == "Project" else home / ".claude"

    check_agents(root / "agents", "Claude", errors)
    for command in ("engineering-workflow", "archive-task"):
        if not (root / "commands" / f"{command}.md").is_file():
            errors.append(f"Missing Claude command: {command}")
    source = repo_source_root()
    if source is not None:
        check_managed_drift(source / "agents", root / "agents", AGENT_FILES, "Claude agent", warnings)
        check_managed_drift(
            source / "commands",
            root / "commands",
            ("engineering-workflow.md", "archive-task.md"),
            "Claude command",
            warnings,
        )


def check_pi(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("pi", errors)
    override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
    pi_user_root = Path(override).expanduser() if override else home / ".pi" / "agent"
    root = project / ".pi" if scope == "Project" else pi_user_root
    check_agents(root / "agents", "Pi", errors)
    source = repo_source_root()
    if source is not None:
        check_managed_drift(source / ".pi" / "agents", root / "agents", AGENT_FILES, "Pi agent", warnings)
    link_roots = pi_skill_link_roots(scope, project, home)
    if link_roots:
        shared = home / ".agents" / "skills"
        installed = 0
        for link_root in link_roots:
            for skill in SKILLS:
                entry = link_root / skill
                try:
                    if is_directory_link(entry) and entry.is_dir() and entry.resolve() == (shared / skill).resolve():
                        installed += 1
                except (OSError, RuntimeError):
                    continue
        warnings.append(f"Pi native shared skill entry installed: {installed}/{len(link_roots) * len(SKILLS)}")
        warnings.append("Runtime skill loading and delegation: UNVERIFIED")
    node_modules = pi_user_root / "npm" / "node_modules"
    subagent_pkgs = (node_modules / "@narumitw" / "pi-subagents", node_modules / "pi-subagents")
    if not any(pkg.is_dir() for pkg in subagent_pkgs):
        warnings.append(
            "Optional Pi package pi-subagents was not found. Planning, bounded "
            "implementation, and independent review will remain in the main Pi session.",
        )


def frontmatter_model(path: Path) -> str | None:
    """Return the agent's `model` frontmatter value without parsing the body."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = re.match(r"(?s)\A---\r?\n(.*?)\r?\n---", text)
    if not match:
        return None
    for line in match.group(1).splitlines():
        hit = re.match(r"\s*model\s*:\s*(.+?)\s*$", line)
        if hit:
            return hit.group(1).strip().strip("\"'")
    return None


def check_pi_overrides(scope: str, home: Path, warnings: list[str]) -> None:
    """Report which Pi workflow overrides exist; never rewrite or judge them.

    Pi agent files must stay model-free so the user's `agentOverrides` keeps
    winning. The doctor only reports the wiring so a silent model change is
    visible instead of mysterious.
    """
    override = os.environ.get("PI_CODING_AGENT_DIR", "").strip()
    pi_user_root = Path(override).expanduser() if override else home / ".pi" / "agent"
    settings = pi_user_root / "settings.json"
    if not settings.is_file():
        return
    try:
        body = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        warnings.append(f"Pi settings could not be parsed, so agent overrides are unknown: {settings}")
        return
    overrides = ((body.get("subagents") or {}).get("agentOverrides") or {}) if isinstance(body, dict) else {}
    configured = [name for name in AGENTS if isinstance(overrides, dict) and name in overrides]
    if configured:
        warnings.append(
            "Pi agentOverrides are user-owned and left untouched for: "
            + ", ".join(configured)
            + ". Pi agents declare no model, so those overrides stay effective."
        )
    agent_root = pi_user_root / "agents"
    for name in AGENTS:
        path = agent_root / f"{name}.md"
        if not path.is_file():
            continue
        model = frontmatter_model(path)
        if model:
            warnings.append(
                f"Pi agent declares its own model ({model}), so a Pi agentOverride cannot take effect: {path}. "
                "Pi agents should omit `model`."
            )


def check_opencode(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    executable_exists("opencode", errors)
    root = project / ".opencode" if scope == "Project" else opencode_user_root(home)

    check_agents(root / "agents", "OpenCode", errors)
    for command in ("engineering-workflow", "archive-task"):
        if not (root / "commands" / f"{command}.md").is_file():
            errors.append(f"Missing OpenCode command: {command}")
    for name in AGENTS:
        path = root / "agents" / f"{name}.md"
        if not path.is_file():
            continue
        model = frontmatter_model(path)
        if model:
            warnings.append(
                f"OpenCode agent pins its own model ({model}), so the user's default model no longer applies: {path}. "
                "The shipped templates omit `model`."
            )
    source = repo_source_root()
    if source is not None:
        check_managed_drift(source / ".opencode" / "agents", root / "agents", AGENT_FILES, "OpenCode agent", warnings)
        check_managed_drift(
            source / "commands",
            root / "commands",
            ("engineering-workflow.md", "archive-task.md"),
            "OpenCode command",
            warnings,
        )


def parse_codex_agent(text: str) -> tuple[dict[str, object] | None, str | None]:
    """Parse one Codex role TOML and require its contract fields.

    Returns ``(fields, None)`` when valid, ``(None, problem)`` when invalid, and
    ``(None, None)`` when no parser is available. Python 3.9/3.10 have no
    ``tomllib`` and no TOML dependency may be added, so no syntax, field, or
    role-name verdict is possible there. The caller owns role-name matching.
    """
    if tomllib is None:
        return None, None
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.strip():
        return None, "is empty"
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return None, f"is not valid TOML ({exc})"
    missing = [
        key
        for key in CODEX_AGENT_FIELDS
        if not isinstance(data.get(key), str) or not str(data[key]).strip()
    ]
    if missing:
        return None, "is missing a non-empty string field: " + ", ".join(missing)
    return data, None


def check_codex(scope: str, project: Path | None, home: Path, errors: list[str], warnings: list[str]) -> None:
    """Report installed artifacts, static discoverability, and unknown runtime facts."""
    root = project / ".codex" if scope == "Project" and project else home / ".codex"
    agents = root / "agents"
    installed = 0
    valid = 0
    for name in AGENTS:
        path = agents / f"{name}.toml"
        if not path.is_file():
            errors.append(f"Missing Codex native workflow agent: {path}")
            continue
        installed += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append(f"Codex workflow agent could not be read ({exc}): {path}")
            continue
        # Text-only concerns stay diagnosable even without a TOML parser.
        if re.search(r"(?m)^\s*(?:model|model_provider|model_reasoning_effort)\s*=", text):
            errors.append(f"Codex workflow agent declares a model key: {path}")
        elif re.search(r"(?m)^\s*sandbox_mode\s*=", text):
            errors.append(f"Codex workflow agent declares sandbox_mode: {path}")
        data, problem = parse_codex_agent(text)
        if data is None and problem is None:
            continue
        if problem is not None:
            errors.append(f"Codex workflow agent {problem}: {path}")
            continue
        declared = str(data["name"]).strip()
        if declared != name:
            errors.append(
                f"Codex workflow agent declares name {declared!r}, expected {name!r}: {path}"
            )
            continue
        valid += 1
    source = repo_source_root()
    if source is not None:
        check_managed_drift(source / ".codex" / "agents", agents, CODEX_AGENT_FILES, "Codex agent", warnings)
    warnings.append(f"Codex native workflow agent TOMLs installed: {installed}/{len(AGENTS)}")
    if tomllib is None:
        warnings.append(
            "Static TOML validation: UNVERIFIED (tomllib is unavailable on this Python; "
            "re-run doctor with Python 3.11+ to validate TOML syntax, required fields, and role names)"
        )
        warnings.append("Statically discoverable: unknown")
    else:
        if valid != installed:
            warnings.append(
                f"Codex native workflow agent TOMLs with a valid role contract: {valid}/{len(AGENTS)}"
            )
        discoverable = installed == len(AGENTS) and valid == len(AGENTS)
        warnings.append(f"Statically discoverable: {'yes' if discoverable else 'no'}")
    warnings.append("Runtime discovery, delegation, and independent review: UNVERIFIED")
    for name in AGENTS:
        legacy = home / ".codex" / "agents" / f"{name}.md"
        if not legacy.is_file():
            continue
        try:
            body = legacy.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if ".trellis/tasks/" in body:
            warnings.append(
                f"Stale Trellis-era Codex agent definition remains: {legacy}. "
                "Re-run the installer to back it up and remove it."
            )


def check_claude_model_aliases(scope: str, project: Path | None, home: Path, warnings: list[str]) -> None:
    """Report alias collapse without printing credentials or rewriting settings.

    Providers that route both alias slots to one model are common; the point is to
    make "Opus" versus "Sonnet" selection visible before someone blames the agents.
    """
    root = project / ".claude" if scope == "Project" else home / ".claude"
    settings = root / "settings.json"
    if not settings.is_file():
        return
    try:
        body = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        warnings.append(f"Claude settings could not be parsed, so model aliases are unknown: {settings}")
        return
    env = body.get("env") if isinstance(body, dict) else None
    if not isinstance(env, dict):
        return
    opus = str(env.get("ANTHROPIC_DEFAULT_OPUS_MODEL") or "").strip()
    sonnet = str(env.get("ANTHROPIC_DEFAULT_SONNET_MODEL") or "").strip()
    if opus and sonnet and opus == sonnet:
        warnings.append(
            f"Claude Opus and Sonnet aliases both resolve to {sonnet}, so a workflow agent "
            "that asks for Opus actually runs on that model. Models are user-owned; the "
            "installer leaves settings.json untouched."
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
        check_claude(args.scope, project, home, errors, warnings)
        check_claude_model_aliases(args.scope, project, home, warnings)
    if selected(args.harness, "Pi"):
        check_pi(args.scope, project, home, errors, warnings)
        check_pi_overrides(args.scope, home, warnings)
    if selected(args.harness, "OpenCode"):
        check_opencode(args.scope, project, home, errors, warnings)
    if selected(args.harness, "Codex"):
        check_codex(args.scope, project, home, errors, warnings)
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
