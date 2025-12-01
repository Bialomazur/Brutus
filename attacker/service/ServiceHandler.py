from abc import ABC


class ServiceHandler(ABC):
    def __init__(self, service_name):
        self.service_name = service_name

    def start_service(self):
        print(f"Starting service: {self.service_name}")

    def stop_service(self):
        print(f"Stopping service: {self.service_name}")

    def restart_service(self):
        print(f"Restarting service: {self.service_name}")

    def get_status(self):
        print(f"Getting status of service: {self.service_name}")
        return "running"  # Placeholder status