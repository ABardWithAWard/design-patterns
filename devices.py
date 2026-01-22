from base_device import SmartDevice

class LightFixture(SmartDevice):
    def powerOn(self):
        self._is_on = True
        return f"{self.name} ON"

    def powerOff(self):
        self._is_on = False
        return f"{self.name} OFF"

class SmartThermostat(SmartDevice):
    def __init__(self, name):
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
        return f"{self.temp}°C" if self._is_on else "OFF"