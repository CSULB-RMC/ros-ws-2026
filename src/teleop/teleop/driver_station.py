import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import math

from std_msgs.msg import Int8, String


class DriverStation(Node):

    def __init__(self):
        super().__init__('driver_station')

        # Constants
        self.DEADBAND = 0.05
        self.DRIVESPEEDLIMIT = 100 # DONT MAKE IT OUTSIDE RANGE OF 1-100

        # Memory variables, compare old value to prevent sending constant repeat msgs
        self.right_joystick = 0.0
        self.left_joystick = 0.0

        self.joy_sub = self.create_subscription(Joy, 'joy', self.joystick_callback, 10)

        self.dt_l_publisher_ = self.create_publisher(Int8, 'dt_left', 10)
        self.dt_r_publisher_ = self.create_publisher(Int8, 'dt_right', 10)

        # timer that periodically publishes to ensure process is alive
        self.alive_publisher_ = self.create_publisher(String, "alive", 10)
        self.alive_timer = self.create_timer(1, self.alive_callback)

    def joystick_callback(self, msg: Joy):
        new_msg = Int8()

        # left joystick tank drive
        # [0, 100] forward
        # [0, -100] backwards
        if msg.axes[1] > self.DEADBAND or msg.axes[1] < -self.DEADBAND:
            new_msg.data = math.floor(msg.axes[1] * self.DRIVESPEEDLIMIT)
        else:
            new_msg.data = 0
        if new_msg.data != self.left_joystick:
            self.left_joystick = new_msg.data
            self.dt_l_publisher_.publish(new_msg)

        # right joystick tank drive
        # [0, 100] forward
        # [0, -100] backwards
        if msg.axes[3] > self.DEADBAND or msg.axes[3] < -self.DEADBAND:
            new_msg.data = math.floor(msg.axes[3] * self.DRIVESPEEDLIMIT)
        else:
            new_msg.data = 0
        if new_msg.data != self.right_joystick:
            self.right_joystick = new_msg.data
            self.dt_r_publisher_.publish(new_msg)

    def alive_callback(self):
        msg = String()
        msg.data = "driver_station:alive"
        self.alive_publisher_.publish(msg)

        

def main(args=None):
    rclpy.init(args=args)

    driver_station = DriverStation()

    rclpy.spin(driver_station)

    driver_station.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()