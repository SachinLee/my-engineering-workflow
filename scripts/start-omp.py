#!/usr/bin/env python3
"""Start OMP with the engineering workflow overlay."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


OVERLAY_NAME = "engineering-workflow.yml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start OMP or ompweb with the engineering workflow overlay.",
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Project directory used to find the overlay; terminal OMP also receives it as --cwd (default: current directory).",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start or reuse the single ompweb service instead of terminal OMP.",
    )
    parser.add_argument(
        "omp_arguments",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to OMP or ompweb. Prefix them with --.",
    )
    return parser


def normalize_forwarded(arguments: list[str]) -> list[str]:
    return arguments[1:] if arguments[:1] == ["--"] else arguments
def split_web_mode(web: bool, forwarded: list[str]) -> tuple[bool, list[str]]:
    forwarded = normalize_forwarded(forwarded)
    if forwarded[:1] == ["--web"]:
        return True, forwarded[1:]
    return web, forwarded
def find_executable(web: bool, which=shutil.which) -> str | None:
    return which("ompweb" if web else "omp")


def build_launch_command(
    *,
    web: bool,
    executable: str,
    project: Path,
    overlay: Path,
    forwarded: list[str],
) -> list[str]:
    forwarded = normalize_forwarded(forwarded)
    if web:
        return [executable, "--omp-config", str(overlay), *forwarded]
    return [executable, "--cwd", str(project), "--config", str(overlay), *forwarded]


def find_overlay(project: Path, script_dir: Path) -> Path:
    candidates = (
        project / ".omp" / OVERLAY_NAME,
        script_dir / OVERLAY_NAME,
        script_dir.parent / "config" / "omp-workflow.yml",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    checked = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"OMP workflow overlay was not found. Checked: {checked}")

def main() -> int:
    args = build_parser().parse_args()
    web, forwarded = split_web_mode(args.web, args.omp_arguments)
    project = Path(args.project_path).expanduser().resolve()
    if not project.is_dir():
        raise NotADirectoryError(f"Project directory was not found: {project}")

    script_dir = Path(__file__).resolve().parent
    overlay = find_overlay(project, script_dir)
    executable_name = "ompweb" if web else "omp"
    executable = find_executable(web)
    if not executable:
        raise FileNotFoundError(f"{executable_name} was not found on PATH.")

    command = build_launch_command(
        web=web,
        executable=executable,
        project=project,
        overlay=overlay,
        forwarded=forwarded,
    )
    completed = subprocess.run(command, cwd=project, check=False)
    return completed.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
