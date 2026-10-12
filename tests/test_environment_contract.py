"""Pin comparison catches drift, extras, includes and missing packages."""
from importlib.metadata import PackageNotFoundError
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from types import SimpleNamespace
from scripts import check_environment as contract


class EnvironmentContractTests(TestCase):
    def test_nested_files_extras_and_name_normalization(self):
        with TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "minimal.txt").write_text("python_dotenv==1.1.1\n", encoding="utf-8")
            (base / "requirements.txt").write_text("# comment\ncrewai[litellm]==1.14.2\n-r minimal.txt\n", encoding="utf-8")
            self.assertEqual(contract.read_pins(base / "requirements.txt"),
                             {"crewai": "1.14.2", "python-dotenv": "1.1.1"})

    def test_unpinned_circular_or_conflicting_input_is_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "requirements.txt"
            for content in ("Flask>=3\n", "-r requirements.txt\n", "Flask==3.1.3\nflask==3.0.0\n"):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    contract.read_pins(path)

    def test_metadata_drift_and_absence_are_reported(self):
        def installed(name):
            if name == "missing":
                raise PackageNotFoundError(name)
            return "2.24.0" if name == "openai" else "1.83.0"
        with patch.object(contract, "version", side_effect=installed):
            self.assertEqual(contract.compare({"openai": "2.32.0", "litellm": "1.83.0", "missing": "1"}),
                             [("missing", "1", "ausente"), ("openai", "2.32.0", "2.24.0")])

    def test_windows_only_pin_is_skipped_on_other_platforms(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "pins.txt"
            path.write_text('pywin32==311; sys_platform == "win32"\n', encoding="utf-8")
            with patch.object(contract.sys, "platform", "linux"):
                self.assertEqual(contract.read_pins(path), {})

    def test_linux_pin_is_enforced_only_on_linux_and_markers_are_restricted(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "pins.txt"
            path.write_text('uvloop==0.23.0; sys_platform == "linux"\npywin32==311; sys_platform == "win32"\n')
            for platform, expected in (("linux", {"uvloop": "0.23.0"}), ("win32", {"pywin32": "311"})):
                with patch.object(contract.sys, "platform", platform):
                    self.assertEqual(contract.read_pins(path), expected)
            for marker in ('sys_platform != "win32"', 'sys_platform == "linux\'', 'os_name == "posix"'):
                path.write_text("uvloop==0.23.0; " + marker)
                with self.assertRaises(ValueError):
                    contract.read_pins(path)

    def test_strict_comparison_rejects_unpinned_packages_without_removing_them(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "pins.txt"
            path.write_text("example==1\n")
            with patch.object(contract.sys, "argv", ["check", "--requirements", str(path), "--constraints", str(path), "--strict"]), \
                    patch.object(contract, "version", return_value="1"), \
                    patch.object(contract, "distributions", return_value=[
                        SimpleNamespace(metadata={"Name": "example"}, version="1"),
                        SimpleNamespace(metadata={"Name": "Unpinned_extra"}, version="2")]), \
                    contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(contract.main(), 1)
                self.assertIn("ADICIONAL unpinned-extra", output.getvalue())
