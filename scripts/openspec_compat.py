#!/usr/bin/env python3
"""OpenSpec compatibility boundary for the engineering workflow.

The module deliberately keeps OpenSpec CLI calls and legacy file migration in one
small, testable surface. New callers should consume the returned dictionaries
rather than parse CLI text or inspect legacy directories themselves.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

MIN_OPENSPEC_VERSION = (1, 14, 0)
MIGRATION_VERSION = "1"
CHANGE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REQUIRED_STATUS_KEYS = {"changeName", "artifacts", "isPlanningComplete", "isComplete"}


class CompatibilityError(RuntimeError):
    """A safe, user-actionable compatibility failure."""


class MigrationError(CompatibilityError):
    """A migration failed without permission to mutate its source."""


def _version_tuple(value: str) -> Tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        raise CompatibilityError(f"Invalid OpenSpec version output: {value!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)


Executable = Union[str, Sequence[str]]


def _executable(path: Optional[Executable]) -> Executable:
    executable = path or shutil.which("openspec")
    if not executable:
        raise CompatibilityError("OpenSpec CLI was not found on PATH. Install OpenSpec >= 1.14.0.")
    return executable


def _run(executable: Executable, project: Path, args: Sequence[str], timeout: float) -> subprocess.CompletedProcess[str]:
    command = [executable] if isinstance(executable, str) else list(executable)
    try:
        return subprocess.run(
            [*command, *args],
            cwd=str(project),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CompatibilityError(
            f"OpenSpec command timed out after {timeout:g}s: openspec {' '.join(args)}"
        ) from exc
    except OSError as exc:
        raise CompatibilityError(f"Could not execute OpenSpec CLI: {exc}") from exc

def _json_command(
    executable: Executable, project: Path, args: Sequence[str], timeout: float
) -> Dict[str, Any]:
    result = _run(executable, project, [*args, "--json"], timeout)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise CompatibilityError(f"OpenSpec returned invalid JSON: {detail}") from exc
    if not isinstance(payload, dict):
        raise CompatibilityError("OpenSpec JSON response must be an object")
    if result.returncode != 0:
        message = _json_error_message(payload) or result.stderr.strip() or "command failed"
        raise CompatibilityError(message)
    return payload


def _json_error_message(payload: Dict[str, Any]) -> Optional[str]:
    statuses = payload.get("status")
    if not isinstance(statuses, list):
        return None
    messages = [
        item.get("message")
        for item in statuses
        if isinstance(item, dict) and isinstance(item.get("message"), str)
    ]
    return "; ".join(messages) if messages else None


def _check_version(executable: Executable, project: Path, timeout: float) -> str:
    result = _run(executable, project, ["--version"], timeout)
    if result.returncode != 0:
        raise CompatibilityError(result.stderr.strip() or "OpenSpec version check failed")
    version = _version_tuple(result.stdout)
    if version < MIN_OPENSPEC_VERSION:
        minimum = ".".join(str(part) for part in MIN_OPENSPEC_VERSION)
        raise CompatibilityError(
            f"OpenSpec {result.stdout.strip()} is too old; version {minimum} or newer is required."
        )
    return ".".join(str(part) for part in version)


def _has_openspec_root(project: Path) -> bool:
    return any((project / "openspec" / name).is_file() for name in ("config.yaml", "config.yml"))


TITLE_RULE_ANCHOR = "提案：<中文短标题>"


def _config_file(project: Path) -> Optional[Path]:
    config = project / "openspec" / "config.yaml"
    if config.is_file():
        return config
    fallback = project / "openspec" / "config.yml"
    return fallback if fallback.is_file() else None


def ensure_proposal_title_rule(project: os.PathLike[str] | str) -> Dict[str, Any]:
    """Idempotently add the Chinese H1 rule to a project's `openspec/config.yaml`.

    Planning artifacts are written by the agent from `openspec instructions
    proposal`, and a fresh project's config carries only commented-out examples,
    so without this rule a new change lands as `# Proposal` and its title is
    unreadable. Editing is text-based on purpose: a YAML round-trip would drop the
    template's comment block and any user comments. Existing configuration is
    never rewritten — the rule is inserted only when the anchor text is absent.
    """
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise CompatibilityError(f"Project root does not exist: {root}")
    config = _config_file(root)
    if config is None:
        return {"status": "skipped", "reason": "no openspec/config.yaml or config.yml"}
    try:
        # Read bytes, not text: `read_text` translates line endings, which would
        # make a CRLF file look like LF and get rewritten with the wrong newline.
        text = config.read_bytes().decode("utf-8-sig")
    except OSError as exc:
        return {"status": "failed", "reason": str(exc)}
    if TITLE_RULE_ANCHOR in text:
        return {"status": "unchanged", "config": str(config)}
    eol = "\r\n" if "\r\n" in text else "\n"
    line = f"    - Write the proposal H1 as `# 提案：<中文短标题>` so `openspec change list` and routing prompts show a readable Chinese title; keep the section headings `## Why` and `## What Changes` in English because OpenSpec parses those names.{eol}"
    lines = text.splitlines()
    proposal_index = None
    rules_index = None
    for index, current in enumerate(lines):
        if rules_index is None and current.startswith("rules:"):
            rules_index = index
        if proposal_index is None and re.match(r"^  proposal:\s*(?:#.*)?$", current):
            proposal_index = index
    if proposal_index is not None:
        end = len(lines)
        for index in range(proposal_index + 1, len(lines)):
            if lines[index].strip() and not lines[index].startswith("     "):
                end = index
                break
        lines.insert(end, line.rstrip("\r\n"))
    elif rules_index is not None:
        lines.insert(rules_index + 1, "  proposal:")
        lines.insert(rules_index + 2, line.rstrip("\r\n"))
    else:
        # `rules:` may only exist inside the template's comment block; append a
        # real block after the `context` value so the commented example stays put.
        end = len(lines)
        for index, current in enumerate(lines):
            if re.match(r"^rules:\s*", current) and not current.lstrip().startswith("#"):
                end = index
                break
        lines.insert(end, "")
        lines.insert(end + 1, "rules:")
        lines.insert(end + 2, "  proposal:")
        lines.insert(end + 3, line.rstrip("\r\n"))
    config.write_text(eol.join(lines) + eol, encoding="utf-8", newline="")
    return {"status": "updated", "config": str(config)}


def _safe_project_path(project: Path, candidate: Path, label: str) -> Path:
    project = project.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(project)
    except ValueError as exc:
        raise CompatibilityError(f"{label} is outside the project root: {candidate}") from exc
    return candidate


def _legacy_task(project: Path) -> Optional[Path]:
    current = project / ".workflow" / "CURRENT.md"
    if current.is_file():
        match = re.search(r"^task:\s*`?([^`\r\n]+)", current.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            candidate = _safe_project_path(project, project / match.group(1).strip(), "Legacy task")
            if candidate.is_dir() and candidate.parent == (project / ".workflow" / "tasks").resolve():
                return candidate
    tasks_root = project / ".workflow" / "tasks"
    if not tasks_root.is_dir():
        return None
    candidates = sorted(path for path in tasks_root.iterdir() if path.is_dir())
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise CompatibilityError(
            "Multiple legacy .workflow tasks exist; select one explicitly before recovery or migration."
        )
    return None


def _result(
    mode: str,
    status: str,
    source: str,
    change: Optional[str] = None,
    reason: Optional[str] = None,
    **details: Any,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "mode": mode,
        "source": source,
        "change": change,
        "status": status,
        "reason": reason,
    }
    payload.update(details)
    return payload


TITLE_RE = re.compile(r"^#\s+(?:Change:\s+)?(.+)$")


def _change_titles(root: Path, names: List[str]) -> Dict[str, str]:
    """Best-effort change titles from each proposal's H1. Never raises: an
    unreadable or placeholder title degrades to the change id, because routing
    only needs titles for display and must not block on them.

    Reads `proposal.md` directly instead of `openspec show <id> --json`: `show`
    fails with `Change must have a Why section` on every change whose proposal
    uses Chinese section names (6 of 8 in this repo), and costs a process per
    change. The regex mirrors OpenSpec's own `extractTitle`."""
    titles = {name: name for name in names}
    for name in names:
        if not CHANGE_ID_RE.fullmatch(name):
            continue
        try:
            text = (root / "openspec" / "changes" / name / "proposal.md").read_text(
                encoding="utf-8-sig", errors="replace"
            )
        except OSError:
            continue
        in_fence = False
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                # A `# comment` inside a fenced block is code, not the title.
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = TITLE_RE.match(line)
            if not match:
                continue
            cleaned = match.group(1).strip()
            if cleaned and cleaned.lower() != "proposal" and cleaned != name:
                titles[name] = cleaned
            break
    return titles


