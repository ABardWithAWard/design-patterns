from tkinter import messagebox
from room import Room
from security_system import SecurityLock, SecurityAlarm

#Factory design pattern
class HomeHub:
    """
    The central controller for the smart home system.
    It manages the collection of rooms and orchestrates system-wide responses
    to critical events (like security breaches).
    """

    def __init__(self):
        """Initialize the HomeHub with an empty list of rooms."""
        self.rooms = []

    def create_room(self, name):
        """
        Creates a new Room instance and registers it with the Hub.

        :param name: The name of the new room.
        :return: The newly created Room instance.
        """
        # Pass self.on_security_breach as the callback so the Room can notify the Hub
        new_room = Room(name, self.on_security_breach)
        self.rooms.append(new_room)
        return new_room

    def on_security_breach(self):
        """
        System-wide Event Handler.

        This method is triggered when *any* room reports a security breach.
        It iterates through every room in the house to:
        1. Block all SecurityLocks (System Lockdown).
        2. Trigger all SecurityAlarms.
        3. Alert the user via the UI.
        """
        for room in self.rooms:
            for dev in room.devices:
                if isinstance(dev, SecurityLock):
                    dev.block()
                if isinstance(dev, SecurityAlarm):
                    dev.trigger()

        messagebox.showwarning("SECURITY BREACH", "All rooms have been BLOCKED!")