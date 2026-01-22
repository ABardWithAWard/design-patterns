from abc import ABC, abstractmethod
from tkinter import messagebox
from base_device import SmartDevice

# ==========================================
# BASE STATE INTERFACE
# ==========================================

class SecurityState(ABC):
    """
    Abstract interface for all possible states of a security device.
    Defines how the device behaves for every possible action.
    """
    @abstractmethod
    def arm(self, device): pass
    @abstractmethod
    def disarm(self, device): pass
    @abstractmethod
    def trigger(self, device, room_name): pass
    @abstractmethod
    def unblock(self, device): pass

    def __str__(self):
        """Returns the state name in uppercase (e.g., 'OFF', 'ARMED')."""
        return self.__class__.__name__.replace("State", "").upper()


# ==========================================
# CONCRETE STATES
# ==========================================

class OffState(SecurityState):
    """Device is inactive. Only the 'arm' action causes a state change."""
    def arm(self, device):
        device.state = ArmedState()
        return f"{device.name} is now ARMED."

    def disarm(self, device): return "Already OFF."
    def trigger(self, device, room_name): return f"{device.name} is OFF; ignoring trigger."
    def unblock(self, device): return "Not blocked."


class ArmedState(SecurityState):
    """Device is active and monitoring. Triggers cause transition to DetectedState."""
    def arm(self, device): return "Already ARMED."

    def disarm(self, device):
        device.state = OffState()
        return f"{device.name} is now DISARMED."

    def trigger(self, device, room_name):
        device.state = DetectedState()
        # If a sensor has a callback to the Hub, notify it of the breach
        if hasattr(device, 'hub_callback'):
            device.hub_callback()

        if isinstance(device, SecurityAlarm):
            full_msg = f"LOCATION: {room_name}\nALARM: {device.name} is sounding!"
            messagebox.showerror("SECURITY BREACH", full_msg)

    def unblock(self, device): return "Not blocked."


class DetectedState(SecurityState):
    """A breach was detected. Requires manual disarm (clear) to return to OFF."""
    def arm(self, device): return "Clear the alert first."

    def disarm(self, device):
        device.state = OffState()
        return f"Alert cleared. {device.name} is now OFF."

    def trigger(self, name): return "Already triggered."
    def unblock(self, device): return "Not blocked."


class BlockedState(SecurityState):
    """System-wide lockdown state. Only the 'unblock' command can exit this state."""
    def arm(self, device): return "System is locked down!"
    def disarm(self, device): return "System is locked down!"
    def trigger(self, device, name): return "Device is blocked."

    def unblock(self, device):
        device.state = OffState()
        return f"{device.name} has been UNBLOCKED."


# ==========================================
# CONTEXT CLASSES (DEVICES)
# ==========================================

class SecurityDevice(SmartDevice):
    """
    The Context class. It maintains a reference to a SecurityState object
    which defines the current behavior of the device.
    """
    def __init__(self, name):
        super().__init__(name)
        self.state = OffState()

    def powerOn(self): return self.state.arm(self)
    def powerOff(self): return self.state.disarm(self)

    @property
    def status(self): return str(self.state)


class SecurityLock(SecurityDevice):
    """Specific security device that can enter a BlockedState."""
    def block(self):
        self.state = BlockedState()
        return f"{self.name} is now BLOCKED."

    def unblock(self):
        return self.state.unblock(self)

# Observer linked to a room
class SecurityMotionSensor(SecurityDevice):
    """Sensor that triggers the Hub callback upon motion detection."""
    def __init__(self, name, hub_callback):
        super().__init__(name)
        self.hub_callback = hub_callback

    def trigger_detection(self):
        return self.state.trigger(self, self.name)


class SecurityAlarm(SecurityDevice):
    """Alarm/Siren that provides visual/auditory feedback in the UI when triggered."""
    def trigger(self, room_name="Unknown"):
        result = self.state.trigger(self, room_name)
        if isinstance(self.state, DetectedState):
            messagebox.showerror("ALARM", f"Siren sounding in {room_name}!")
        return result