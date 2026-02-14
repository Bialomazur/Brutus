from enum import Enum

"""General configuration settings used on both ends."""


class Config(Enum):
    BACKDOOR_SERVER_IP = ""
    BACKDOOR_SERVER_PORT = 8080
    WEBCAM_SERVER_IP = ""
    WEBCAM_SERVER_PORT = 8081
    MICROPHONE_SERVER_IP = ""
    MICROPHONE_SERVER_PORT = 8082

    RECONNECT_INTERVAL = 5  # seconds
    BACKDOOR_BUFFER_SIZE = 4096  # bytes
    WEBCAM_CHUNK_SIZE = 4096  # bytes
    MICROPHONE_CHUNK_SIZE = 4096  # bytes