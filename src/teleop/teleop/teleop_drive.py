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
        self.CONTAINMENT_ID = Vesc.id_conversion(21, 3)
        self.EXCAVATOR_ID = Vesc.id_conversion(22, 3)
        self.LINKAGE_ID = 23

        self.speedlimit = 10000 # RPM
        self.dig_speedlimit = 10000
        self.deposit_speedlimit = 10000

        self.dt_left_subscriber = self.create_subscription(Int8, 'dt_left', self.dt_left_callback, 10)
        self.dt_right_subscriber = self.create_subscription(Int8, 'dt_right', self.dt_right_callback, 10)

        self.linkage_subscriber = self.create_subscription(Int8, 'linkage', self.linkage_callback, 10)
        self.excavator_subscriber = self.create_subscription(Int8, 'excavator', self.excavator_callback, 10)
        self.containment_subscriber = self.create_subscription(Int8, 'containment', self.containment_callback, 10)


        try:
            self.BackDriveBus = can.interface.Bus(interface='socketcan', channel='BackDriveCan', bitrate='500000')
            # self.FrontDriveBus = can.interface.Bus(interface='socketcan', channel='FrontDriveCan', bitrate='500000')
            # change to the 3rd canable when you get it, temp bound the front can
            self.PeripheralBus = can.interface.Bus(interface='socketcan', channel = 'FrontDriveCan', bitrate='500000')
        except:
            try:
                self.bus0 = can.interface.Bus(interface='socketcan', channel='vcan0', bitrate='500000')
                self.bus1 = can.interface.Bus(interface='socketcan', channel='vcan1', bitrate='500000')
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
        rpm = int(msg.data / 100 * self.speedlimit)
        self.get_logger().info('left rpm: "%s"' % rpm)

        signal = Vesc.signal_conversion(rpm, 4)

        self.can_publish(
            self.BackDriveBus,
            self.BACK_LEFT_INNER_ID,
            signal,
            True,
        )
        self.can_publish(
            self.BackDriveBus,
            self.BACK_LEFT_OUTER_ID,
            signal,
            True,
        )
        '''
        self.can_publish(
            self.FrontDriveBus,
            self.FRONT_LEFT_INNER_ID,
            signal,
            True,
        )
        self.can_publish(
            self.FrontDriveBus,
            self.FRONT_LEFT_OUTER_ID,
            signal,
            True,
        )
        '''


    def dt_right_callback(self, msg):
        rpm = int(msg.data / 100 * self.speedlimit)
        self.get_logger().info('right rpm: "%s"' % rpm)

        signal = Vesc.signal_conversion(rpm, 4)

        self.can_publish(
            self.BackDriveBus,
            self.BACK_RIGHT_INNER_ID,
            signal,
            True,
        )
        self.can_publish(
            self.BackDriveBus,
            self.BACK_RIGHT_OUTER_ID,
            signal,
            True,
        )
        '''
        self.can_publish(
            self.FrontDriveBus,
            self.FRONT_RIGHT_INNER_ID,
            signal,
            True,
        )
        self.can_publish(
            self.FrontDriveBus,
            self.FRONT_RIGHT_OUTER_ID,
            signal,
            True,
        )
        '''

    def linkage_callback(self, msg):
        self.get_logger().info('linkage data: "%s"' % msg.data)
        self.can_publish(
            self.PeripheralBus,
            self.LINKAGE_ID,
            Vesc.signal_conversion(int(msg.data), 8),
            False
        )
    
    def excavator_callback(self, msg):
        self.get_logger().info('excavator data: "%s"' % msg.data)
        self.can_publish(
            self.PeripheralBus,
            self.EXCAVATOR_ID,
            Vesc.signal_conversion(int(msg.data) * self.dig_speedlimit, 4),
            True
        )
        

    def containment_callback(self, msg):

        self.get_logger().info('containment data: "%s"' % msg.data)
        self.can_publish(
            self.PeripheralBus,
            self.CONTAINMENT_ID,
            Vesc.signal_conversion(int(msg.data) * self.deposit_speedlimit, 4),
            True
        )

    

def main(args=None):
    rclpy.init(args=args)

    teleop_drive = TeleopDrive()

    rclpy.spin(teleop_drive)

    teleop_drive.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()