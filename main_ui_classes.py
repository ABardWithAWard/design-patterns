import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from commands import TogglePowerCommand, ChangeTempCommand
from devices import LightFixture, SmartThermostat
from security_system import SecurityMotionSensor, SecurityLock, SecurityDevice, SecurityAlarm


class RemoteControlUI:
    """
    A Toplevel window acting as a central remote for specific controllable devices
    (Lights and Thermostats). Uses the Command Pattern to execute actions.
    """

    def __init__(self, parent, hub):
        """
        Initialize the remote control window.

        :param parent: The parent Tkinter widget.
        :param hub: The central HomeHub instance containing rooms and devices.
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Remote Control (Command Pattern)")
        self.window.geometry("350x450")
        self.hub = hub

        tk.Label(self.window, text="Device Commands", font=("Arial", 12, "bold")).pack(pady=10)
        self.refresh()

    def refresh(self):
        """
        Clears and rebuilds the UI to reflect the current state of devices.
        Iterates through all rooms and generates controls for LightFixtures and SmartThermostats.
        """
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame): widget.destroy()

        for room in self.hub.rooms:
            if not room.devices: continue
            group = tk.LabelFrame(self.window, text=room.name, padx=10, pady=5)
            group.pack(fill="x", padx=10, pady=5)

            for dev in room.devices:
                frame = tk.Frame(group, pady=5)
                frame.pack(fill="x")

                if isinstance(dev, LightFixture):
                    tk.Button(frame, text=f"Toggle {dev.name}",
                              command=lambda d=dev: self.execute_cmd(TogglePowerCommand(d))).pack(side=tk.LEFT)

                elif isinstance(dev, SmartThermostat):
                    pwr_color = "#90ee90" if dev.status == "ON" else "#ff9999"
                    tk.Button(frame, text="Power", bg=pwr_color, width=6,
                              command=lambda d=dev: self.execute_cmd(TogglePowerCommand(d))).pack(side=tk.LEFT, padx=2)

                    tk.Label(frame, text=f"{dev.name}:").pack(side=tk.LEFT, padx=2)

                    spin = tk.Spinbox(frame, from_=15, to=30, width=5)
                    spin.delete(0, "end")
                    spin.insert(0, int(dev.temp))
                    spin.pack(side=tk.LEFT)

                    tk.Button(frame, text="Set",
                              command=lambda d=dev, s=spin: self.execute_cmd(ChangeTempCommand(d, int(s.get())))).pack(
                        side=tk.LEFT, padx=2)

    def execute_cmd(self, cmd):
        """
        Executes a command object and refreshes the UI.

        :param cmd: A command object implementing the execute() method.
        """
        res = cmd.execute()
        print(f"Command Result: {res}")
        self.refresh()


class RoomInspectorUI:
    """
    A Toplevel window for managing a specific room. Allows adding/removing devices
    and simulating motion events.
    """

    def __init__(self, parent, room, main_refresh_callback):
        """
        Initialize the room inspector.

        :param parent: The parent Tkinter widget.
        :param room: The specific Room object to manage.
        :param main_refresh_callback: Callback to update the main HomeHubUI list.
        """
        self.window = tk.Toplevel(parent)
        self.window.title(f"Managing: {room.name}")
        self.room = room
        self.main_refresh = main_refresh_callback

        add_frame = tk.LabelFrame(self.window, text="Add Device", padx=5, pady=5)
        add_frame.pack(fill="x", padx=10, pady=5)

        self.type_var = tk.StringVar(value="Light")
        ttk.Combobox(add_frame, textvariable=self.type_var,
                     values=["Light", "Thermostat", "Lock", "Motion Sensor", "Alarm"]).pack(side=tk.LEFT)

        self.name_entry = tk.Entry(add_frame)
        self.name_entry.insert(0, "Device Name")
        self.name_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(add_frame, text="+", command=self.add_dev).pack(side=tk.LEFT)

        self.listbox = tk.Listbox(self.window, width=50)
        self.listbox.pack(pady=10, padx=10)

        tk.Button(self.window, text="Delete Selected", command=self.delete_dev, bg="#ff9999").pack(pady=2)
        tk.Button(self.window, text="SIMULATE MOTION", command=self.sim_motion, bg="orange").pack(pady=5)
        self.refresh()

    def refresh(self):
        """Populates the listbox with the current devices in the room."""
        self.listbox.delete(0, tk.END)
        for dev in self.room.devices:
            self.listbox.insert(tk.END, f"{dev.name} [{dev.__class__.__name__}] - Status: {dev.status}")
        self.main_refresh()

    def add_dev(self):
        """Creates a new device based on input fields and adds it to the room."""
        name = self.name_entry.get()
        self.room.add_device(self.type_var.get(), name)
        self.refresh()

    def delete_dev(self):
        """Removes the selected device from the room."""
        idx = self.listbox.curselection()
        if idx:
            self.room.devices.pop(idx[0])
            self.refresh()

    def sim_motion(self):
        """
        Triggers the detection logic on all Motion Sensors in the room.
        Warns if no sensors are present.
        """
        sensors_found = False
        for dev in self.room.devices:
            if isinstance(dev, SecurityMotionSensor):
                sensors_found = True
                msg = dev.trigger_detection()
                print(f"Sensor Debug: {msg}")

        if not sensors_found:
            messagebox.showwarning("Warning", "No Motion Sensor in this room!")
        self.refresh()


class HomeHubUI:
    """
    The main application window. Displays the list of rooms and provides access
    to specific subsystems (Remote, Security Panel).
    """

    def __init__(self, root, hub):
        """
        Initialize the main dashboard.

        :param root: The root Tkinter window.
        :param hub: The central HomeHub instance.
        """
        self.hub = hub
        self.root = root
        self.root.title("Smart Home System")
        self.sample_counter = 1

        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(fill="x", padx=10)

        tk.Button(top_frame, text="Remote Control", width=15, command=self.open_remote, bg="lightblue").pack(
            side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Security Panel", width=15, command=self.open_security, bg="#ffcccb").pack(
            side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="+ Add Room", width=12, command=self.add_room, bg="#90ee90").pack(side=tk.LEFT,
                                                                                                    padx=5)
        tk.Button(top_frame, text="+ Sample Room", width=15, command=self.add_sample_room, bg="#e1bee7").pack(
            side=tk.LEFT, padx=5)

        tk.Label(root, text="Double-click a room to manage devices:", font=("Arial", 9, "italic")).pack(pady=(10, 0))
        self.room_listbox = tk.Listbox(root, width=50, height=10)
        self.room_listbox.pack(padx=20, pady=10, fill="both", expand=True)
        self.room_listbox.bind('<Double-1>', self.open_room)
        self.refresh()

    def add_sample_room(self):
        """Generates a room populated with a full suite of test devices."""
        name = f"SampleRoom{self.sample_counter}"
        new_room = self.hub.create_room(name)
        new_room.add_device("Light", "Main Light" + self.sample_counter.__str__())
        new_room.add_device("Thermostat", "AC Unit" + self.sample_counter.__str__())
        new_room.add_device("Lock", "Front Door" + self.sample_counter.__str__())
        new_room.add_device("Motion Sensor", "Window Sensor" + self.sample_counter.__str__())
        new_room.add_device("Alarm", "Main Siren" + self.sample_counter.__str__())
        self.sample_counter += 1
        self.refresh()

    def refresh(self):
        """Updates the room listbox."""
        self.room_listbox.delete(0, tk.END)
        if not self.hub.rooms:
            self.room_listbox.insert(tk.END, "No rooms added yet.")
        else:
            for r in self.hub.rooms:
                self.room_listbox.insert(tk.END, f"{r.name} — ({len(r.devices)} devices)")

    def add_room(self):
        """Prompts user for a room name and adds it to the hub."""
        room_name = simpledialog.askstring("New Room", "Enter room name:", parent=self.root)
        if room_name and room_name.strip():
            self.hub.create_room(room_name.strip())
            self.refresh()

    def open_room(self, event):
        """Opens the RoomInspectorUI for the double-clicked room."""
        idx = self.room_listbox.curselection()
        if idx and self.hub.rooms:
            RoomInspectorUI(self.root, self.hub.rooms[idx[0]], self.refresh)

    def open_remote(self):
        """Opens the generic Remote Control UI."""
        if not self.hub.rooms: return
        RemoteControlUI(self.root, self.hub)

    def open_security(self):
        """Opens the dedicated Security Dashboard."""
        if not self.hub.rooms:
            messagebox.showinfo("Security", "Add rooms and security devices first!")
            return
        SecurityDashboardUI(self.root, self.hub, self.refresh)


class SecurityDashboardUI:
    """
    A specialized Toplevel window for monitoring and controlling security devices.
    Features global Arm/Disarm controls and a scrollable list of security devices.
    """

    def __init__(self, parent, hub, main_refresh):
        """
        Initialize the security dashboard.

        :param parent: The parent Tkinter widget.
        :param hub: The central HomeHub instance.
        :param main_refresh: Callback to refresh the main UI.
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Master Security Oversight")
        self.window.geometry("600x600")
        self.hub = hub
        self.main_refresh = main_refresh

        master_frame = tk.LabelFrame(self.window, text="Master Controls", padx=10, pady=10)
        master_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(master_frame, text="ARM ALL", bg="#ffcccc", font=("Arial", 9, "bold"),
                  command=lambda: self.global_security_action("arm")).pack(side=tk.LEFT, expand=True, fill="x",
                                                                           padx=5)
        tk.Button(master_frame, text="DISARM ALL", bg="#ccffcc", font=("Arial", 9, "bold"),
                  command=lambda: self.global_security_action("disarm")).pack(side=tk.LEFT, expand=True, fill="x",
                                                                              padx=5)

        self.canvas = tk.Canvas(self.window)
        self.scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh()

    def refresh(self):
        """
        Rebuilds the security device list inside the scrollable frame.
        Filters devices to show only SecurityDevice or SecurityAlarm instances.
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for room in self.hub.rooms:
            sec_devices = [d for d in room.devices if isinstance(d, (SecurityDevice, SecurityAlarm))]
            if not sec_devices: continue

            tk.Label(self.scroll_frame, text=f"ROOM: {room.name}",
                     font=("Arial", 11, "bold"), fg="darkblue", pady=5).pack(fill="x")

            for dev in sec_devices:
                frame = tk.Frame(self.scroll_frame, bd=1, relief="groove", pady=5)
                frame.pack(fill="x", padx=10, pady=2)

                status_str = str(dev.status)
                color = "green" if status_str == "OFF" else "orange" if status_str == "ARMED" else "red"

                tk.Label(frame, text=f"{dev.name} ({dev.__class__.__name__})",
                         width=25, anchor="w").pack(side=tk.LEFT, padx=5)

                tk.Label(frame, text=status_str, width=10, fg=color,
                         font=("Arial", 9, "bold")).pack(side=tk.LEFT)

                tk.Button(frame, text="Arm", command=lambda d=dev: self.update_dev(d, "arm")).pack(side=tk.LEFT,
                                                                                                   padx=2)
                tk.Button(frame, text="Disarm", command=lambda d=dev: self.update_dev(d, "disarm")).pack(
                    side=tk.LEFT, padx=2)
                if isinstance(dev, SecurityLock):
                    tk.Button(frame, text="Unblock", bg="#ffffcc",
                              command=lambda d=dev: self.update_dev(d, "unblock")).pack(side=tk.LEFT, padx=2)

    def global_security_action(self, action):
        """
        Arms or disarms every security device in the house.

        :param action: 'arm' to power on, 'disarm' to power off.
        """
        for room in self.hub.rooms:
            for dev in room.devices:
                if isinstance(dev, SecurityDevice):
                    if action == "arm":
                        dev.powerOn()
                    else:
                        dev.powerOff()
        self.refresh()
        self.main_refresh()

    def update_dev(self, dev, action):
        """
        Performs an action on a single security device.

        :param dev: The device object.
        :param action: 'arm', 'disarm', or 'unblock'.
        """
        if action == "arm":
            dev.powerOn()
        elif action == "disarm":
            dev.powerOff()
        elif action == "unblock" and hasattr(dev, 'unblock'):
            dev.unblock()
        self.refresh()
        self.main_refresh()