import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("start-omp.py")
SPEC = importlib.util.spec_from_file_location("start_omp", MODULE_PATH)
assert SPEC and SPEC.loader
start_omp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(start_omp)
class StartOmpCommandTests(unittest.TestCase):
    def test_web_command_uses_overlay_without_project_cwd(self):
        command = start_omp.build_launch_command(
            web=True,
            executable="ompweb.exe",
            project=Path(r"D:\project"),
            overlay=Path(r"D:\workflow\engineering-workflow.yml"),
            forwarded=["--", "--no-open"],
        )
        self.assertEqual(
            command,
            ["ompweb.exe", "--omp-config", r"D:\workflow\engineering-workflow.yml", "--no-open"],
        )

    def test_wrapper_delimited_web_flag_is_consumed(self):
        self.assertEqual(
            start_omp.split_web_mode(False, ["--", "--web", "--no-open"]),
            (True, ["--no-open"]),
        )

    def test_web_mode_only_requires_ompweb_executable(self):
        available = {"ompweb": "ompweb.exe"}
        self.assertEqual(
            start_omp.find_executable(True, available.get),
            "ompweb.exe",
        )
        self.assertIsNone(start_omp.find_executable(False, available.get))

    def test_terminal_command_keeps_project_cwd_and_overlay(self):
        command = start_omp.build_launch_command(
            web=False,
            executable="omp.exe",
            project=Path(r"D:\project"),
            overlay=Path(r"D:\workflow\engineering-workflow.yml"),
            forwarded=["--", "--continue"],
        )
        self.assertEqual(
            command,
            [
                "omp.exe",
                "--cwd",
                r"D:\project",
                "--config",
                r"D:\workflow\engineering-workflow.yml",
                "--continue",
            ],
        )


if __name__ == "__main__":
    unittest.main()
