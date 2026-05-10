"""Abstract interface that every platform backend must implement."""

from abc import ABC, abstractmethod
from pathlib import Path


class PlatformBase(ABC):
    @abstractmethod
    def screenshot(self) -> bytes:
        """Capture the current screen and return PNG bytes."""

    @abstractmethod
    def show_popup(self, title: str, message: str) -> None:
        """Display a native message-box (best-effort; non-fatal if unavailable)."""

    @abstractmethod
    def install_persistence(self, script_path: str) -> bool:
        """Register *script_path* to run at login.  Returns True on success."""

    @abstractmethod
    def temp_dir(self) -> Path:
        """Return a writable temporary directory."""
