
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import serial
import serial.tools.list_ports


class ESP32LEDController:

    def __init__(self, root):
        self.root = root
        root.title("ESP32 LED Controller")
        root.geometry("380x470")
        root.resizable(False, False)
        root.configure(bg="#F2F2F2")

        self.ser = None
        self.is_connected = False
        self.stop_thread = False

        tk.Label(root, text="LED CONTROL", font=("Arial", 18, "bold"),
                 bg="#F2F2F2").pack(pady=12)

        frame = tk.Frame(root, bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            frame, textvariable=self.port_var,
            state="readonly", width=12
        )
        self.port_combo.pack(side="left", expand=True, fill="x")

        tk.Button(frame, text="↻", command=self.refresh_ports).pack(
            side="left", padx=4
        )

        self.connect_btn = tk.Button(
            frame, text="CONNECT", bg="#A982E8",
            command=self.toggle_connection
        )
        self.connect_btn.pack(side="left")

        state = tk.Frame(root, bg="white", pady=12)
        state.pack(fill="x", padx=20, pady=12)

        tk.Label(
            state, text="CURRENT LED STATE",
            bg="white", font=("Arial", 9, "bold")
        ).pack()

        self.led_state = tk.StringVar(value="DISCONNECTED")
        self.state_label = tk.Label(
            state, textvariable=self.led_state,
            bg="white", font=("Arial", 14, "bold")
        )
        self.state_label.pack(pady=5)

        self.description = tk.Label(
            state, text="Connect your ESP32 to begin", bg="white"
        )
        self.description.pack()

        self.status = tk.StringVar(value="● DISCONNECTED")
        self.status_label = tk.Label(
            root, textvariable=self.status, bg="#F2F2F2"
        )
        self.status_label.pack(pady=5)

        tk.Label(
            root, text="LIGHTING MODES", bg="#F2F2F2",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.buttons = []

        for name, color, command in [
            ("BLINK", "#A982E8", "1"),
            ("ALTERNATE", "#9270CE", "2"),
            ("RUN", "#8060B5", "3")
        ]:
            btn = tk.Button(
                root, text=name, bg=color, fg="black",
                font=("Arial", 10, "bold"), height=2,
                command=lambda c=command: self.send_command(c)
            )
            btn.pack(fill="x", padx=20, pady=5)
            self.buttons.append(btn)

        self.set_buttons("disabled")
        self.refresh_ports()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports

        if ports:
            self.port_combo.current(0)
        else:
            self.port_var.set("")

    def toggle_connection(self):
        if self.is_connected:
            self.disconnect()
            return

        port = self.port_var.get()

        if not port:
            messagebox.showwarning("No Port", "Select a COM port.")
            return

        try:
            self.ser = serial.Serial(port, 9600, timeout=0.5)
            time.sleep(2)
            self.ser.reset_input_buffer()

            self.is_connected = True
            self.stop_thread = False

            self.connect_btn.config(
                text="DISCONNECT", bg="#E58B8B"
            )
            self.port_combo.config(state="disabled")
            self.set_buttons("normal")

            self.update_state(
                "IDLE (READY)",
                "ESP32 connected successfully",
                "green"
            )

            self.status.set(f"● CONNECTED TO {port}")
            self.status_label.config(fg="green")

            threading.Thread(
                target=self.read_serial_loop, daemon=True
            ).start()

        except (serial.SerialException, OSError) as e:
            self.ser = None
            messagebox.showerror("Connection Error", str(e))

    def disconnect(self):
        self.stop_thread = True
        self.is_connected = False

        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except (serial.SerialException, OSError):
                pass

        self.ser = None

        self.connect_btn.config(text="CONNECT", bg="#A982E8")
        self.port_combo.config(state="readonly")
        self.set_buttons("disabled")

        self.update_state(
            "DISCONNECTED",
            "Connect your ESP32 to begin",
            "gray"
        )

        self.status.set("● DISCONNECTED")
        self.status_label.config(fg="gray")

    def set_buttons(self, state):
        for btn in self.buttons:
            btn.config(state=state)

    def update_state(self, title, description, color):
        self.led_state.set(title)
        self.state_label.config(fg=color)
        self.description.config(text=description)

    def send_command(self, mode):
        if self.is_connected and self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{mode}\n".encode())

                self.status.set(f"● COMMAND SENT: MODE {mode}")
                self.status_label.config(fg="green")

            except (serial.SerialException, OSError) as e:
                messagebox.showerror("Serial Error", str(e))
                self.disconnect()

    def read_serial_loop(self):
        while not self.stop_thread and self.is_connected:
            try:
                if self.ser and self.ser.is_open and self.ser.in_waiting:
                    response = self.ser.readline().decode(
                        "utf-8", errors="ignore"
                    ).strip()

                    if response:
                        self.root.after(
                            0, self.handle_response, response
                        )

                time.sleep(0.05)

            except (serial.SerialException, OSError):
                if not self.stop_thread:
                    self.root.after(0, self.disconnect)
                break

    def handle_response(self, response):

        messages = {
            "ESP32 LED Controller Ready":
                ("IDLE (READY)", "ESP32 connected successfully", "green"),

            "Mode 1 selected - BLINK":
                ("ACTIVE: BLINK", "Mode 1 • All LEDs blinking", "#A982E8"),

            "Mode 2 selected - ALTERNATE":
                ("ACTIVE: ALTERNATE", "Mode 2 • LED groups alternating", "#A982E8"),

            "Mode 3 selected - RUNNING":
                ("ACTIVE: RUN", "Mode 3 • Forward and reverse sequence", "#A982E8"),

            "Mode 3 selected - RUNNING LIGHTS":
                ("ACTIVE: RUN", "Mode 3 • Forward and reverse sequence", "#A982E8"),

            "All LEDs OFF":
                ("ALL LEDs OFF", "Both physical switches are DOWN", "gray")
        }

        if response in messages:
            self.update_state(*messages[response])

        elif response == "Invalid Input":
            self.status.set("● INVALID COMMAND")
            self.status_label.config(fg="red")

        # Ignore other ESP32 messages so they
        # won't overwrite the current GUI status.

    def on_closing(self):
        self.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32LEDController(root)
    root.mainloop()
