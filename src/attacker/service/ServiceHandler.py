from abc import ABC

from src.attacker.service.Service import Service


class ServiceHandler(ABC):
    services = {}

    def __init__(self, service: Service, service_id: str):
        self.service = service
        self.service_id = service_id
        self.__class__.services[service_id] = service

    def start_service(self):
        print(f"Starting service: {self.service_id}")

    def stop_service(self):
        print(f"Stopping service: {self.service_id}")
        self.__class__.services.pop(self.service_id)

    def restart_service(self):
        print(f"Restarting service: {self.service_id}")

    def get_status(self):
        print(f"Getting status of service: {self.service_id}")
        return "running"  # Placeholder status