import uuid
from abc import ABC, abstractmethod

class SmartDevice(ABC):
    def __init__(self, name: str):
        self.id = uuid.uuid4()
        self.name = name
        self._is_on = False

    @property
    def status(self):
        return "ON" if self._is_on else "OFF"

    @abstractmethod
    def powerOn(self):
        pass

    @abstractmethod
    def powerOff(self):
        pass