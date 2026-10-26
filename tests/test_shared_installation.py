"""Exercise the public installer/doctor against disposable user and project roots."""
import os
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
        for name in ("skills", "agents", ".omp/agents", ".pi/agents", "commands", "config", "scripts"):
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
        for root in (".codex/skills", ".omp/agent/skills", ".pi/agent/skills"):
            for name in doctor.SKILLS:
                self.assertFalse((self.home / root / name).exists())
        for name in doctor.SKILLS:
            self.assertEqual((self.home / ".claude/skills" / name).resolve(), (self.shared / name).resolve())
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
        for name in ("omp", "pi", "claude"):
            path = bins / (name + ".cmd" if os.name == "nt" else name)
            path.write_text("@exit /b 0\n" if os.name == "nt" else "#!/bin/sh\nexit 0\n", encoding="utf-8")
            path.chmod(0o755)
        env = dict(self.env, PATH=str(bins) + os.pathsep + self.env["PATH"])
        result = subprocess.run([sys.executable, str(self.repo / "scripts/doctor.py"), "--scope", "Project",
                                 "--harness", "All", "--project-path", str(self.project)],
                                env=env, capture_output=True, text=True, timeout=30)
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
            if ".claude" in old.parts:
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

    def test_agent_directory_override_only_moves_adapters_and_legacy_root(self):
        override = self.base / "custom agent directory"
        self.env["PI_CODING_AGENT_DIR"] = str(override)
        self.legacy(override / "skills")
        self.install("-Scope", "User", "-Harness", "All")
        self.assert_shared()
        self.assertFalse((override / "skills/run-engineering-workflow").exists())
        self.assertTrue((override / "agents/workflow-planner.md").is_file())
        self.assertTrue((override / "start-engineering-workflow.py").is_file())
        self.assertFalse((self.home / ".omp").exists())
        self.assertFalse((self.home / ".pi").exists())


if __name__ == "__main__":
    unittest.main()
