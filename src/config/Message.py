"""Protocol tokens used for attacker/victim communication.

Notes
- Prefer stable, machine-friendly, lowercase `snake_case` command tokens.
- Responses follow a structured `OK:` / `ERROR:` convention.
- Legacy tokens are kept for backward compatibility.
"""

from enum import Enum


class Message(str, Enum):
    # ---- Encoding (industry standard) ----
    TEXT_ENCODING = "utf-8"

    # ---- Attacker -> Victim commands (preferred) ----
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

    # Generic passthrough execution (shell/OS command)
    CMD_EXECUTE = "execute"

    # ---- Victim -> Attacker status messages (structured + professional) ----
    STATUS_SCREENSHOT_CAPTURED = "OK:SCREENSHOT_CAPTURED"
    STATUS_SNAPSHOT_CAPTURED = "OK:SNAPSHOT_CAPTURED"
    STATUS_VIDEO_STREAM_STARTING = "OK:VIDEO_STREAM_STARTING"
    STATUS_AUDIO_STREAM_STARTING = "OK:AUDIO_STREAM_STARTING"
    ERROR_COMMAND_FAILED = "ERROR:COMMAND_FAILED"

    # ---- Legacy command tokens (still accepted) ----
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

    # ---- Backwards-compatible aliases (old constant names -> new preferred tokens) ----
    SHOW_HEADER = CMD_SHOW_HEADER
    SHOW_CLIENTS = CMD_LIST_CLIENTS
    ECHO = CMD_ECHO
    QUIT = CMD_EXIT
    IP = CMD_PUBLIC_IP
    SEND_AT = CMD_SEND_TO_CLIENT

    TAKE_SCREENSHOT = CMD_CAPTURE_SCREENSHOT
    TSS = CMD_CAPTURE_SCREENSHOT_SHORT
    TAKE_SNAPSHOT = CMD_CAPTURE_SNAPSHOT

    START_WEBCAM = CMD_START_VIDEO_STREAM
    START_WEBCAM_SHORT = CMD_START_VIDEO_STREAM_SHORT
    START_MICROPHONE = CMD_START_AUDIO_STREAM
    START_MICROPHONE_SHORT = CMD_START_AUDIO_STREAM_SHORT

    TAKE_WEBCAM_SNAPSHOT = CMD_CAPTURE_WEBCAM_SNAPSHOT
    SHOW_POPUP = CMD_SHOW_POPUP
    EXECUTE = CMD_EXECUTE

    TAKEN_SCREENSHOT = STATUS_SCREENSHOT_CAPTURED
    TAKEN_SNAPSHOT = STATUS_SNAPSHOT_CAPTURED
    STARTING_LIVESTREAM = STATUS_VIDEO_STREAM_STARTING
    STARTING_AUDIOSTREAM = STATUS_AUDIO_STREAM_STARTING
    ERROR_MSG = ERROR_COMMAND_FAILED

    # Deprecated historical name; kept so existing code doesn't break.
    ENCODING_CP1252 = TEXT_ENCODING
