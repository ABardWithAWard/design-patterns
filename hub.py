from tkinter import messagebox
from room import Room
from security_system import SecurityLock, SecurityAlarm


class HomeHub:
    def __init__(self):
        self.rooms = []

    def create_room(self, name):
        new_room = Room(name, self.on_security_breach)
        self.rooms.append(new_room)
        return new_room

    def on_security_breach(self):
        """Observer Pattern: Hub reacts to motion detection across all rooms"""
        for room in self.rooms:
            for dev in room.devices:
                if isinstance(dev, SecurityLock):
                    dev.block()
                if isinstance(dev, SecurityAlarm):
                    dev.trigger()
        messagebox.showwarning("SECURITY BREACH", "All rooms have been BLOCKED!")