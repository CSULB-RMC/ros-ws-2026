import rclpy
from rclpy.node import Node
import math
from datetime import datetime

from std_msgs.msg import Int8, String


class TeleopBot(Node):

    def __init__(self):
        super().__init__('teleop_bot')
        self.get_logger().info('[%s] Teleop Bot Running' % datetime.now().strftime("%H:%M:%S"))

        self.dt_left_subscriber = self.create_subscription(Int8, 'dt_left', self.dt_left_callback, 10)
        self.dt_right_subscriber = self.create_subscription(Int8, 'dt_right', self.dt_right_callback, 10)

    def dt_left_callback(self, msg):
        self.get_logger().info('data: "%s"' % msg.data)
    
    def dt_right_callback(self, msg):
        self.get_logger().info('data: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)

    teleop_bot = TeleopBot()

    rclpy.spin(teleop_bot)

    teleop_bot.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()