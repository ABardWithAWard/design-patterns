import uuid
from abc import ABC, abstractmethod

class SmartDevice(ABC):
    """
    Abstract Base Class for all smart home devices.
    Provides a unique identifier, basic power management, and
    forces concrete subclasses to implement power controls.
    """
    def __init__(self, name: str):
        """
        Initialize the core attributes of a smart device.

        :param name: The user-defined name for the device.
        """
        self.id = uuid.uuid4()
        self.name = name
        self._is_on = False

    @property
    def status(self):
        """
        Returns string of the current power state.
        :return: "ON" or "OFF"
        """
        return "ON" if self._is_on else "OFF"

    @abstractmethod
    def powerOn(self):
        pass

    @abstractmethod
    def powerOff(self):
        pass