def _open_spec_names(
    executable: Executable, root: Path, timeout: float
) -> Tuple[str, List[str], Dict[str, str]]:
    """Read-only discovery: version check, list --json, root match, change names."""
    version = _check_version(executable, root, timeout)
    listing = _json_command(executable, root, ["list"], timeout)
    root_info = listing.get("root")
    if not isinstance(root_info, dict) or not isinstance(root_info.get("path"), str):
        raise CompatibilityError("OpenSpec did not return a resolved project root")
    if Path(root_info["path"]).expanduser().resolve() != root:
        raise CompatibilityError("OpenSpec resolved a different project root")
    changes = listing.get("changes")
    if not isinstance(changes, list) or any(not isinstance(item, dict) for item in changes):
        raise CompatibilityError("OpenSpec list response has no valid changes array")
    names = [item.get("name") for item in changes if isinstance(item.get("name"), str)]
    return version, names, _change_titles(root, names)


def list_changes(
    project: os.PathLike[str] | str,
    *,
    openspec_executable: Optional[Executable] = None,
    timeout: float = 15,
) -> Dict[str, Any]:
    """Read-only discovery of unarchived OpenSpec changes. Never creates or selects."""
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        return _result("blocked", "blocked", "none", reason=f"Project root does not exist: {root}")
    if not _has_openspec_root(root):
        return _result("blocked", "blocked", "none", reason="OpenSpec is not initialized in this project.")
    try:
        executable = _executable(openspec_executable)
        version, names, titles = _open_spec_names(executable, root, timeout)
    except CompatibilityError as exc:
        return _result("blocked", "blocked", "openspec", reason=str(exc))
    return _result(
        "openspec",
        "ready",
        "openspec",
        openspec_version=version,
        available_changes=names,
        change_titles=titles,
    )


