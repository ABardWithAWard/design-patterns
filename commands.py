from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): pass

class TogglePowerCommand(Command):
    def __init__(self, device):
        self.device = device

    def execute(self):
        if not self.device._is_on:
            return self.device.powerOn()
        return self.device.powerOff()

class ChangeTempCommand(Command):
    def __init__(self, thermostat, temp):
        self.thermostat = thermostat
        self.temp = temp

    def execute(self):
        return self.thermostat.change_temp(self.temp)