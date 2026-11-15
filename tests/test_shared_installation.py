"""Exercise the public installer/doctor against disposable user and project roots."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import doctor  # noqa: E402

PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell 7 (pwsh) is required for installation tests")
class SharedInstallationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = tempfile.TemporaryDirectory(prefix="workflow source ")
        base = Path(cls.sources.name)
        cls.repo = base / "workflow"
        names = ["skills", "agents", ".omp/agents", ".pi/agents", ".opencode/agents", "commands", "config", "scripts"]
        # .codex/agents ships with this change; copy it only once it exists so the
        # RED run fails on assertions instead of dying in setUpClass.
        if (REPO / ".codex/agents").is_dir():
            names.append(".codex/agents")
        for name in names:
            shutil.copytree(REPO / name, cls.repo / name, ignore=shutil.ignore_patterns("__pycache__"))
        # The external gate is owned by another repo. Its content is not this seam.
        gate = base / "omp-extensions" / "workflow-review-gate"
        actual_gate = REPO.parent / "omp-extensions/workflow-review-gate"
        if actual_gate.is_dir():
            shutil.copytree(actual_gate, gate, ignore=shutil.ignore_patterns("node_modules", ".git"))
        else:
            gate.mkdir(parents=True)
            (gate / "index.ts").write_text('// installation fixture\n', encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.sources.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow install ")
        self.base = Path(self.temp.name)
        self.home = self.base / "user home"
        self.project = self.base / "project with spaces"
        self.home.mkdir()
        self.project.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home))
        self.env.pop("PI_CODING_AGENT_DIR", None)
        self.env.pop("OPENCODE_CONFIG_DIR", None)
        self.shared = self.home / ".agents" / "skills"

    def tearDown(self):
        self.temp.cleanup()

    def install(self, *args, success=True):
        result = subprocess.run(
            [PWSH, "-NoLogo", "-NoProfile", "-File", str(self.repo / "scripts/install.ps1"), *args],
            env=self.env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_shared(self):
        for name in doctor.SKILLS:
            self.assertEqual(
                (self.shared / name / "SKILL.md").read_bytes(),
                (self.repo / "skills" / name / "SKILL.md").read_bytes(),
            )
        self.assertEqual(
            (self.shared / "run-engineering-workflow/scripts/openspec_compat.py").read_bytes(),
            (self.repo / "scripts/openspec_compat.py").read_bytes(),
        )

    def test_all_installs_one_shared_copy_with_adapters_and_is_idempotent(self):
        foreign = self.home / ".claude/skills/unrelated/SKILL.md"
        foreign.parent.mkdir(parents=True)
        foreign.write_text("unrelated", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "All")
        self.assert_shared()
        for root in (".codex/skills", ".omp/agent/skills"):
            for name in doctor.SKILLS:
                self.assertFalse((self.home / root / name).exists())
        for root in (".claude/skills", ".pi/agent/skills"):
            for name in doctor.SKILLS:
                entry = self.home / root / name
                self.assertTrue(entry.is_dir(), entry)
                self.assertEqual(entry.resolve(), (self.shared / name).resolve(), entry)
        for name in doctor.AGENTS:
            self.assertTrue((self.home / ".codex/agents" / f"{name}.toml").is_file())
        for root in (".claude", ".omp/agent", ".pi/agent"):
            for name in doctor.AGENTS:
                self.assertTrue((self.home / root / "agents" / f"{name}.md").is_file())
        self.assertTrue((self.home / ".omp/agent/extensions/workflow-review-gate/index.ts").is_file())
        self.assertTrue((self.home / ".omp/agent/start-engineering-workflow.py").is_file())
        self.assertTrue((self.home / ".claude/commands/archive-task.md").is_file())
        self.assertEqual(foreign.read_text(encoding="utf-8"), "unrelated")
        before = {p.relative_to(self.home): p.lstat().st_mtime_ns for p in self.home.rglob("SKILL.md")}
        self.install("-Scope", "User", "-Harness", "All")
        self.assertEqual(before, {p.relative_to(self.home): p.lstat().st_mtime_ns for p in self.home.rglob("SKILL.md")})
        self.assertFalse((self.home / ".agents/backups/my-engineering-workflow").exists())

    def diagnose(self, harness="All", scope="User"):
        args = type("Args", (), dict(scope=scope, harness=harness, project_path=str(self.project)))()
        output = StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True), mock.patch.object(Path, "home", return_value=self.home), \
             mock.patch.object(doctor, "parse_args", return_value=args), \
             mock.patch.object(doctor, "executable_exists"), mock.patch.object(doctor, "check_review_gate"), \
             mock.patch.object(doctor, "repo_source_root", return_value=self.repo), \
             redirect_stdout(output), redirect_stderr(output):
            code = doctor.main()
        return code, output.getvalue()

    @unittest.skipUnless((REPO.parent / "omp-extensions/workflow-review-gate").is_dir() and shutil.which("node"),
                         "real OMP gate and node are required for the doctor CLI integration")
    def test_doctor_cli_with_real_gate_and_isolated_home(self):
        self.install("-Scope", "Project", "-Harness", "All", "-ProjectPath", str(self.project))
        # Stub discovery only; doctor does not launch these harnesses.
        bins = self.base / "bin"
        bins.mkdir()
        for name in ("omp", "pi", "claude", "opencode"):
            path = bins / (name + ".cmd" if os.name == "nt" else name)
            path.write_text("@exit /b 0\n" if os.name == "nt" else "#!/bin/sh\nexit 0\n", encoding="utf-8")
            path.chmod(0o755)
        env = dict(self.env, PATH=str(bins) + os.pathsep + self.env["PATH"])
        result = subprocess.run([sys.executable, str(self.repo / "scripts/doctor.py"), "--scope", "Project",
                                 "--harness", "All", "--project-path", str(self.project)],
                                env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Workflow installation is healthy.", result.stdout)

    def test_override_to_shared_parent_does_not_report_shared_skills_as_legacy(self):
        self.env["PI_CODING_AGENT_DIR"] = str(self.home / ".agents")
        self.install("-Scope", "User", "-Harness", "Pi")
        self.assert_shared()
        code, output = self.diagnose("Pi")
        self.assertEqual(code, 0, output)
        self.assertNotIn("Legacy skill entry", output)

    def test_home_as_project_does_not_report_shared_skills_as_legacy(self):
        self.project = self.home
        self.install("-Scope", "Project", "-Harness", "Codex", "-ProjectPath", str(self.project))
        self.assert_shared()
        code, output = self.diagnose("Codex", "Project")
        self.assertEqual(code, 0, output)
        self.assertNotIn("Legacy skill entry", output)

    def test_unix_link_comparison_preserves_case(self):
        target = self.shared / "plan-solution"
        target.mkdir(parents=True)
        entry = self.home / ".claude/skills/plan-solution"
        self.directory_link(entry, self.shared / "PLAN-SOLUTION")
        # Exercise the actual Unix comparison branch on Windows too. Filesystem
        # semantics are covered by the separate Unix-only integration test.
        source = (self.repo / "scripts/install.ps1").read_text(encoding="utf-8")
        function = source[source.index("function Test-SharedLink {"):source.index("$backupRoot =")]
        script = self.base / "check link.ps1"
        quote = lambda path: "'" + str(path).replace("'", "''") + "'"
        script.write_text(function + "\n$env:OS = 'Unix'\nif (Test-SharedLink -Path " + quote(entry)
                          + " -Target " + quote(target) + ") { exit 1 }\nexit 0\n", encoding="utf-8")
        result = subprocess.run([PWSH, "-NoProfile", "-File", str(script)], env=self.env,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipIf(os.name == "nt", "requires a case-sensitive Unix filesystem")
    def test_case_different_unknown_links_are_rejected_even_when_broken(self):
        wrong = self.shared / "PLAN-SOLUTION"
        wrong.mkdir(parents=True)
        if (self.shared / "plan-solution").exists():
            self.skipTest("filesystem is case insensitive")
        marker = wrong / "custom.txt"
        marker.write_text("untouched", encoding="utf-8")
        entry = self.home / ".claude/skills/plan-solution"
        self.directory_link(entry, wrong)
        self.install("-Scope", "User", "-Harness", "Claude", success=False)
        self.assertEqual(entry.readlink(), wrong)
        self.assertEqual(marker.read_text(encoding="utf-8"), "untouched")
        self.assertFalse((self.shared / "run-engineering-workflow").exists())
        marker.unlink()
        wrong.rmdir()
        self.install("-Scope", "User", "-Harness", "Claude", success=False)
        self.assertEqual(entry.readlink(), wrong)
        self.assertFalse((self.shared / "run-engineering-workflow").exists())

    def test_doctor_recognizes_windows_junction_without_new_pathlib_api(self):
        entry = mock.Mock(spec=["lstat"])
        entry.lstat.return_value = type("Stat", (), {"st_mode": 0o40755, "st_file_attributes": 0x400})()
        self.assertTrue(doctor.is_directory_link(entry))
        entry.lstat.side_effect = FileNotFoundError
        self.assertFalse(doctor.is_directory_link(entry))

    def test_doctor_accepts_shared_all_and_rejects_shadow_copy_and_missing_helper(self):
        self.install("-Scope", "User", "-Harness", "All")
        code, output = self.diagnose()
        self.assertEqual(code, 0, output)
        old = self.legacy(self.home / ".codex/skills")
        code, output = self.diagnose()
        self.assertEqual(code, 1, output)
        self.assertIn("Legacy skill entry", output)
        shutil.rmtree(old)
        (self.shared / "run-engineering-workflow/scripts/openspec_compat.py").unlink()
        code, output = self.diagnose()
        self.assertEqual(code, 1, output)
        self.assertIn("shared OpenSpec helper", output)

    def test_doctor_rejects_claude_copy_wrong_link_and_broken_link(self):
        self.install("-Scope", "User", "-Harness", "Claude")
        entry = self.home / ".claude/skills/plan-solution"
        entry.rmdir() if os.name == "nt" else entry.unlink()
        self.legacy(entry.parent, entry.name)
        code, output = self.diagnose("Claude")
        self.assertEqual(code, 1, output)
        self.assertIn("Claude skill link", output)
        shutil.rmtree(entry)
        wrong = self.base / "wrong target"
        wrong.mkdir()
        self.directory_link(entry, wrong)
        code, output = self.diagnose("Claude")
        self.assertEqual(code, 1, output)
        self.assertIn("Claude skill link", output)
        wrong.rmdir()
        code, output = self.diagnose("Claude")
        self.assertEqual(code, 1, output)
        self.assertIn("Claude skill link", output)

    def legacy(self, root, name="run-engineering-workflow"):
        path = root / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text("local edit", encoding="utf-8")
        (path / "custom.txt").write_text(str(path), encoding="utf-8")
        return path

    def directory_link(self, path, target):
        path.parent.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(path), str(target)],
                           capture_output=True, check=True, timeout=10)
        else:
            path.symlink_to(target, target_is_directory=True)

    def test_project_migrates_old_user_and_project_copies_with_local_edits(self):
        roots = [self.home / root for root in (".codex/skills", ".omp/agent/skills", ".pi/agent/skills", ".claude/skills")]
        roots += [self.project / root for root in (".agents/skills", ".omp/skills", ".pi/skills", ".claude/skills")]
        originals = [self.legacy(root) for root in roots]
        result = self.install("-Scope", "Project", "-Harness", "All", "-ProjectPath", str(self.project))
        self.assert_shared()
        backup_root = self.home / ".agents/backups/my-engineering-workflow"
        saved = sorted(p.read_text(encoding="utf-8") for p in backup_root.rglob("custom.txt"))
        self.assertEqual(saved, sorted(map(str, originals)))
        self.assertIn("Backup:", result.stdout)
        for old in originals:
            if ".claude" in old.parts or ".pi" in old.parts:
                self.assertEqual(old.resolve(), (self.shared / old.name).resolve())
            else:
                self.assertFalse(old.exists())
        self.assertTrue((self.project / ".omp/agents/workflow-planner.md").is_file())
        self.assertTrue((self.project / ".pi/agents/workflow-planner.md").is_file())
        self.assertTrue((self.project / ".claude/agents/workflow-planner.md").is_file())
        self.install("-Scope", "Project", "-Harness", "All", "-ProjectPath", str(self.project))
        self.assertEqual(saved, sorted(p.read_text(encoding="utf-8") for p in backup_root.rglob("custom.txt")))

    def test_shared_local_edits_are_backed_up_on_update(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        modified = self.shared / "plan-solution/SKILL.md"
        modified.write_text("shared local edit", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "Codex")
        self.assert_shared()
        backups = self.home / ".agents/backups/my-engineering-workflow"
        self.assertEqual([p.read_text(encoding="utf-8") for p in backups.rglob("SKILL.md")], ["shared local edit"])

    def test_whatif_has_no_writes_on_new_or_legacy_installation(self):
        # PowerShell itself creates its AppData startup cache even for `exit 0`.
        subprocess.run([PWSH, "-NoProfile", "-Command", "exit 0"], env=self.env,
                       capture_output=True, check=True, timeout=10)
        baseline = sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*"))
        self.install("-Scope", "User", "-Harness", "All", "-WhatIf")
        self.assertEqual(sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*")), baseline)
        old = self.legacy(self.home / ".codex/skills")
        before = sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*"))
        self.install("-Scope", "Project", "-Harness", "All", "-ProjectPath", str(self.project), "-WhatIf")
        self.assertEqual(before, sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*")))
        self.assertEqual((old / "SKILL.md").read_text(encoding="utf-8"), "local edit")
        self.assertEqual(list(self.project.iterdir()), [])

    def test_unknown_links_and_link_parents_fail_before_skill_migration(self):
        outside = self.base / "outside"
        outside.mkdir()
        sentinel = outside / "SKILL.md"
        sentinel.write_text("untouched", encoding="utf-8")
        old = self.home / ".codex/skills/plan-solution"
        self.directory_link(old, outside)
        result = self.install("-Scope", "User", "-Harness", "Codex", success=False)
        self.assertIn("symlink or junction", result.stdout + result.stderr)
        self.assertFalse(self.shared.exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "untouched")
        old.rmdir() if os.name == "nt" else old.unlink()
        shutil.rmtree(self.home / ".codex/skills")
        self.directory_link(self.home / ".codex/skills", outside)
        self.install("-Scope", "User", "-Harness", "Codex", success=False)
        self.assertFalse(self.shared.exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "untouched")

    def test_linked_adapter_parent_is_rejected_before_any_publication(self):
        outside = self.base / "outside agents"
        outside.mkdir()
        self.directory_link(self.home / ".pi/agent/agents", outside)
        self.install("-Scope", "User", "-Harness", "All", success=False)
        self.assertFalse(self.shared.exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_default_scope_is_user_and_both_preserves_codex_plus_omp(self):
        self.install()
        self.assert_shared()
        self.assertTrue((self.home / ".omp/agent/agents/workflow-planner.md").is_file())
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / ".pi").exists())
        self.assertFalse((self.home / ".config/opencode").exists())
        self.assertIn("Codex adapter installs 3 native workflow agent TOML files", self.install().stdout)

    def opencode_root(self):
        return self.home / ".config/opencode"

    def test_opencode_installs_agents_commands_and_migrates_stale_skills(self):
        stale = self.opencode_root() / "skills" / "plan-solution"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text("stale copy", encoding="utf-8")
        (stale / "custom.txt").write_text("keep me", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "OpenCode")
        self.assert_shared()
        for name in doctor.AGENTS:
            self.assertTrue((self.opencode_root() / "agents" / f"{name}.md").is_file())
        for name in ("engineering-workflow", "archive-task"):
            self.assertEqual(
                (self.opencode_root() / "commands" / f"{name}.md").read_bytes(),
                (self.repo / "commands" / f"{name}.md").read_bytes(),
            )
        self.assertFalse(stale.exists())
        backups = list((self.home / ".agents/backups/my-engineering-workflow").rglob("custom.txt"))
        self.assertEqual([p.read_text(encoding="utf-8") for p in backups], ["keep me"])
        # No OpenCode-owned skill copy remains; discovery uses ~/.agents/skills.
        for name in doctor.SKILLS:
            self.assertFalse((self.opencode_root() / "skills" / name).exists())
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / ".pi").exists())

    def test_opencode_install_is_idempotent_and_preserves_user_model_settings(self):
        self.install("-Scope", "User", "-Harness", "OpenCode")
        config = self.opencode_root() / "opencode.json"
        config.write_text('{"model": "user/owned"}\n', encoding="utf-8")
        agents = self.opencode_root() / "agents" / "workflow-planner.md"
        before = agents.read_bytes()
        self.install("-Scope", "User", "-Harness", "OpenCode")
        self.assertEqual(agents.read_bytes(), before)
        self.assertEqual(config.read_text(encoding="utf-8"), '{"model": "user/owned"}\n')
        self.assertFalse((self.home / ".agents/backups/my-engineering-workflow").exists())

    def test_local_opencode_agent_edit_is_backed_up_before_refresh(self):
        self.install("-Scope", "User", "-Harness", "OpenCode")
        agents = self.opencode_root() / "agents" / "workflow-reviewer.md"
        agents.write_text("local permission tweak", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "OpenCode")
        self.assertEqual(agents.read_bytes(), (self.repo / ".opencode/agents/workflow-reviewer.md").read_bytes())
        backups = list((self.home / ".agents/backups/my-engineering-workflow").rglob("*workflow-reviewer.md"))
        self.assertEqual([p.read_text(encoding="utf-8") for p in backups], ["local permission tweak"])

    def test_opencode_agent_templates_omit_model_and_deny_nested_dispatch(self):
        for name in doctor.AGENTS:
            text = (self.repo / ".opencode/agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertNotIn("model:", text, name)
            self.assertIn("task: deny", text, name)
            self.assertIn("mode: subagent", text, name)
        reviewer = (self.repo / ".opencode/agents/workflow-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("edit: deny", reviewer)
        self.assertIn("bash: deny", reviewer)

    def test_doctor_reports_missing_opencode_adapter_and_drift(self):
        self.install("-Scope", "User", "-Harness", "OpenCode")
        code, output = self.diagnose("OpenCode")
        self.assertEqual(code, 0, output)
        (self.opencode_root() / "commands" / "archive-task.md").unlink()
        (self.opencode_root() / "agents" / "workflow-planner.md").write_text("drifted", encoding="utf-8")
        code, output = self.diagnose("OpenCode")
        self.assertEqual(code, 1, output)
        self.assertIn("Missing OpenCode command: archive-task", output)
        self.assertIn("OpenCode agent file differs from the shipped template", output)

    def test_doctor_flags_pi_agent_model_and_leaves_overrides_untouched(self):
        self.install("-Scope", "User", "-Harness", "Pi")
        settings = self.home / ".pi/agent/settings.json"
        original = {
            "defaultModel": "magpie/auto/gpt-6.1-sol",
            "subagents": {"agentOverrides": {
                "workflow-planner": {"model": "magpie/auto/gpt-6.1-sol", "thinking": "xhigh"},
                "workflow-reviewer": {"model": "magpie/es-grok/grok-4.7"},
            }},
        }
        settings.write_text(json.dumps(original), encoding="utf-8")
        agent = self.home / ".pi/agent/agents/workflow-planner.md"
        agent.write_text(agent.read_text(encoding="utf-8").replace(
            "description:", "model: opus\ndescription:"), encoding="utf-8")
        code, output = self.diagnose("Pi")
        self.assertEqual(code, 0, output)
        self.assertIn("Pi agentOverrides are user-owned and left untouched", output)
        self.assertIn("workflow-planner, workflow-reviewer", output)
        self.assertIn("Pi agent declares its own model (opus)", output)
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8")), original)

    def test_doctor_warns_on_claude_alias_collapse_without_leaking_credentials(self):
        self.install("-Scope", "User", "-Harness", "Claude")
        settings = self.home / ".claude/settings.json"
        settings.write_text(json.dumps({
            "env": {
                "ANTHROPIC_DEFAULT_OPUS_MODEL": "es-claude/claude-sonnet-5-5",
                "ANTHROPIC_DEFAULT_SONNET_MODEL": "es-claude/claude-sonnet-5-5",
                "ANTHROPIC_AUTH_TOKEN": "super-secret-token",
            }
        }), encoding="utf-8")
        code, output = self.diagnose("Claude")
        self.assertEqual(code, 0, output)
        self.assertIn("Claude Opus and Sonnet aliases both resolve to es-claude/claude-sonnet-5-5", output)
        self.assertIn("leaves settings.json untouched", output)
        self.assertNotIn("super-secret-token", output)
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8"))["env"]["ANTHROPIC_DEFAULT_OPUS_MODEL"],
                         "es-claude/claude-sonnet-5-5")

    def test_codex_backs_up_only_trellis_signature_agents(self):
        codex_agents = self.home / ".codex/agents"
        codex_agents.mkdir(parents=True)
        trellis = codex_agents / "workflow-planner.md"
        trellis.write_text("---\nname: workflow-planner\n---\n\n# Planner\n\n"
                           "Read the active Trellis task at `.trellis/tasks/<id>/`.\n", encoding="utf-8")
        foreign = codex_agents / "workflow-reviewer.md"
        foreign.write_text("---\nname: workflow-reviewer\n---\n\nMy own reviewer.\n", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "Codex")
        self.assertFalse(trellis.exists())
        self.assertEqual(foreign.read_text(encoding="utf-8"), "---\nname: workflow-reviewer\n---\n\nMy own reviewer.\n")
        backups = list((self.home / ".agents/backups/my-engineering-workflow").rglob("*workflow-planner.md"))
        self.assertEqual(len(backups), 1)
        self.assertIn(".trellis/tasks/", backups[0].read_text(encoding="utf-8"))

    def test_doctor_reports_codex_capability_layers_and_stale_agents(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 0, output)
        self.assertIn("Codex native workflow agent TOMLs installed: 3/3", output)
        if doctor.tomllib is None:
            self.assertIn("Static TOML validation: UNVERIFIED", output)
            self.assertIn("Statically discoverable: unknown", output)
            self.assertNotIn("Statically discoverable: yes", output)
        else:
            self.assertIn("Statically discoverable: yes", output)
        self.assertIn("Runtime discovery, delegation, and independent review: UNVERIFIED", output)
        self.assertNotIn("do not establish native Codex runtime support", output)
        self.assertNotIn("run in the main Codex session", output)
        stale = self.home / ".codex/agents/workflow-reviewer.md"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("---\nname: workflow-reviewer\n---\nSee `.trellis/tasks/<id>/`.\n", encoding="utf-8")
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 0, output)
        self.assertIn("Stale Trellis-era Codex agent definition remains", output)

    def test_opencode_config_dir_override_targets_custom_root(self):
        override = self.base / "custom opencode"
        self.env["OPENCODE_CONFIG_DIR"] = str(override)
        stale = override / "skills" / "plan-solution"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text("stale", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "OpenCode")
        self.assert_shared()
        self.assertFalse(stale.exists())
        self.assertTrue((override / "agents" / "workflow-planner.md").is_file())
        self.assertTrue((override / "commands" / "engineering-workflow.md").is_file())
        self.assertFalse((self.home / ".config/opencode").exists())

    def test_agent_directory_override_only_moves_adapters_and_legacy_root(self):
        override = self.base / "custom agent directory"
        self.env["PI_CODING_AGENT_DIR"] = str(override)
        self.legacy(override / "skills")
        self.install("-Scope", "User", "-Harness", "All")
        self.assert_shared()
        entry = override / "skills" / "run-engineering-workflow"
        self.assertTrue(doctor.is_directory_link(entry), entry)
        self.assertEqual(entry.resolve(), (self.shared / "run-engineering-workflow").resolve())
        self.assertTrue((override / "agents/workflow-planner.md").is_file())
        self.assertTrue((override / "start-engineering-workflow.py").is_file())
        self.assertFalse((self.home / ".omp").exists())
        self.assertFalse((self.home / ".pi").exists())


    def test_project_standards_is_the_seventh_shared_skill(self):
        self.install("-Harness", "All")
        self.assertIn("project-standards", doctor.SKILLS)
        self.assert_shared()
        shared = self.shared / "project-standards"
        for reference in (
            "references/common.md",
            "references/java.md",
            "references/spring-mybatis-plus.md",
            "references/project-agents-template.md",
        ):
            self.assertTrue((shared / reference).is_file(), reference)
        self.assertEqual(
            (self.home / ".claude/skills/project-standards").resolve(), shared.resolve()
        )
        code, output = self.diagnose("All")
        self.assertEqual(code, 0, output)

    def test_doctor_reports_omp_and_claude_adapter_drift(self):
        self.install("-Harness", "All")
        omp_agent = self.home / ".omp/agent/agents/workflow-planner.md"
        omp_agent.write_text(omp_agent.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        claude_agent = self.home / ".claude/agents/workflow-reviewer.md"
        claude_agent.write_text(claude_agent.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        claude_command = self.home / ".claude/commands/engineering-workflow.md"
        claude_command.write_text(claude_command.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
        code, output = self.diagnose("All")
        self.assertEqual(code, 0, output)
        self.assertIn("OMP agent file differs from the shipped template", output)
        self.assertIn("Claude agent file differs from the shipped template", output)
        self.assertIn("Claude command file differs from the shipped template", output)

    def test_doctor_reports_project_agents_skills_as_legacy_for_opencode(self):
        migrated = self.legacy(self.project / ".agents/skills", "plan-solution")
        result = self.install(
            "-Scope", "Project", "-Harness", "OpenCode", "-ProjectPath", str(self.project)
        )
        self.assertFalse(migrated.exists())
        self.assertIn("Backup:", result.stdout)
        stale = self.project / ".agents/skills/plan-solution"
        stale.mkdir(parents=True)
        (stale / "SKILL.md").write_text(
            "---\nname: plan-solution\ndescription: stale copy\n---\nstale\n", encoding="utf-8"
        )
        code, output = self.diagnose("OpenCode", "Project")
        self.assertNotEqual(code, 0, output)
        self.assertIn(f"Legacy skill entry may shadow shared installation: {stale}", output)

    # --- Codex native TOML roles (AC-009) ---

    def codex_agents(self):
        return self.home / ".codex/agents"

    def test_codex_installs_model_free_native_toml_roles(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        for name in doctor.AGENTS:
            path = self.codex_agents() / f"{name}.toml"
            self.assertTrue(path.is_file(), path)
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, rf'(?m)^\s*name\s*=\s*"{name}"\s*$')
            self.assertRegex(text, r'(?m)^\s*developer_instructions\s*=\s*"""')
            for forbidden in ("model", "model_provider", "model_reasoning_effort", "sandbox_mode"):
                self.assertIsNone(
                    re.search(rf"(?m)^\s*{forbidden}\s*=", text), f"{path}: {forbidden}"
                )

    def test_codex_toml_sources_declare_required_contract_fields(self):
        source = REPO / ".codex/agents"
        self.assertTrue(source.is_dir())
        for name in doctor.AGENTS:
            text = (source / f"{name}.toml").read_text(encoding="utf-8")
            for key in ("name", "description", "developer_instructions"):
                self.assertRegex(text, rf"(?m)^\s*{key}\s*=")
            for forbidden in ("model", "model_provider", "model_reasoning_effort", "sandbox_mode"):
                self.assertIsNone(re.search(rf"(?m)^\s*{forbidden}\s*=", text), f"{name}: {forbidden}")

    def test_codex_toml_install_is_idempotent_and_backs_up_local_edits(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        planner = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(planner.is_file(), planner)
        before = planner.read_text(encoding="utf-8")
        planner.write_text(before + "\n# local edit\n", encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "Codex")
        self.assertEqual(planner.read_text(encoding="utf-8"), before)
        backups = list(
            (self.home / ".agents/backups/my-engineering-workflow").rglob("*workflow-planner.toml")
        )
        self.assertEqual(len(backups), 1)
        self.assertIn("# local edit", backups[0].read_text(encoding="utf-8"))
        self.install("-Scope", "User", "-Harness", "Codex")
        self.assertEqual(
            list((self.home / ".agents/backups/my-engineering-workflow").rglob("*workflow-planner.toml")),
            backups,
        )

    def test_codex_install_preserves_user_roles_and_config(self):
        codex = self.home / ".codex"
        codex.mkdir(parents=True)
        (codex / "config.toml").write_text('model_provider = "magpie"\n', encoding="utf-8")
        agents = codex / "agents"
        agents.mkdir()
        (agents / "fixer.toml").write_text('name = "fixer"\n', encoding="utf-8")
        self.install("-Scope", "User", "-Harness", "Codex")
        self.assertEqual((codex / "config.toml").read_text(encoding="utf-8"), 'model_provider = "magpie"\n')
        self.assertEqual((agents / "fixer.toml").read_text(encoding="utf-8"), 'name = "fixer"\n')
        self.assertEqual(
            sorted(p.name for p in agents.glob("*.toml")),
            ["fixer.toml", "workflow-implementer.toml", "workflow-planner.toml", "workflow-reviewer.toml"],
        )

    def test_codex_project_scope_installs_toml_into_project_root(self):
        self.install("-Scope", "Project", "-Harness", "Codex", "-ProjectPath", str(self.project))
        self.assert_shared()
        for name in doctor.AGENTS:
            self.assertTrue((self.project / ".codex/agents" / f"{name}.toml").is_file())
            self.assertFalse((self.home / ".codex/agents" / f"{name}.toml").exists())

    def test_codex_unknown_toml_link_is_rejected_before_publication(self):
        outside = self.base / "outside toml"
        outside.mkdir()
        self.directory_link(self.home / ".codex/agents/workflow-planner.toml", outside)
        self.install("-Scope", "User", "-Harness", "Codex", success=False)
        self.assertFalse(self.shared.exists())
        self.assertEqual(list(outside.iterdir()), [])

    # --- Pi native shared skill links (AC-010) ---

    def pi_skill_root(self):
        return self.home / ".pi/agent/skills"

    def test_pi_installs_native_shared_skill_links(self):
        self.install("-Scope", "User", "-Harness", "Pi")
        self.assert_shared()
        root = self.pi_skill_root()
        for name in doctor.SKILLS:
            entry = root / name
            self.assertTrue(doctor.is_directory_link(entry), entry)
            self.assertEqual(entry.resolve(), (self.shared / name).resolve(), entry)

    def test_pi_legacy_skill_copy_is_backed_up_before_link(self):
        self.legacy(self.pi_skill_root())
        result = self.install("-Scope", "User", "-Harness", "Pi")
        self.assertIn("Backup:", result.stdout)
        self.assertTrue(doctor.is_directory_link(self.pi_skill_root() / "run-engineering-workflow"))
        backups = list((self.home / ".agents/backups/my-engineering-workflow").rglob("custom.txt"))
        self.assertEqual(len(backups), 1)

    def test_pi_unknown_skill_link_is_rejected(self):
        outside = self.base / "outside skills"
        outside.mkdir()
        self.directory_link(self.pi_skill_root() / "plan-solution", outside)
        self.install("-Scope", "User", "-Harness", "Pi", success=False)
        self.assertFalse(self.shared.exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_pi_link_install_is_idempotent(self):
        self.install("-Scope", "User", "-Harness", "Pi")
        before = sorted((p.name, p.resolve()) for p in self.pi_skill_root().iterdir())
        self.install("-Scope", "User", "-Harness", "Pi")
        after = sorted((p.name, p.resolve()) for p in self.pi_skill_root().iterdir())
        self.assertEqual(before, after)

    def test_pi_project_scope_links_user_and_project_roots(self):
        self.install("-Scope", "Project", "-Harness", "Pi", "-ProjectPath", str(self.project))
        self.assert_shared()
        for root in (self.pi_skill_root(), self.project / ".pi/skills"):
            for name in doctor.SKILLS:
                entry = root / name
                self.assertTrue(doctor.is_directory_link(entry), entry)
                self.assertEqual(entry.resolve(), (self.shared / name).resolve(), entry)

    def test_both_preserves_codex_plus_omp_without_pi_links(self):
        self.install()
        self.assert_shared()
        self.assertFalse((self.home / ".pi").exists())

    # --- Doctor layering for Codex and Pi ---

    def test_doctor_errors_on_missing_codex_toml(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        path = self.codex_agents() / "workflow-implementer.toml"
        self.assertTrue(path.is_file(), path)
        path.unlink()
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn("Missing Codex native workflow agent", output)

    def test_doctor_errors_on_model_key_in_codex_toml(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        planner = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(planner.is_file(), planner)
        planner.write_text(
            planner.read_text(encoding="utf-8") + '\nmodel = "opus"\n', encoding="utf-8"
        )
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn("declares a model key", output)

    def test_doctor_warns_on_codex_toml_drift(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        planner = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(planner.is_file(), planner)
        planner.write_text(planner.read_text(encoding="utf-8") + "\n# local edit\n", encoding="utf-8")
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 0, output)
        self.assertIn("Codex agent file differs from the shipped template", output)

    @unittest.skipIf(doctor.tomllib is None, "TOML syntax/field validation requires Python 3.11+ tomllib")
    def test_doctor_rejects_empty_codex_toml(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        path = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(path.is_file(), path)
        path.write_text("", encoding="utf-8")
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn("Codex workflow agent is empty", output)
        # Presence and validity stay separate reports.
        self.assertIn("Codex native workflow agent TOMLs installed: 3/3", output)
        self.assertIn("Statically discoverable: no", output)
        self.assertNotIn("Statically discoverable: yes", output)

    @unittest.skipIf(doctor.tomllib is None, "TOML syntax/field validation requires Python 3.11+ tomllib")
    def test_doctor_rejects_invalid_codex_toml_syntax(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        path = self.codex_agents() / "workflow-implementer.toml"
        self.assertTrue(path.is_file(), path)
        path.write_text(
            'name = "workflow-implementer"\ndescription = "unterminated\n', encoding="utf-8"
        )
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn("is not valid TOML", output)
        self.assertIn("Statically discoverable: no", output)
        self.assertNotIn("Statically discoverable: yes", output)

    @unittest.skipIf(doctor.tomllib is None, "TOML syntax/field validation requires Python 3.11+ tomllib")
    def test_doctor_rejects_codex_toml_missing_required_field(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        path = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(path.is_file(), path)
        text = "\n".join(
            line for line in path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("description =")
        )
        path.write_text(text, encoding="utf-8")
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn("is missing a non-empty string field: description", output)
        self.assertIn("Statically discoverable: no", output)
        self.assertNotIn("Statically discoverable: yes", output)

    @unittest.skipIf(doctor.tomllib is None, "TOML syntax/field validation requires Python 3.11+ tomllib")
    def test_doctor_rejects_codex_toml_role_name_mismatch(self):
        self.install("-Scope", "User", "-Harness", "Codex")
        path = self.codex_agents() / "workflow-reviewer.toml"
        self.assertTrue(path.is_file(), path)
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                'name = "workflow-reviewer"', 'name = "workflow-planner"'
            ),
            encoding="utf-8",
        )
        code, output = self.diagnose("Codex")
        self.assertEqual(code, 1, output)
        self.assertIn(
            "declares name 'workflow-planner', expected 'workflow-reviewer'", output
        )
        self.assertIn("Statically discoverable: no", output)
        self.assertNotIn("Statically discoverable: yes", output)

    def test_doctor_never_claims_static_yes_without_tomllib(self):
        # No parser means no syntax/field/name verdict, even for a file whose
        # bare `description = 42` would pass a naive line scanner.
        self.install("-Scope", "User", "-Harness", "Codex")
        planner = self.codex_agents() / "workflow-planner.toml"
        self.assertTrue(planner.is_file(), planner)
        planner.write_text(
            'name = "workflow-planner"\ndescription = 42\n'
            'developer_instructions = "not a real role"\n',
            encoding="utf-8",
        )
        with mock.patch.object(doctor, "tomllib", None):
            self.assertEqual(
                doctor.parse_codex_agent(planner.read_text(encoding="utf-8")), (None, None)
            )
            code, output = self.diagnose("Codex")
        self.assertEqual(code, 0, output)
        self.assertIn("Codex native workflow agent TOMLs installed: 3/3", output)
        self.assertIn("Static TOML validation: UNVERIFIED", output)
        self.assertIn("Statically discoverable: unknown", output)
        self.assertNotIn("Statically discoverable: yes", output)
        self.assertIn("Codex agent file differs from the shipped template", output)

    def test_doctor_reports_pi_native_entries_and_runtime_unknown(self):
        self.install("-Scope", "User", "-Harness", "Pi")
        code, output = self.diagnose("Pi")
        self.assertEqual(code, 0, output)
        self.assertIn("Pi native shared skill entry installed: 7/7", output)
        self.assertIn("Runtime skill loading and delegation: UNVERIFIED", output)
        self.assertNotIn("Legacy skill entry", output)

    def test_doctor_errors_on_invalid_pi_skill_link(self):
        self.install("-Scope", "User", "-Harness", "Pi")
        entry = self.pi_skill_root() / "plan-solution"
        if entry.exists():
            entry.rmdir() if os.name == "nt" else entry.unlink()
        entry.mkdir(parents=True)
        shutil.copy2(self.shared / "plan-solution/SKILL.md", entry / "SKILL.md")
        code, output = self.diagnose("Pi")
        self.assertEqual(code, 1, output)
        self.assertIn("Invalid or missing Pi skill link", output)

    def test_doctor_pi_link_root_equal_to_shared_is_not_legacy(self):
        self.env["PI_CODING_AGENT_DIR"] = str(self.home / ".agents")
        self.install("-Scope", "User", "-Harness", "Pi")
        code, output = self.diagnose("Pi")
        self.assertEqual(code, 0, output)
        self.assertNotIn("Legacy skill entry", output)


if __name__ == "__main__":
    unittest.main()
