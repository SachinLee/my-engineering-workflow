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
        description="Start OMP with the engineering workflow overlay.",
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Project directory passed to OMP (default: current directory).",
    )
    parser.add_argument(
        "omp_arguments",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to OMP. Prefix them with --.",
    )
    return parser


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
    project = Path(args.project_path).expanduser().resolve()
    if not project.is_dir():
        raise NotADirectoryError(f"Project directory was not found: {project}")

    script_dir = Path(__file__).resolve().parent
    overlay = find_overlay(project, script_dir)
    omp = shutil.which("omp")
    if not omp:
        raise FileNotFoundError("omp was not found on PATH.")

    forwarded = args.omp_arguments
    if forwarded[:1] == ["--"]:
        forwarded = forwarded[1:]

    completed = subprocess.run(
        [omp, "--cwd", str(project), "--config", str(overlay), *forwarded],
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
