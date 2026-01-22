from devices import LightFixture, SmartThermostat
from security_system import SecurityLock, SecurityMotionSensor, SecurityDevice, SecurityAlarm


class Room:
    """
    Represents a physical room in the smart home.
    It acts as a container for devices and a mediator for security events.
    """

    def __init__(self, name, breach_callback):
        """
        Initialize the Room.

        :param name: The name of the room (e.g., "Living Room").
        :param breach_callback: A function to call when a security breach is confirmed
                                (usually triggers the main system alarm).
        """
        self.name = name
        self.devices = []
        self.breach_callback = breach_callback

    def add_device(self, type_str, name):
        """
        Factory method to create and register a new device in the room.

        :param type_str: The type of device to create ("Light", "Thermostat", "Lock", "Motion Sensor", "Alarm").
        :param name: The friendly name for the new device.
        :return: The instantiated device object.
        """
        # Mapping string identifiers to class constructors or lambdas
        mapping = {
            "Light": LightFixture,
            "Thermostat": SmartThermostat,
            "Lock": SecurityLock,
            # Motion sensors require the breach callback injection
            "Motion Sensor": lambda n: SecurityMotionSensor(n, self.breach_callback),
            "Alarm": SecurityAlarm,
        }

        if type_str not in mapping:
            raise ValueError(f"Unknown device type: {type_str}")

        # Instantiate the device using the mapping
        dev = mapping[type_str](name)
        self.devices.append(dev)
        return dev

    def breach_callback(self):
        """
        Orchestrates the room's response to a security breach.

        This method acts as a local mediator: when a MotionSensor detects movement,
        this method is triggered to notify other security devices in the same room
        (e.g., locking doors, sounding sirens).
        """
        for dev in self.devices:
            # Filter for security-related devices
            if isinstance(dev, (SecurityDevice, SecurityAlarm)):

                # Trigger alarms/sirens if they are armed
                if hasattr(dev, 'trigger') and not isinstance(dev, SecurityMotionSensor):
                    dev.trigger(room_name=self.name)

                # Immediately block any locks in the room
                if isinstance(dev, SecurityLock):
                    dev.block()