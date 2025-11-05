import time

# String templates and helpers to avoid inconsistent inline formatting
HEADER_TEMPLATE = "{version:<40}{ip}"
CLIENT_HEADER = "ID\t\t       Address\t\t\t   Location\n\n"
CLIENT_ROW_TEMPLATE = "{id}\t\t{addr}\t\t{location}"
IP_TEMPLATE = "Current IP: {ip}"
ERROR_CLIENT_NOT_FOUND = "[ ! ] ERROR Client not found."
UNKNOWN_COMMAND_TEMPLATE = "[ ? ] Unknown command: {command}"
CONN_CONNECT_TEMPLATE = "{time}  Target {addr!r} connected to the server."
CONN_DISCONNECT_TEMPLATE = "{time}  Target {addr!r} disconnected from the server."
CONN_LOST_TEMPLATE = "{time}  Target {addr!r} lost connection to the server."
SNAPSHOT_SAVED_TEMPLATE = "\n{time} Snapshot saved to: {path}"
SCREENSHOT_SAVED_TEMPLATE = "\n{time} Screenshot saved to: {path}"
TIME_FMT = "%H:%M:%S"


def ts():
    """Return current timestamp string according to TIME_FMT."""
    return time.strftime(TIME_FMT)
