import time

VERSION = "BRUTUS V. 1.0 Beta"
TIME_FMT = "%H:%M:%S"

HEADER_TEMPLATE = "{version:<40}{ip}"
CLIENT_HEADER = "ID\t\t       Address\t\t\t   Location\n\n"
CLIENT_ROW_TEMPLATE = "{id}\t\t{addr}\t\t{location}"
IP_TEMPLATE = "Current IP: {ip}"
NO_CLIENTS_TEMPLATE = "No connected client found."
ERROR_CLIENT_NOT_FOUND = "[ ! ] ERROR Client not found."
UNKNOWN_COMMAND_TEMPLATE = "[ ? ] Unknown command: {command}"
CONNECTION_CONNECT_TEMPLATE = "{time}  Target {addr!r} connected to the server."
CONNECTION_DISCONNECT_TEMPLATE = "{time}  Target {addr!r} disconnected from the server."
CONNECTION_LOST_TEMPLATE = "{time}  Target {addr!r} lost connection to the server."
SNAPSHOT_SAVED_TEMPLATE = "\n{time} Snapshot saved to: {path}"
SCREENSHOT_SAVED_TEMPLATE = "\n{time} Screenshot saved to: {path}"


def ts() -> str:
    return time.strftime(TIME_FMT)
