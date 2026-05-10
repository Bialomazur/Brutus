"""Auto-select the right platform backend at import time."""

import sys

from brutus.platform._base import PlatformBase


def get_platform() -> PlatformBase:
    if sys.platform == "win32":
        from brutus.platform._windows import WindowsPlatform

        return WindowsPlatform()
    if sys.platform == "darwin":
        from brutus.platform._macos import MacOSPlatform

        return MacOSPlatform()
    from brutus.platform._linux import LinuxPlatform

    return LinuxPlatform()
