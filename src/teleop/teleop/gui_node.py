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
        self.root.geometry("800x800") 

        # UI Variables
        self.state_var = tk.StringVar(value="IDLE")
        self.volt_var = tk.StringVar(value="0.0 V")
        self.draw_var = tk.StringVar(value="0.0 A")

        # --- UI Layout ---
        # State Section
        tk.Label(self.root, text="System State", font=("Arial", 16, "bold")).pack(pady=5)
        tk.Label(self.root, textvariable=self.state_var, font=("Arial", 18), fg="green").pack()

        # Power Draw
        power_frame = tk.Frame(self.root)
        power_frame.pack(pady=20)
        tk.Label(power_frame, text="Voltage:", font=("Arial", 14)).grid(row=0, column=0)
        tk.Label(power_frame, textvariable=self.volt_var, font=("Arial", 14, "bold")).grid(row=0, column=1, padx=10)
        tk.Label(power_frame, text="Total Draw:", font=("Arial", 14)).grid(row=1, column=0)
        tk.Label(power_frame, textvariable=self.draw_var, font=("Arial", 14, "bold")).grid(row=1, column=1, padx=10)

        # Wheel Current Caps (Visual Indicators)
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(pady=20)

        wheel_names = ["FL", "FR", "RL", "RR"]
        self.bars = []
        self.value_labels = []

        floor_y = 350 

        for i, name in enumerate(wheel_names):
            # Spread bars apart
            x0 = 40 + (i * 140)
            
            # Create the Bar (starts at floor_y)
            bar = self.canvas.create_rectangle(x0, floor_y, x0 + 80, floor_y, fill="orange")
            self.bars.append(bar)
            
            # Create the Moving Numerical Label (above the bar)
            val_label = self.canvas.create_text(x0 + 40, floor_y - 5, text="0.0A", anchor="s", font=("Arial", 14, "bold"))
            self.value_labels.append(val_label)
            
            # Create the Static Axis Label (under the bar)
            self.canvas.create_text(x0 + 40, floor_y + 10, text=name, anchor="n", font=("Arial", 16, "bold"))

    # --- Callbacks ---
    def state_callback(self, msg):
        self.state_var.set(msg.data.upper())

    def voltage_callback(self, msg):
        self.volt_var.set(f"{msg.data:.2f} V")

    def amps_callback(self, msg):
        self.draw_var.set(f"{msg.data:.2f} A")

    def wheel_caps_callback(self, msg):
        floor_y = 350

        # Expecting an array of 4 floats [FL, FR, RL, RR]
        for i, val in enumerate(msg.data):
            if i < len(self.bars): # Safety check
                # Scale: 1 Amp = 30 pixels
                height = min(val * 30, 300) 
                x0 = 40 + (i * 140)
                
                # Update bar and numerical label positions
                self.canvas.coords(self.bars[i], x0, floor_y - height, x0 + 80, floor_y)
                self.canvas.itemconfig(self.value_labels[i], text=f"{val:.1f}A")
                self.canvas.coords(self.value_labels[i], x0 + 40, floor_y - 5 - height)


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
