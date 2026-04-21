import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Float32MultiArray # Using MultiArray for wheels
import tkinter as tk
from tkinter import ttk
import threading

class RoverGui(Node):
    def __init__(self):
        super().__init__('rover_gui_node')

        # --- ROS 2 Subscribers ---
        self.create_subscription(String, 'rover_state', self.state_callback, 10)
        self.create_subscription(Float32, 'battery_voltage', self.voltage_callback, 10)
        self.create_subscription(Float32, 'power_draw', self.amps_callback, 10)
        self.create_subscription(Float32MultiArray, 'wheel_current_caps', self.wheel_caps_callback, 10)

        # --- Tkinter Setup ---
        self.root = tk.Tk()
        self.root.title("Rover Diagnostics")
        self.root.geometry("400x500")

        # UI Variables
        self.state_var = tk.StringVar(value="IDLE")
        self.volt_var = tk.StringVar(value="0.0 V")
        self.draw_var = tk.StringVar(value="0.0 A")

        # --- UI Layout ---
        # State Section
        tk.Label(self.root, text="System State", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self.root, textvariable=self.state_var, font=("Arial", 18), fg="green").pack()

        # Power Draw
        power_frame = tk.Frame(self.root)
        power_frame.pack(pady=20)
        tk.Label(power_frame, text="Voltage:", font=("Arial", 10)).grid(row=0, column=0)
        tk.Label(power_frame, textvariable=self.volt_var, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)
        tk.Label(power_frame, text="Total Draw:", font=("Arial", 10)).grid(row=1, column=0)
        tk.Label(power_frame, textvariable=self.draw_var, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=10)

        # Wheel Current Caps (Visual Indicators)
        tk.Label(self.root, text="Wheel Current Caps (Amps)", font=("Arial", 12, "bold")).pack(pady=5)
        self.canvas = tk.Canvas(self.root, width=300, height=150, bg="white")
        self.canvas.pack()
        # Initialize 4 bars (one for each wheel)
        self.bars = []
        for i in range(4):
            x0 = 30 + (i * 70)
            bar = self.canvas.create_rectangle(x0, 140, x0 + 40, 140, fill="orange")
            self.bars.append(bar)
            self.canvas.create_text(x0 + 20, 145, text=f"W{i+1}", anchor="n")

    # --- Callbacks ---
    def state_callback(self, msg):
        self.state_var.set(msg.data.upper())

    def voltage_callback(self, msg):
        self.volt_var.set(f"{msg.data:.2f} V")

    def amps_callback(self, msg):
        self.draw_var.set(f"{msg.data:.2f} A")

    def wheel_caps_callback(self, msg):
        # Expecting an array of 4 floats [FL, FR, RL, RR]
        for i, val in enumerate(msg.data):
            if i < 4:
                # Scaling: 1 amp = 10 pixels high (adjust based on max expected amps) !!
                height = min(val * 10, 130) 
                x0 = 30 + (i * 70)
                self.canvas.coords(self.bars[i], x0, 140 - height, x0 + 40, 140)

    def run_gui(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    gui_node = RoverGui()

    # Run ROS spinning in a separate thread so it doesn't block Tkinter
    ros_thread = threading.Thread(target=rclpy.spin, args=(gui_node,), daemon=True)
    ros_thread.start()

    try:
        gui_node.run_gui()
    except KeyboardInterrupt:
        pass
    finally:
        gui_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