def create_change(
    project: os.PathLike[str] | str,
    change_id: str,
    *,
    description: str,
    goal: str,
    schema: str = "spec-driven",
    openspec_executable: Optional[Executable] = None,
    timeout: float = 30,
) -> Dict[str, Any]:
    """Explicitly create one OpenSpec change after user confirmation. Never overwrites."""
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise CompatibilityError(f"Project root does not exist: {root}")
    if not _has_openspec_root(root):
        raise CompatibilityError("OpenSpec is not initialized; create_change cannot run in this project")
    if not CHANGE_ID_RE.fullmatch(change_id):
        raise CompatibilityError("Change id must contain lowercase letters, numbers, and hyphens only")
    executable = _executable(openspec_executable)
    payload = _json_command(
        executable,
        root,
        [
            "new",
            "change",
            change_id,
            "--description",
            description,
            "--goal",
            goal,
            "--schema",
            schema,
        ],
        timeout,
    )
    # The change's artifacts are authored from `openspec instructions proposal`,
    # so the title rule has to be in the project config before that read happens.
    title_rule = ensure_proposal_title_rule(root)
    return {"status": "created", "change": change_id, "detail": payload, "title_rule": title_rule}


def detect_project_mode(
    project: os.PathLike[str] | str,
    change: Optional[str] = None,
    *,
    openspec_executable: Optional[Executable] = None,
    timeout: float = 15,
) -> Dict[str, Any]:
    """Return the canonical mode for a project without mutating it."""
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        return _result("blocked", "blocked", "none", reason=f"Project root does not exist: {root}")

    if _has_openspec_root(root):
        try:
            executable = _executable(openspec_executable)
            version, names, titles = _open_spec_names(executable, root, timeout)
            selected = change
            if selected is None:
                # Consent-first routing: no auto-selection, no blocked state on
                # multiple changes. The main session matches intent against the
                # candidates and asks the user before creating or reusing.
                return _result(
                    "openspec",
                    "unselected",
                    "openspec",
                    openspec_version=version,
                    available_changes=names,
                    change_titles=titles,
                )
            if selected not in names:
                return _result(
                    "blocked",
                    "blocked",
                    "openspec",
                    reason=f"OpenSpec change was not listed: {selected}",
                    available_changes=names,
                    change_titles=titles,
                    openspec_version=version,
                )
            status = _json_command(executable, root, ["status", "--change", selected], timeout)
            missing = REQUIRED_STATUS_KEYS.difference(status)
            if missing:
                raise CompatibilityError(
                    "OpenSpec status response is missing required keys: " + ", ".join(sorted(missing))
                )
            if status.get("changeName") != selected:
                raise CompatibilityError("OpenSpec status returned a different change name")
            return _result(
                "openspec",
                "ready" if status.get("isComplete") else "incomplete",
                "openspec",
                selected,
                openspec_version=version,
                planning_complete=bool(status.get("isPlanningComplete")),
                complete=bool(status.get("isComplete")),
                artifacts=status.get("artifacts", []),
            )
        except CompatibilityError as exc:
            return _result("blocked", "blocked", "openspec", reason=str(exc))

    try:
        legacy = _legacy_task(root)
    except (CompatibilityError, OSError, UnicodeError) as exc:
        return _result("blocked", "blocked", "workflow", reason=str(exc))
    if legacy is not None:
        return _result("legacy-workflow", "recoverable", str(legacy), reason="Legacy workflow records are read-only until explicitly migrated.")
    if (root / ".trellis" / "tasks").is_dir():
        return _result("legacy-trellis", "read-only", str(root / ".trellis"), reason="Trellis records are historical and read-only.")
    return _result("unconfigured", "unconfigured", "none", reason="No OpenSpec, .workflow, or .trellis record system was found.")


