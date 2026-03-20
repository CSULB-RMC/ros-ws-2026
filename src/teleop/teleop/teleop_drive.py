import rclpy
from rclpy.node import Node
import math
from datetime import datetime
from std_msgs.msg import Int8, String
import can
from .vesc import Vesc

class TeleopDrive(Node):

    def __init__(self):
        super().__init__('teleop_drive')

        self.BACK_RIGHT_INNER_ID = Vesc.id_conversion(13, 3)
        self.BACK_RIGHT_OUTER_ID = Vesc.id_conversion(14, 3)
        self.BACK_LEFT_INNER_ID = Vesc.id_conversion(15, 3)
        self.BACK_LEFT_OUTER_ID = Vesc.id_conversion(16, 3)
        self.FRONT_LEFT_INNER_ID = Vesc.id_conversion(17, 3)
        self.FRONT_LEFT_OUTER_ID = Vesc.id_conversion(18, 3)
        self.FRONT_RIGHT_INNER_ID = Vesc.id_conversion(19, 3)
        self.FRONT_RIGHT_OUTER_ID = Vesc.id_conversion(20, 3)

        self.left_speed = 0
        self.right_speed = 0

        self.speedlimit = 8000 # RPM

        self.dt_left_subscriber = self.create_subscription(Int8, 'dt_left', self.dt_left_callback, 10)
        self.dt_right_subscriber = self.create_subscription(Int8, 'dt_right', self.dt_right_callback, 10)
        self.dt_can_publish_timer = self.create_timer(0.01, self.can_publish_timer_callback)

        try:
            self.bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate='500000')
        except:
            try:
                self.bus = can.interface.Bus(interface='socketcan', channel='vcan0', bitrate='500000')
            except:
                self.get_logger().info('*** No Can interface was found, failed to start Teleop Bot Node ***')
                exit()

        self.get_logger().info('[%s] Teleop Bot Initialized' % datetime.now().strftime("%H:%M:%S"))

    def can_publish(self, bus, arbitration_id, data, is_extended_id) -> None:
        can_msg = can.Message(
            arbitration_id=arbitration_id, data=data, is_extended_id=is_extended_id
        )
        bus.send(can_msg)

    def dt_left_callback(self, msg):
        self.get_logger().info('left data: "%s"' % msg.data)
        self.left_speed = int(msg.data / 100 * self.speedlimit)
        # self.get_logger().info('left rpm: "%s"' % rpm)


    def dt_right_callback(self, msg):
        self.get_logger().info('right data: "%s"' % msg.data)
        self.right_speed = int(msg.data / 100 * self.speedlimit)
        # self.get_logger().info('right rpm: "%s"' % rpm)
        
    
    def can_publish_timer_callback(self):
        # convert into a 4 byte array [255, 255, 255, 255]
        left_rpm = Vesc.signal_conversion(self.left_speed, 4)
        right_rpm = Vesc.signal_conversion(self.right_speed, 4)
        
        # publish left motors
        self.can_publish(
            self.bus,
            self.BACK_LEFT_INNER_ID,
            left_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.BACK_LEFT_OUTER_ID,
            left_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.FRONT_LEFT_INNER_ID,
            left_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.FRONT_LEFT_OUTER_ID,
            left_rpm,
            True,
        )

        # publish right motors
        self.can_publish(
            self.bus,
            self.BACK_RIGHT_INNER_ID,
            right_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.BACK_RIGHT_OUTER_ID,
            right_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.FRONT_RIGHT_INNER_ID,
            right_rpm,
            True,
        )
        self.can_publish(
            self.bus,
            self.FRONT_RIGHT_OUTER_ID,
            right_rpm,
            True,
        )

def main(args=None):
    rclpy.init(args=args)

    teleop_drive = TeleopDrive()

    rclpy.spin(teleop_drive)

    teleop_drive.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()