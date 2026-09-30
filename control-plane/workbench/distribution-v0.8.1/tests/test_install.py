import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("installer", Path(__file__).resolve().parents[1] / "installer/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.package = self.base / "package"
        self.target = self.base / "existing project"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        self.files = {
            "README.md": b"Framework readme\n", "AGENTS.md": b"Read control-plane/README.md\n",
            ".gitignore": b".cp-venv/\n",
            ".github/copilot-instructions.md": b"Framework instructions\n",
            ".github/prompts/plan-work.prompt.md": b"Framework prompt\n",
            ".cpb.yaml": b"cp_root: control-plane\n",
            "control-plane/README.md": b"Framework guide\n",
        }
        rows = []
        for name, data in self.files.items():
            installer.write_new(self.package / "payload" / name, data)
            rows.append({"path": name, "sha256": installer.sha(data), "bytes": len(data), "mode": 0o644})
        installer.write_new(self.package / "RELEASE.json", installer.encoded({"version": "test", "source_commit": "fixture", "files": rows}))
        self.original = {"README.md": b"My product\r\n", "app.txt": b"product code\n",
                         "AGENTS.md": b"Existing policy\r\n", ".gitignore": b"node_modules/\n",
                         ".claude/settings.json": installer.encoded({"permissions": {"deny": ["Bash(rm *)"]}, "hooks": {"Stop": []}})}
        for name, data in self.original.items():
            installer.write_new(self.target / name, data)

    def tree(self):
        return {filename.relative_to(self.target).as_posix(): filename.read_bytes()
                for filename in self.target.rglob("*") if filename.is_file()}

    def test_dry_run_no_writes(self):
        before = self.tree()
        installer.install(self.package, self.target, dry_run=True)
        self.assertEqual(before, self.tree())

    def test_brownfield_preservation_backups_and_verify(self):
        installer.install(self.package, self.target, skip_venv=True)
        installer.verify(self.target)
        for name in ("README.md", "app.txt"):
            self.assertEqual((self.target / name).read_bytes(), self.original[name])
        for name in ("AGENTS.md", ".gitignore"):
            self.assertEqual((self.target / installer.BACKUPS / name).read_bytes(), self.original[name])
        self.assertTrue((self.target / "AGENTS.md").read_bytes().startswith(self.original["AGENTS.md"]))
        self.assertEqual((self.target / ".claude/settings.json").read_bytes(), self.original[".claude/settings.json"])
        self.assertFalse((self.target / "CLAUDE.md").exists())
        with self.assertRaises(ValueError):
            installer.plan(self.package, self.target)

    def test_collision_refuses_without_writes(self):
        installer.write_new(self.target / ".github/prompts/plan-work.prompt.md", b"mine")
        before = self.tree()
        with self.assertRaises(ValueError):
            installer.install(self.package, self.target, skip_venv=True)
        self.assertEqual(before, self.tree())

    def test_existing_controller_refuses(self):
        (self.target / "control-plane").mkdir()
        with self.assertRaises(ValueError):
            installer.plan(self.package, self.target)

    def test_bad_payload_refuses(self):
        (self.package / "payload/AGENTS.md").write_bytes(b"corrupt")
        before = self.tree()
        with self.assertRaises(ValueError):
            installer.plan(self.package, self.target)
        self.assertEqual(before, self.tree())

    def test_symlink_and_traversal_refuse(self):
        for name in ("../escape", "/absolute", "C:/escape", "a/../b", "a\\b"):
            with self.assertRaises(ValueError):
                installer.checked_path(self.target, name)
        try:
            (self.target / ".github").symlink_to(self.package, target_is_directory=True)
        except OSError:
            self.skipTest("Symlink creation requires Windows Developer Mode or privilege")
        with self.assertRaises(ValueError):
            installer.plan(self.package, self.target)

    def test_native_environment_paths(self):
        environment = self.target / ".cp-venv"
        self.assertEqual(installer.environment_python(environment, "nt"), environment / "Scripts/python.exe")
        self.assertEqual(installer.environment_python(environment, "posix"), environment / "bin/python")

    def test_windows_reparse_point_refuses(self):
        original = installer.redirected
        with patch.object(installer, "redirected", side_effect=lambda filename: filename == self.target / ".github" or original(filename)):
            with self.assertRaises(ValueError):
                installer.plan(self.package, self.target)

    def test_deferred_harness_payload_refuses(self):
        manifest_path = self.package / 'RELEASE.json'
        manifest = json.loads(manifest_path.read_bytes())
        before = self.tree()
        for name in ('CLAUDE.md', '.claude/settings.json', '.claude/commands/example.md'):
            candidate = dict(manifest)
            candidate['files'] = manifest['files'] + [{'path': name}]
            manifest_path.write_bytes(installer.encoded(candidate))
            with self.assertRaisesRegex(ValueError, 'Deferred harness binding'):
                installer.plan(self.package, self.target)
            self.assertEqual(before, self.tree())

    def test_caught_failure_restores_files(self):
        before = self.tree()
        with patch.object(installer, "verify", side_effect=ValueError("injected failure")):
            with self.assertRaises(ValueError):
                installer.install(self.package, self.target, skip_venv=True)
        self.assertEqual(before, self.tree())

    def test_receipt_detects_tampering(self):
        installer.install(self.package, self.target, skip_venv=True)
        (self.target / "AGENTS.md").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            installer.verify(self.target)


if __name__ == "__main__":
    unittest.main()