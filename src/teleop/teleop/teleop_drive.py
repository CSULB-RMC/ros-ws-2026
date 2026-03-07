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

        self.speedlimit = 3000 # RPM

        self.dt_left_subscriber = self.create_subscription(Int8, 'dt_left', self.dt_left_callback, 10)
        self.dt_right_subscriber = self.create_subscription(Int8, 'dt_right', self.dt_right_callback, 10)

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
        rpm = int(msg.data / 100 * self.speedlimit)
        self.get_logger().info('left rpm: "%s"' % rpm)
        self.can_publish(
            self.bus,
            Vesc.id_conversion(15, 3),
            Vesc.signal_conversion(rpm, 4),
            True,
        )


    def dt_right_callback(self, msg):
        self.get_logger().info('right data: "%s"' % msg.data)
        rpm = int(msg.data / 100 * self.speedlimit)
        self.get_logger().info('right rpm: "%s"' % rpm)
        self.can_publish(
            self.bus,
            Vesc.id_conversion(17, 3),
            Vesc.signal_conversion(rpm, 4),
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