from base_device import SmartDevice

class LightFixture(SmartDevice):
    """
    A concrete implementation of a SmartDevice representing a light.
    Handles basic binary state (ON/OFF).
    """
    def powerOn(self):
        self._is_on = True
        return f"{self.name} ON"

    def powerOff(self):
        self._is_on = False
        return f"{self.name} OFF"


class SmartThermostat(SmartDevice):
    """
    A concrete implementation of a SmartDevice with additional
    state management for temperature control.
    """
    def __init__(self, name):
        """
        Initialize the thermostat with a default temperature of 20°C.
        """
        super().__init__(name)
        self.temp = 20

    def powerOn(self):
        self._is_on = True
        return f"{self.name} ON"

    def powerOff(self):
        self._is_on = False
        return f"{self.name} OFF"

    def change_temp(self, val):
        self.temp = val
        return f"{self.name} set to {val}°C"

    @property
    def status(self):
        """
        Overrides the base status to show temperature when active.
        :return: Current temperature string or 'OFF'.
        """
        return f"{self.temp}°C" if self._is_on else "OFF"