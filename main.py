import tkinter as tk
from tkinter import messagebox, ttk
from hub import HomeHub
from devices import LightFixture, SmartThermostat
from security_system import SecurityMotionSensor
from commands import TogglePowerCommand, ChangeTempCommand
from main_ui_classes import HomeHubUI


if __name__ == "__main__":
    hub = HomeHub()
    root = tk.Tk()
    app = HomeHubUI(root, hub)
    root.mainloop()