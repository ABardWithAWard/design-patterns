from abc import ABC, abstractmethod
from tkinter import messagebox

from base_device import SmartDevice


# ==========================================
# BASE STATE INTERFACE
# ==========================================

class SecurityState(ABC):
    @abstractmethod
    def arm(self, device): pass
    @abstractmethod
    def disarm(self, device): pass
    @abstractmethod
    def trigger(self, device, room_name): pass
    @abstractmethod
    def unblock(self, device): pass

    def __str__(self):
        return self.__class__.__name__.replace("State", "").upper()


# ==========================================
# CONCRETE STATES
# ==========================================


class OffState(SecurityState):
    def arm(self, device):
        device.state = ArmedState()
        return f"{device.name} is now ARMED."

    def disarm(self, device): return "Already OFF."

    def trigger(self, device, room_name):
        # SILENT: Alarm does not sound because it is OFF
        return f"{device.name} is OFF; ignoring trigger."

    def unblock(self, device): return "Not blocked."


class ArmedState(SecurityState):
    def arm(self, device): return "Already ARMED."

    def disarm(self, device):
        device.state = OffState()
        return f"{device.name} is now DISARMED."

    def trigger(self, device, room_name):
        device.state = DetectedState()
        if hasattr(device, 'hub_callback'):
            device.hub_callback()

        if isinstance(device, SecurityAlarm):
            full_msg = f"LOCATION: {room_name}\nALARM: {device.name} is sounding!"
            messagebox.showerror("SECURITY BREACH", full_msg)

    def unblock(self, device): return "Not blocked."



class DetectedState(SecurityState):
    def arm(self, device): return "Clear the alert first."

    def disarm(self, device):
        device.state = OffState()
        return f"Alert cleared. {device.name} is now OFF."

    def trigger(self, device, name): return "Already triggered."

    def unblock(self, device): return "Not blocked."


class BlockedState(SecurityState):
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
    def __init__(self, name):
        super().__init__(name)
        self.state = OffState()  # Initial State

    def powerOn(self): return self.state.arm(self)

    def powerOff(self): return self.state.disarm(self)

    @property
    def status(self): return str(self.state)


class SecurityLock(SecurityDevice):
    def block(self):
        self.state = BlockedState()
        return f"{self.name} is now BLOCKED."

    def unblock(self):
        return self.state.unblock(self)


class SecurityMotionSensor(SecurityDevice):
    def __init__(self, name, hub_callback):
        super().__init__(name)
        self.hub_callback = hub_callback

    def trigger_detection(self):
        return self.state.trigger(self, self.name.__str__())


class SecurityAlarm(SecurityDevice):
    def __init__(self, name):
        super().__init__(name)
        self.state = OffState()  # Starts OFF

    def trigger(self, room_name="Unknown"):
        result = self.state.trigger(self, room_name)
        # Check if the state transition actually resulted in a detection
        if isinstance(self.state, DetectedState):
            messagebox.showerror("ALARM", f"Siren sounding in {room_name}!")
        return result

    @property
    def status(self): return str(self.state)