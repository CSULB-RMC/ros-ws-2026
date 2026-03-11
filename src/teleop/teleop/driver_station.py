import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import math
from datetime import datetime
from std_msgs.msg import Int8, String, Bool

class DriverStation(Node):

    def __init__(self):
        super().__init__('driver_station')

        # Constants
        self.DEADBAND = 0.05
        self.DRIVESPEEDLIMIT = 100 # DONT MAKE IT OUTSIDE RANGE OF 1-100

        # Memory variables, compare old value to prevent sending constant repeat msgs
        self.right_joystick = 0.0
        self.left_joystick = 0.0
        self.excavator = False 

        self.joy_subcriber = self.create_subscription(Joy, 'joy', self.joystick_callback, 10)

        # Drivetrain publishers
        self.dt_left_publisher = self.create_publisher(Int8, 'dt_left', 10)
        self.dt_right_publisher = self.create_publisher(Int8, 'dt_right', 10)

        # excavator publishers # publish type, topic, queue size
        self.excavator_publisher = self.create_publisher(Bool, 'excavator', 10)

        # timer that periodically publishes to ensure process is alive
        self.alive_publisher = self.create_publisher(String, "alive", 10)
        self.alive_timer = self.create_timer(1, self.alive_callback)

        self.get_logger().info('[%s] Driver Station Initialized' % datetime.now().strftime("%H:%M:%S"))

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
            self.dt_left_publisher.publish(new_msg)

        # right joystick tank drive
        # [0, 100] forward
        # [0, -100] backwards
        if msg.axes[3] > self.DEADBAND or msg.axes[3] < -self.DEADBAND:
            new_msg.data = math.floor(msg.axes[3] * self.DRIVESPEEDLIMIT)
        else:
            new_msg.data = 0
        if new_msg.data != self.right_joystick:
            self.right_joystick = new_msg.data
            self.dt_right_publisher.publish(new_msg)

        excavator_msg = Bool()
        if msg.buttons[7]==1:
            excavator_msg.data = True
        else:
            excavator_msg.data = False
        if excavator_msg.data != self.excavator:
            self.excavator = excavator_msg.data
            self.excavator_publisher.publish(excavator_msg)

    def alive_callback(self):
        msg = String()
        msg.data = "driver_station:alive"
        self.alive_publisher.publish(msg)

        

def main(args=None):
    rclpy.init(args=args)

    driver_station = DriverStation()

    rclpy.spin(driver_station)

    driver_station.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
