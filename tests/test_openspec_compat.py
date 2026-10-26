#!/usr/bin/env python3
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from openspec_compat import (
    TITLE_RULE_ANCHOR,
    CompatibilityError,
    create_change,
    detect_project_mode,
    ensure_proposal_title_rule,
    list_changes,
    migrate_workflow_task,
)  # noqa: E402
from unittest import mock  # noqa: E402

import openspec_compat  # noqa: E402


FAKE_CLI = r'''#!/usr/bin/env python3
import json
import os
import sys

mode = os.environ.get("FAKE_OPENSPEC_MODE", "single")
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("FAKE_OPENSPEC_VERSION", "1.14.1"))
    raise SystemExit(0)
if sys.argv[1:2] == ["list"]:
    if mode == "malformed":
        print("not-json")
        raise SystemExit(0)
    names = {"single": ["alpha"], "multiple": ["alpha", "beta"], "empty": []}.get(mode, ["alpha"])
    print(json.dumps({"changes": [{"name": name, "status": "in-progress"} for name in names], "root": {"path": os.getcwd()}}))
    raise SystemExit(0)
if sys.argv[1:2] == ["status"]:
    change = sys.argv[sys.argv.index("--change") + 1]
    print(json.dumps({
        "changeName": change,
        "artifacts": [],
        "isPlanningComplete": True,
        "isComplete": True,
    }))
    raise SystemExit(0)
if sys.argv[1:2] == ["show"]:
    print(json.dumps({"status": [{"message": "Change must have a Why section"}]}))
    raise SystemExit(1)
if sys.argv[1:3] == ["new", "change"]:
    if "--json" not in sys.argv:
        print(json.dumps({"status": [{"message": "fake CLI requires --json"}]}))
        raise SystemExit(1)
    name = sys.argv[3]
    if os.environ.get("FAKE_OPENSPEC_NEW") == "duplicate":
        print(json.dumps({"status": [{"message": f"Change '{name}' already exists at change"}]}))
        raise SystemExit(1)
    with open(".new-change-args.json", "w", encoding="utf-8") as handle:
        json.dump(sys.argv[1:], handle)
    print(json.dumps({
        "change": {"id": name, "schema": "spec-driven"},
        "root": {"path": os.getcwd()},
    }))
    raise SystemExit(0)
print(json.dumps({"status": [{"message": "unsupported fake command"}]}))
raise SystemExit(1)
'''


class OpenSpecCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fake = self.root / "fake-openspec.py"
        self.fake.write_text(FAKE_CLI, encoding="utf-8")
        self.fake_command = [sys.executable, str(self.fake)]
        self.old_mode = os.environ.get("FAKE_OPENSPEC_MODE")
        self.old_version = os.environ.get("FAKE_OPENSPEC_VERSION")
        self.old_new = os.environ.get("FAKE_OPENSPEC_NEW")

    def tearDown(self):
        for key, value in (
            ("FAKE_OPENSPEC_MODE", self.old_mode),
            ("FAKE_OPENSPEC_VERSION", self.old_version),
            ("FAKE_OPENSPEC_NEW", self.old_new),
        ):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp.cleanup()

    def enable_openspec(self):
        (self.root / "openspec").mkdir()
        (self.root / "openspec" / "config.yaml").write_text("schema: spec-driven\n", encoding="utf-8")

    def test_create_change_adds_the_title_rule(self):
        self.enable_openspec()
        result = create_change(self.root, "gamma", description="d", goal="g", openspec_executable=self.fake_command)
        self.assertEqual(result["title_rule"]["status"], "updated")
        text = (self.root / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn(TITLE_RULE_ANCHOR, text)

        self.assertIn("rules:", text)
        self.assertIn("  proposal:", text)

    def test_ensure_title_rule_is_idempotent(self):
        self.enable_openspec()
        first = ensure_proposal_title_rule(self.root)
        self.assertEqual(first["status"], "updated")
        after_first = (self.root / "openspec" / "config.yaml").read_text(encoding="utf-8")
        second = ensure_proposal_title_rule(self.root)
        self.assertEqual(second["status"], "unchanged")
        self.assertEqual((self.root / "openspec" / "config.yaml").read_text(encoding="utf-8"), after_first)

    def test_ensure_title_rule_preserves_comments_and_user_rules(self):
        (self.root / "openspec").mkdir()
        config = self.root / "openspec" / "config.yaml"
        config.write_text(
            "schema: spec-driven\n\n"
            "context: |\n  Language: Chinese\n\n"
            "# Per-artifact rules (optional)\n"
            "# Example:\n"
            "#   rules:\n"
            "#     proposal:\n"
            "#       - Keep proposals under 500 words\n\n"
            "rules:\n"
            "  proposal:\n"
            "    - Keep proposals under 500 words\n",
            encoding="utf-8",
        )
        ensure_proposal_title_rule(self.root)
        text = config.read_text(encoding="utf-8")
        # User content and the template's commented example both survive.
        self.assertIn("#   rules:", text)
        self.assertIn("    - Keep proposals under 500 words", text)
        self.assertIn(TITLE_RULE_ANCHOR, text)

        # The rule joins the existing proposal list, it does not replace it.
        self.assertLess(text.index("Keep proposals under 500 words"), text.index(TITLE_RULE_ANCHOR))

    def test_ensure_title_rule_inserts_after_commented_example_when_no_rules_block(self):
        (self.root / "openspec").mkdir()
        config = self.root / "openspec" / "config.yaml"
        config.write_text(
            "schema: spec-driven\n\n"
            "context: |\n  Language: Chinese\n\n"
            "# Per-artifact rules (optional)\n"
            "# Example:\n"
            "#   rules:\n"
            "#     proposal:\n"
            "#       - Keep proposals under 500 words\n",
            encoding="utf-8",
        )
        ensure_proposal_title_rule(self.root)
        text = config.read_text(encoding="utf-8")
        self.assertIn("#   rules:", text)
        self.assertIn("\nrules:\n  proposal:\n", text)
        self.assertIn(TITLE_RULE_ANCHOR, text)


    def test_ensure_title_rule_reports_missing_config(self):
        self.root.mkdir(exist_ok=True)
        result = ensure_proposal_title_rule(self.root)
        self.assertEqual(result["status"], "skipped")

    def test_ensure_title_rule_handles_crlf(self):
        (self.root / "openspec").mkdir()
        config = self.root / "openspec" / "config.yaml"
        config.write_text("schema: spec-driven\r\n", encoding="utf-8", newline="")
        ensure_proposal_title_rule(self.root)
        text = config.read_bytes().decode("utf-8")
        self.assertIn("\r\n", text)
        # Every newline stays CRLF; no bare LF is introduced.
        self.assertNotIn("\n", text.replace("\r\n", ""))
        self.assertIn(TITLE_RULE_ANCHOR, text)

    def test_single_open_spec_change_is_not_auto_selected(self):
        self.enable_openspec()
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["mode"], "openspec")
        self.assertIsNone(result["change"])
        self.assertEqual(result["status"], "unselected")
        self.assertEqual(result["available_changes"], ["alpha"])

    def test_multiple_open_spec_changes_wait_for_user_decision(self):
        self.enable_openspec()
        os.environ["FAKE_OPENSPEC_MODE"] = "multiple"
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "unselected")
        self.assertIsNone(result["change"])
        self.assertEqual(result["available_changes"], ["alpha", "beta"])

    def write_proposal(self, name, body):
        change = self.root / "openspec" / "changes" / name
        change.mkdir(parents=True)
        (change / "proposal.md").write_text(body, encoding="utf-8")

    def test_unselected_routing_carries_readable_titles(self):
        self.enable_openspec()
        os.environ["FAKE_OPENSPEC_MODE"] = "multiple"
        self.write_proposal("alpha", "# 提案：阿尔法\n\n## Why\n\n理由。\n\n## What Changes\n\n- 改动\n")
        self.write_proposal("beta", "# Change: 提案：贝塔\n\n## Why\n\n理由。\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "unselected")
        self.assertEqual(result["available_changes"], ["alpha", "beta"])
        self.assertEqual(result["change_titles"], {"alpha": "提案：阿尔法", "beta": "提案：贝塔"})
    def test_non_heading_hash_lines_are_not_titles(self):
        self.enable_openspec()
        self.write_proposal("alpha", "前言文字\n  # 缩进注释\n#hashtag\n\n# 提案：真的标题\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["change_titles"], {"alpha": "提案：真的标题"})

    def test_fenced_code_hash_lines_are_not_titles(self):
        self.enable_openspec()
        self.write_proposal("alpha", "```bash\n# not a title\n```\n\n# 提案：围栏外的标题\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["change_titles"], {"alpha": "提案：围栏外的标题"})

    def test_placeholder_title_falls_back_to_change_id(self):
        self.enable_openspec()
        self.write_proposal("alpha", "# Proposal\n\n## Why\n\n理由。\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "unselected")
        self.assertEqual(result["change_titles"], {"alpha": "alpha"})

    def test_missing_proposal_falls_back_to_change_id(self):
        self.enable_openspec()
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "unselected")
        self.assertEqual(result["change_titles"], {"alpha": "alpha"})

    def test_show_failure_never_blocks_routing(self):
        # `openspec show` rejects proposals with Chinese section names; titles
        # must come from the H1 on disk, not from that failing command.
        self.enable_openspec()
        self.write_proposal("alpha", "# 提案：阿尔法\n\n## 目标\n\n理由。\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "unselected")
        self.assertIsNone(result["reason"])
        self.assertEqual(result["change_titles"], {"alpha": "提案：阿尔法"})

    def test_bare_heading_without_text_falls_back_to_change_id(self):
        self.enable_openspec()
        self.write_proposal("alpha", "#   \n\n## Why\n\n理由。\n")
        result = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["change_titles"], {"alpha": "alpha"})

    def test_explicit_change_keeps_available_changes_unchanged(self):
        self.enable_openspec()
        result = detect_project_mode(self.root, change="alpha", openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "ready")
        self.assertNotIn("change_titles", result)

    def test_explicit_change_reads_status(self):
        self.enable_openspec()
        result = detect_project_mode(self.root, change="alpha", openspec_executable=self.fake_command)
        self.assertEqual(result["mode"], "openspec")
        self.assertEqual(result["change"], "alpha")
        self.assertEqual(result["status"], "ready")

    def test_blocks_unknown_explicit_change(self):
        self.enable_openspec()
        result = detect_project_mode(self.root, change="missing", openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("not listed", result["reason"])
    def test_blocks_missing_or_malformed_open_spec(self):
        self.enable_openspec()
        missing = detect_project_mode(self.root, openspec_executable=[str(self.root / "missing")])
        self.assertEqual(missing["status"], "blocked")
        os.environ["FAKE_OPENSPEC_MODE"] = "malformed"
        malformed = detect_project_mode(self.root, openspec_executable=self.fake_command)
        self.assertEqual(malformed["status"], "blocked")

    def test_reads_legacy_workflow_without_mutation(self):
        task = self.root / ".workflow" / "tasks" / "legacy"
        task.mkdir(parents=True)
        (self.root / ".workflow" / "CURRENT.md").write_text("task: .workflow/tasks/legacy\n", encoding="utf-8")
        (task / "prd.md").write_text("# Legacy\n", encoding="utf-8")
        result = detect_project_mode(self.root)
        self.assertEqual(result["mode"], "legacy-workflow")
        self.assertEqual(Path(result["source"]), task)

    def test_reads_trellis_as_read_only_fallback(self):
        (self.root / ".trellis" / "tasks" / "legacy").mkdir(parents=True)
        result = detect_project_mode(self.root)
        self.assertEqual(result["mode"], "legacy-trellis")
        self.assertEqual(result["status"], "read-only")

    def test_reports_unconfigured_project(self):
        result = detect_project_mode(self.root)
        self.assertEqual(result["mode"], "unconfigured")

    def test_lists_changes_without_mutation(self):
        self.enable_openspec()
        result = list_changes(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["available_changes"], ["alpha"])
        self.assertEqual(result["openspec_version"], "1.14.1")
        self.assertFalse((self.root / ".new-change-args.json").exists())

    def test_lists_changes_reports_blocked_environments(self):
        self.enable_openspec()
        os.environ["FAKE_OPENSPEC_MODE"] = "malformed"
        result = list_changes(self.root, openspec_executable=self.fake_command)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("invalid JSON", result["reason"])

    def test_create_change_runs_explicit_cli_command(self):
        self.enable_openspec()
        result = create_change(
            self.root,
            "intent-routing",
            description="按会话意图匹配",
            goal="确认后创建",
            openspec_executable=self.fake_command,
        )
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["change"], "intent-routing")
        args = json.loads((self.root / ".new-change-args.json").read_text(encoding="utf-8"))
        self.assertEqual(args[0:3], ["new", "change", "intent-routing"])
        self.assertIn("--description", args)
        self.assertIn("按会话意图匹配", args)
        self.assertIn("--goal", args)
        self.assertIn("--schema", args)
        self.assertIn("spec-driven", args)
        self.assertIn("--json", args)

    def test_create_change_never_overwrites_existing_name(self):
        self.enable_openspec()
        os.environ["FAKE_OPENSPEC_NEW"] = "duplicate"
        with self.assertRaises(CompatibilityError) as ctx:
            create_change(self.root, "alpha", description="x", goal="y", openspec_executable=self.fake_command)
        self.assertIn("already exists", str(ctx.exception))
        self.assertFalse((self.root / ".new-change-args.json").exists())

    def test_create_change_rejects_invalid_id_before_cli(self):
        self.enable_openspec()
        with self.assertRaises(CompatibilityError) as ctx:
            create_change(self.root, "Bad_Id", description="x", goal="y", openspec_executable=self.fake_command)
        self.assertIn("lowercase letters, numbers, and hyphens", str(ctx.exception))
        self.assertFalse((self.root / ".new-change-args.json").exists())

    def test_create_change_requires_openspec_root(self):
        with self.assertRaises(CompatibilityError):
            create_change(self.root, "no-root", description="x", goal="y", openspec_executable=self.fake_command)
        self.assertFalse((self.root / ".new-change-args.json").exists())

    def test_migration_is_idempotent_and_preserves_source(self):
        self.enable_openspec()
        source = self.root / ".workflow" / "tasks" / "legacy"
        source.mkdir(parents=True)
        (source / "prd.md").write_text("# Legacy requirements\n", encoding="utf-8")
        (source / "design.md").write_text("# Legacy design\n", encoding="utf-8")
        (source / "implement.md").write_text("- [ ] 1.1 Implement it\n", encoding="utf-8")
        before = self.source_snapshot(source)

        first = migrate_workflow_task(self.root, source, "legacy-migration")
        self.assertEqual(first["status"], "migrated")
        target = self.root / "openspec" / "changes" / "legacy-migration"
        self.assertTrue((target / "artifacts" / "migration-report.json").is_file())
        self.assertEqual(before, self.source_snapshot(source))

        second = migrate_workflow_task(self.root, source, "legacy-migration")
        self.assertEqual(second["status"], "already-migrated")
        self.assertEqual(before, self.source_snapshot(source))

    def test_failed_migration_keeps_source_and_writes_no_target(self):
        self.enable_openspec()
        source = self.root / ".workflow" / "tasks" / "broken"
        source.mkdir(parents=True)
        (source / "design.md").write_text("# no prd\n", encoding="utf-8")
        before = self.source_snapshot(source)
        with self.assertRaises(Exception):
            migrate_workflow_task(self.root, source, "broken-migration")
        self.assertEqual(before, self.source_snapshot(source))
        self.assertFalse((self.root / "openspec" / "changes" / "broken-migration").exists())

    def test_list_command_prints_id_and_readable_title(self):
        with mock.patch.object(openspec_compat, "list_changes") as stub:
            stub.return_value = {
                "status": "ready",
                "available_changes": ["alpha", "beta"],
                "change_titles": {"alpha": "提案：甲", "beta": "beta"},
            }
            code, output = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("alpha", output)
        self.assertIn("提案：甲", output)
        self.assertNotIn("beta  beta", output)

    def test_list_command_skips_duplicate_and_missing_titles(self):
        with mock.patch.object(openspec_compat, "list_changes") as stub:
            stub.return_value = {
                "status": "ready",
                "available_changes": ["alpha"],
                "change_titles": {"alpha": "alpha"},
            }
            code, output = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "alpha")

    def test_list_command_reports_blocked_projects(self):
        with mock.patch.object(openspec_compat, "list_changes") as stub:
            stub.return_value = {"status": "blocked", "reason": "invalid JSON"}
            code, output = self.run_cli(["list"])
        self.assertEqual(code, 1)
        self.assertIn("invalid JSON", output)

    def test_no_subcommand_prints_help(self):
        code, output = self.run_cli([])
        self.assertEqual(code, 2)
        self.assertIn("usage:", output)

    @staticmethod
    def run_cli(argv):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = openspec_compat._main(argv)
        return code, out.getvalue() + err.getvalue()

    @staticmethod
    def source_snapshot(source):
        digest = hashlib.sha256()
        for path in sorted(source.rglob("*")):
            if path.is_file():
                digest.update(path.relative_to(source).as_posix().encode("utf-8"))
                digest.update(path.read_bytes())
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
