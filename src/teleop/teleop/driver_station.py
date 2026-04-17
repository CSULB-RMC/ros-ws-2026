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
        self.linkage = 0
        self.excavator = 0
        self.containment = 0

        self.joy_subcriber = self.create_subscription(Joy, 'joy', self.joystick_callback, 10)

        # Drivetrain publishers
        self.dt_left_publisher = self.create_publisher(Int8, 'dt_left', 10)
        self.dt_right_publisher = self.create_publisher(Int8, 'dt_right', 10)

        # linkage publisher # publish type, topic, queue size
        self.linkage_publisher = self.create_publisher(Int8, 'linkage', 10)

        # excavator publisher # publish type, topic, queue size
        self.excavator_publisher = self.create_publisher(Int8, 'excavator', 10)

        # containment publisher # publish type, topic, queue size
        self.containment_publisher = self.create_publisher(Int8, 'containment', 10)

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

        # linkage system (Left Bumper Retract, Right Bumper Extend)
        # extend = 1
        # retract = -1
        # stop = 0
        if msg.buttons[5]:
            new_msg.data = 1
        elif msg.buttons[4]:
            new_msg.data = -1
        else:
            new_msg.data = 0
        if new_msg.data != self.linkage:
            self.linkage = new_msg.data
            self.linkage_publisher.publish(new_msg)

        # excavator system - Right Trigger (B reverse)
        # forwards (dig) = 1
        # backwards = -1
        # stop = 0
        if msg.buttons[7]:
            new_msg.data = 1
            # input the combo b button here to reverse
            if (msg.buttons[1]): # B Button Needed)
                new_msg.data = -1
        else:
            new_msg.data = 0
        if new_msg.data != self.excavator:
            self.excavator = new_msg.data
            self.excavator_publisher.publish(new_msg)

        # containment system - Left Trigger (B reverse)
        # forwards (dump) = 1
        # backwards = -1 need to test, might throw sand into the robot
        # stop = 0
        if msg.buttons[6]:
            new_msg.data = 1
            # input the combo b button here to reverse
            if (msg.buttons[1]): # B Button Needed)
                new_msg.data = -1
        else:
            new_msg.data = 0
        if new_msg.data != self.containment:
            self.containment = new_msg.data
            self.containment_publisher.publish(new_msg)

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