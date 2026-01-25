import os
import shutil
import subprocess
import tempfile
import unittest
import venv
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(
    cmd: List[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_bin(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts"
    return venv_dir / "bin"


class TestInstallCommands(unittest.TestCase):
    def test_editable_install_succeeds(self) -> None:
        """`python -m pip install -e .` should work.

        We pass `--no-deps` to avoid downloading heavy runtime deps (e.g. opencv-python/pyaudio)
        during unit tests, but we still validate that the install command itself succeeds.
        """
        with tempfile.TemporaryDirectory() as td:
            venv_dir = Path(td) / "venv"
            venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)

            py = _venv_python(venv_dir)
            proc = _run([str(py), "-m", "pip", "install", "-e", str(REPO_ROOT), "--no-deps"])
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"Editable install failed. Output:\n{proc.stdout}",
            )

            # Sanity check: package is importable in that environment.
            proc = _run([str(py), "-c", "import brutus; print(brutus.__name__)"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout)
            self.assertIn("brutus", proc.stdout)

    def test_runtime_dependencies_declared_in_metadata(self) -> None:
        """Validate runtime deps are declared so pip can install them when not using --no-deps."""
        with tempfile.TemporaryDirectory() as td:
            venv_dir = Path(td) / "venv"
            venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)

            py = _venv_python(venv_dir)
            proc = _run([str(py), "-m", "pip", "install", "-e", str(REPO_ROOT), "--no-deps"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout)

            # Read declared requirements from installed distribution metadata.
            code = (
                "import importlib.metadata as md; "
                "reqs = md.distribution('brutus').requires or []; "
                "print('\\n'.join(reqs))"
            )
            proc = _run([str(py), "-c", code])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout)

            requires = {line.split(";", 1)[0].strip() for line in proc.stdout.splitlines() if line.strip()}
            expected = {"requests", "pynput", "opencv-python", "pyaudio"}

            # The metadata may include version markers, but we at least expect the base names.
            missing = {dep for dep in expected if not any(r.lower().startswith(dep) for r in requires)}
            self.assertFalse(missing, msg=f"Missing dependencies from metadata: {sorted(missing)}\n{proc.stdout}")


class TestLintAndFormatCommands(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ruff"), "ruff is not installed")
    def test_ruff_check_succeeds(self) -> None:
        proc = _run(["ruff", "check", "."], cwd=REPO_ROOT)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout)

    @unittest.skipUnless(shutil.which("ruff"), "ruff is not installed")
    def test_ruff_format_check_succeeds(self) -> None:
        proc = _run(["ruff", "format", ".", "--check"], cwd=REPO_ROOT)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout)


class TestPyprojectMetadata(unittest.TestCase):
    def _load_pyproject(self) -> dict:
        try:
            import tomllib  # type: ignore[attr-defined]

            return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        except ModuleNotFoundError:
            try:
                import tomli  # type: ignore

                return tomli.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
            except ModuleNotFoundError as e:
                self.skipTest("tomllib/tomli not available to parse pyproject.toml")
                raise e

    def test_project_metadata_has_expected_dependencies(self) -> None:
        pyproject = self._load_pyproject()

        project = pyproject.get("project", {})
        self.assertEqual(project.get("name"), "brutus")
        self.assertIsInstance(project.get("version"), str)

        deps = project.get("dependencies")
        self.assertIsInstance(deps, list)
        self.assertTrue(deps, msg="project.dependencies must be non-empty")

        expected = {"requests", "pynput", "opencv-python", "pyaudio"}
        normalized = {str(d).strip() for d in deps}
        self.assertTrue(expected.issubset(normalized), msg=f"Missing deps: {sorted(expected - normalized)}")

        opt = project.get("optional-dependencies", {})
        self.assertIn("dev", opt)
        self.assertIsInstance(opt["dev"], list)
        self.assertIn("ruff", opt["dev"])
        self.assertIn("pre-commit", opt["dev"])

    def test_console_scripts_are_declared(self) -> None:
        pyproject = self._load_pyproject()
        project = pyproject.get("project", {})
        scripts = project.get("scripts", {})

        self.assertIn("brutus", scripts)
        self.assertEqual(scripts["brutus"], "brutus.cli:main")

        # Validate import path and callability.
        import importlib

        mod = importlib.import_module("brutus.cli")
        self.assertTrue(hasattr(mod, "main"), msg="brutus.cli must define main")
        self.assertTrue(callable(mod.main), msg="brutus.cli:main must be callable")


class TestScriptRegistration(unittest.TestCase):
    def test_installed_console_script_is_callable(self) -> None:
        """After install, `brutus --help` should run.

        We validate the actual console script wrapper exists and can execute.
        """
        with tempfile.TemporaryDirectory() as td:
            venv_dir = Path(td) / "venv"
            venv.EnvBuilder(with_pip=True, clear=True).create(venv_dir)

            py = _venv_python(venv_dir)
            proc = _run([str(py), "-m", "pip", "install", "-e", str(REPO_ROOT), "--no-deps"])
            self.assertEqual(proc.returncode, 0, msg=proc.stdout)

            brutus_exe = _venv_bin(venv_dir) / ("brutus.exe" if os.name == "nt" else "brutus")
            self.assertTrue(brutus_exe.exists(), msg=f"Console script not found at {brutus_exe}")

            proc = _run([str(brutus_exe), "--help"], cwd=REPO_ROOT)
            self.assertEqual(proc.returncode, 0, msg=proc.stdout)
            self.assertIn("Project CLI scaffold", proc.stdout)
