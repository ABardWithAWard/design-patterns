from devices import LightFixture, SmartThermostat
from security_system import SecurityLock, SecurityMotionSensor, SecurityDevice, SecurityAlarm


class Room:
    def __init__(self, name, breach_callback):
        self.name = name
        self.devices = []
        self.breach_callback = breach_callback

    def add_device(self, type_str, name):
        mapping = {
            "Light": LightFixture,
            "Thermostat": SmartThermostat,
            "Lock": SecurityLock,
            "Motion Sensor": lambda n: SecurityMotionSensor(n, self.breach_callback),
            "Alarm": SecurityAlarm,
        }
        dev = mapping[type_str](name)
        self.devices.append(dev)
        return dev

    def breach_callback(self):
        """Triggered by a MotionSensor. Tells all devices in the room to react."""
        for dev in self.devices:
            if isinstance(dev, SecurityDevice) or isinstance(dev, SecurityAlarm):
                # If it's a Lock, it will block.
                # If it's a Siren/Alarm, it will only popup if its state is ARMED.
                if hasattr(dev, 'trigger') and not isinstance(dev, SecurityMotionSensor):
                    dev.trigger(room_name=self.name)

                if isinstance(dev, SecurityLock):
                    dev.block()