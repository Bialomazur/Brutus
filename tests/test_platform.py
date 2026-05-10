"""Platform shim selection and interface tests."""

import sys
import unittest


class TestPlatformSelection(unittest.TestCase):
    def test_returns_correct_type_for_current_os(self):
        from brutus.platform import get_platform
        from brutus.platform._base import PlatformBase

        p = get_platform()
        self.assertIsInstance(p, PlatformBase)

    def test_platform_has_required_methods(self):
        from brutus.platform import get_platform

        p = get_platform()
        for method in ("screenshot", "show_popup", "install_persistence", "temp_dir"):
            self.assertTrue(callable(getattr(p, method, None)), msg=f"missing: {method}")

    def test_temp_dir_is_writable(self):
        from pathlib import Path

        from brutus.platform import get_platform

        p = get_platform()
        d = p.temp_dir()
        self.assertIsInstance(d, Path)
        self.assertTrue(d.exists())
        probe = d / ".brutus_test_probe"
        probe.write_text("ok")
        probe.unlink()

    def test_windows_backend_imported_on_win32(self):
        if sys.platform != "win32":
            self.skipTest("Windows only")
        from brutus.platform import get_platform
        from brutus.platform._windows import WindowsPlatform

        self.assertIsInstance(get_platform(), WindowsPlatform)

    def test_macos_backend_imported_on_darwin(self):
        if sys.platform != "darwin":
            self.skipTest("macOS only")
        from brutus.platform import get_platform
        from brutus.platform._macos import MacOSPlatform

        self.assertIsInstance(get_platform(), MacOSPlatform)

    def test_linux_backend_imported_on_linux(self):
        if sys.platform not in ("linux", "linux2"):
            self.skipTest("Linux only")
        from brutus.platform import get_platform
        from brutus.platform._linux import LinuxPlatform

        self.assertIsInstance(get_platform(), LinuxPlatform)
