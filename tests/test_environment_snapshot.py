"""Complete metadata/freeze contract; synthetic packages and no provider imports."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from scripts import snapshot_environment as inventory


class EnvironmentSnapshotTests(TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name).resolve()
        for name in ("requirements.txt", "constraints-py311.txt"):
            (self.root / name).write_text("pip==26.2.1\nexample==1\n")
        self.enterContext(patch.object(inventory, "ROOT", self.root))
        self.metadata = self.enterContext(patch.object(inventory, "installed_pins", return_value={"pip": "26.2.1", "example": "1"}))
        self.freeze = self.enterContext(patch.object(inventory.subprocess, "run", return_value=SimpleNamespace(stdout="example==1\npip==26.2.1\n")))

    def test_all_tools_are_captured_and_files_match_metadata_and_hash(self):
        with contextlib.redirect_stdout(io.StringIO()):
            report = inventory.snapshot(Path(".local-state/environment"))
        self.assertEqual(self.freeze.call_args.args[0][-3:], ["pip", "freeze", "--all"])
        folder = self.root / ".local-state/environment"
        self.assertEqual(report["installed_count"], 2)
        self.assertEqual(report["freeze_sha256"], hashlib.sha256((folder / "requirements-freeze.txt").read_bytes()).hexdigest())
        self.assertEqual(json.loads((folder / "environment.json").read_text())["packages"], self.metadata.return_value)

    def test_extra_missing_or_drifted_freeze_is_not_exported(self):
        for content in ("example==1\n", "example==2\npip==26.2.1\n", "example==1\npip==26.2.1\nextra==2\n"):
            with self.subTest(content=content):
                self.freeze.return_value.stdout = content
                with self.assertRaises(ValueError):
                    inventory.snapshot(Path(".local-state/environment"))
                self.assertFalse((self.root / ".local-state").exists())
        self.metadata.return_value["extra"] = "2"
        with self.assertRaisesRegex(ValueError, "contrato"):
            inventory.snapshot(Path(".local-state/environment"))

    def test_direct_url_never_enters_output_or_files(self):
        self.freeze.return_value.stdout = "example @ https://synthetic:credential@example.invalid/archive\n"
        with patch.object(inventory.sys, "argv", ["snapshot"]), contextlib.redirect_stderr(io.StringIO()) as console:
            self.assertEqual(inventory.main(), 1)
        self.assertNotIn("credential", console.getvalue())
        self.assertFalse((self.root / ".local-state").exists())
        with self.assertRaises(ValueError):
            inventory.freeze_pins("example==1\nEXAMPLE==1\n")

    def test_export_outside_workspace_is_rejected(self):
        with self.assertRaises(ValueError):
            inventory.snapshot(self.root.parent / "unrelated-inventory")