def _iter_source_files(source: Path) -> Iterable[Path]:
    return sorted(path for path in source.rglob("*") if path.is_file())


def _source_hash(source: Path) -> str:
    digest = hashlib.sha256()
    for path in _iter_source_files(source):
        relative = path.relative_to(source).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _read_optional(source: Path, name: str) -> str:
    path = source / name
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _migrated_tasks(implement: str) -> str:
    tasks = [line for line in implement.splitlines() if re.match(r"^\s*- \[[ xX]\]", line)]
    if not tasks:
        return "- [ ] 1.1 Review the migrated task and verify its acceptance criteria before implementation."
    return "\n".join(tasks)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def migrate_workflow_task(
    project: os.PathLike[str] | str,
    source_task: os.PathLike[str] | str,
    change_id: str,
) -> Dict[str, Any]:
    """Copy one legacy task into a validated OpenSpec change, without source writes."""
    root = Path(project).expanduser().resolve()
    source = _safe_project_path(root, Path(source_task), "Legacy task")
    tasks_root = (root / ".workflow" / "tasks").resolve()
    changes_root = (root / "openspec" / "changes").resolve()
    if source.parent != tasks_root or not source.is_dir():
        raise MigrationError("Source must be one direct child of .workflow/tasks")
    if not CHANGE_ID_RE.fullmatch(change_id):
        raise MigrationError("Change id must contain lowercase letters, numbers, and hyphens only")
    if not _has_openspec_root(root):
        raise MigrationError("OpenSpec is not initialized; migration cannot create a canonical change")

    source_hash = _source_hash(source)
    target = _safe_project_path(root, changes_root / change_id, "Migration target")
    existing_report = target / "artifacts" / "migration-report.json"
    if target.exists():
        if existing_report.is_file():
            try:
                report = json.loads(existing_report.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise MigrationError(f"Existing migration report is unreadable: {target}") from exc
            if report.get("source_hash") == source_hash and report.get("result") == "success":
                return {"status": "already-migrated", "change": change_id, "source_hash": source_hash}
        raise MigrationError(f"Migration target already exists and does not match this source: {target}")

    prd = _read_optional(source, "prd.md")
    if not prd:
        raise MigrationError("Legacy task is missing required prd.md")
    design = _read_optional(source, "design.md") or "# Design\n\nReview the migrated requirements before implementation."
    implement = _read_optional(source, "implement.md")
    context = _read_optional(source, "context.md") or "# Context\n\nNo legacy context.md was present."
    outcome = _read_optional(source, "outcome.md") or "# Verification\n\nPending verification after migration."

    changes_root.mkdir(parents=True, exist_ok=True)
    temp_path = Path(tempfile.mkdtemp(prefix=f".{change_id}.", dir=str(changes_root)))
    try:
        _write_text(temp_path / ".openspec.yaml", "schema: spec-driven\n")
        _write_text(
            temp_path / "proposal.md",
            "# Proposal\n\n## Why\n\nThis change was migrated from a legacy workflow task.\n\n## Legacy Source\n\n" + prd,
        )
        _write_text(
            temp_path / "specs" / "workflow-compatibility" / "spec.md",
            "# Spec Delta\n\n## Purpose\n\nPreserves the observable acceptance intent of a migrated legacy workflow task while moving its canonical record to OpenSpec.\n\n## ADDED Requirements\n\n### Requirement: Preserve migrated acceptance intent\nThe system SHALL retain the legacy task requirements as reviewable OpenSpec change context before implementation continues.\n\n#### Scenario: Legacy task is migrated\n- **WHEN** the migration completes successfully\n- **THEN** the target change contains the source requirements and a migration report\n",
        )
        _write_text(temp_path / "design.md", design)
        _write_text(temp_path / "tasks.md", "# Tasks\n\n## 1. Migrated work\n\n" + _migrated_tasks(implement))
        _write_text(temp_path / "artifacts" / "context.md", context)
        _write_text(temp_path / "artifacts" / "verification.md", outcome)
        report = {
            "migration_version": MIGRATION_VERSION,
            "source": str(source),
            "source_hash": source_hash,
            "target": str(target),
            "change": change_id,
            "result": "success",
        }
        _write_text(temp_path / "artifacts" / "migration-report.json", json.dumps(report, indent=2))
        _write_text(
            temp_path / "artifacts" / "migration-report.md",
            "# Migration Report\n\n" + "\n".join(f"- **{key}**: `{value}`" for key, value in report.items()),
        )
        required = (
            temp_path / "proposal.md",
            temp_path / "specs" / "workflow-compatibility" / "spec.md",
            temp_path / "design.md",
            temp_path / "tasks.md",
            temp_path / "artifacts" / "context.md",
            temp_path / "artifacts" / "verification.md",
            temp_path / "artifacts" / "migration-report.json",
        )
        if not all(path.is_file() for path in required):
            raise MigrationError("Migration output is incomplete")
        temp_path.rename(target)
        return {"status": "migrated", "change": change_id, "source_hash": source_hash, "target": str(target)}
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise


def _safe_print(line: str) -> None:
    """Print a line, degrading a title the console cannot encode instead of crashing.

    Windows consoles often report ``gbk``; a Chinese title is then unprintable and a
    bare ``print`` raises UnicodeEncodeError. Losing the title is acceptable, losing
    the id is not, because the id is what every OpenSpec command takes.
    """
    try:
        print(line)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(line.encode(encoding, "replace").decode(encoding, "replace"))


def _main(argv: Sequence[str]) -> int:
    """Read-only `list` command so a human can find a change without the agent.

    `openspec list` prints English kebab-case ids only, and `openspec change list
    --long` prints `(unable to read)` for any proposal using Chinese section
    names. Reading the H1 directly avoids both problems.
    """
    parser = argparse.ArgumentParser(
        prog="openspec_compat.py",
        description="Read-only OpenSpec change discovery with readable titles.",
    )
    sub = parser.add_subparsers(dest="command")
    list_parser = sub.add_parser("list", help="list unarchived changes with their titles")
    list_parser.add_argument("--project", default=".", help="project root (default: current directory)")
    args = parser.parse_args(argv)
    if args.command != "list":
        parser.print_help()
        return 2
    root = Path(args.project).expanduser().resolve()
    result = list_changes(root)
    if result["status"] not in {"ready", "unselected"}:
        print(f"blocked: {result.get('reason') or 'unknown error'}", file=sys.stderr)
        return 1
    names = result.get("available_changes") or []
    titles = result.get("change_titles") or {}
    if not names:
        print("No unarchived changes.")
        return 0
    width = max(len(name) for name in names)
    for name in names:
        title = titles.get(name)
        # `_change_titles` falls back to the id, so only print a real title.
        if title and title != name:
            _safe_print(name.ljust(width) + "  " + title)
        else:
            _safe_print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
