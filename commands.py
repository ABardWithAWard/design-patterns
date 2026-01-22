from abc import ABC, abstractmethod

class Command(ABC):
    """
    The Command interface. Defines the contract for all executable actions
    within the smart home system.
    """
    @abstractmethod
    def execute(self):
        """
        Executes the specific operation.
        Subclasses implement this to interact with their receivers.
        """
        pass

class TogglePowerCommand(Command):
    """
    A concrete command to flip the power state of any SmartDevice.
    This demonstrates the Command pattern's ability to handle different
    receivers through a common interface.
    """
    def __init__(self, device):
        """
        :param device: The SmartDevice (Receiver) to be controlled.
        """
        self.device = device

    def execute(self):
        """
        Logic to toggle power based on the current state of the device.
        """
        if not self.device._is_on:
            return self.device.powerOn()
        return self.device.powerOff()

class ChangeTempCommand(Command):
    """
    A specialized command for Thermostat devices.
    Encapsulates both the receiver and the parameters needed for the action.
    """
    def __init__(self, thermostat, temp):
        """
        :param thermostat: The SmartThermostat instance.
        :param temp: The target temperature value.
        """
        self.thermostat = thermostat
        self.temp = temp

    def execute(self):
        """
        Invokes the temperature change logic on the thermostat.
        """
        return self.thermostat.change_temp(self.temp)