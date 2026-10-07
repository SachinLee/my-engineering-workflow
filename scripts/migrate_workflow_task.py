#!/usr/bin/env python3
"""Migrate one legacy .workflow task into an OpenSpec change."""

from __future__ import annotations

import argparse
import json
import sys

from openspec_compat import CompatibilityError, migrate_workflow_task


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy one legacy .workflow task into an OpenSpec change without deleting the source."
    )
    parser.add_argument("--project-path", required=True, help="Project root containing openspec/ and .workflow/")
    parser.add_argument("--source-task", required=True, help="One direct child directory under .workflow/tasks/")
    parser.add_argument("--change-id", required=True, help="Lowercase OpenSpec change id, for example migrate-auth")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = migrate_workflow_task(args.project_path, args.source_task, args.change_id)
    except (CompatibilityError, OSError, UnicodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
