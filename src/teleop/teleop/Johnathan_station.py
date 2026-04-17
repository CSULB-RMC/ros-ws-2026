import rclpy
from rclpy.node import Node
import math
from datetime import datetime
from std_msgs.msg import Int8, String, Bool
import can
from .vesc import Vesc
from sensor_msgs.msg import Joy


class TeleopDrive(Node):


    def __init__(self):
        super().__init__('teleop_drive')
        #constants
        self.speedlimit = 100 #cannot exceed 100
        self.deadband = 0.05

        #intializing left and right joysticks
        self.right_joystick = 0.0
        self.left_joystick = 0.0

        #initialize buttons
        self.top_right = False
        self.top_left = False
        self.bottom_right = False
        self.bottom_left = False

        
        #joystick + button subscriber
        self.joystick_subscriber = self.create_subscription(Joy, 'joy', self.joystick_callback, 10)

        #drivetrain publishers
        self.dt_left_publisher = self.create_publisher(Int8, 'dt_left', 10)
        self.dt_right_publisher = self.create_publisher(Int8, 'dt_right', 10)

        #Top button publisher
        self.button_top_left_publisher=self.create_publisher(Bool, 'LT', 10)
        self.button_top_right_publisher = self.create_publisher(Bool, 'RT', 10)

        #Bottom Button publisher
        self.button_bottom_right_publisher = self.create_publisher(Bool,"RB",10)
        self.button_bottom_left_publisher = self.create_publisher(Bool,"LB",10)

        #send this periodically to see if code is alive
        self.alive_publisher = self.create_publisher(String,"alive",10)
        self.alive_time = self.create_timer(1,self.alive_callback)

        #code that sends string to command console
        self.get_logger().info('[%s] Driver Station Initialized' % datetime.now().strftime("%H:%M:%S"))

        
        

    def joystick_callback (self,msg:Joy):
        new_msg = Int8()
        new_msg2=Bool()

        # left joystick tank drive
        # [0, 100] forward
        # [0, -100] backwards
        if msg.axes[1] > self.deadband or msg.axes[1]<(-1*(self.deadband)):
            new_msg.data =math.floor(msg.axes[1] * self.speedlimit)
        else:
            new_msg.data = 0

        if new_msg.data != self.left_joystick: 
            self.left_joystick = new_msg.data
            self.dt_left_publisher.publish(new_msg)


        # right joystick tank drive
        # [0, 100] forward
        # [0, -100] backwards
        if msg.axes[3] > self.deadband or msg.axes[3]<-self.deadband:
            new_msg.data = math.floor(msg.axes[3] * self.speedlimit)
        else:
            new_msg.data = 0
        
        if new_msg.data!=self.right_joystick:
            self.right_joystick = new_msg.data
            self.dt_right_publisher.publish(new_msg)

        
        #top left
        #outputs 1 when hed and 0 when not held
        if (msg.buttons[6]>0):
            new_msg2.data = True
        else: 
            new_msg2.data = False
        if (not(new_msg2.data) and (self.top_left))or ((new_msg2.data)and not(self.top_left)):
            self.button_top_left_publisher.publish(new_msg2)
            self.top_left = new_msg2.data


        #top right
        #outputs 1 if held, and 0 if not
        if (msg.buttons[7]>0):
            new_msg2.data=True
        else:
            new_msg2.data = False
        if (not(new_msg2.data) and (self.top_right))or ((new_msg2.data)and not(self.top_right)):
            self.button_top_right_publisher.publish(new_msg2)
            self.top_right = new_msg2.data


        #bottom left
        #1 if held and 0 if not
        if msg.buttons[4]>0:
            new_msg2.data = True

        else: 
            new_msg2.data = False

        if (not(new_msg2.data) and (self.bottom_left))or ((new_msg2.data)and not(self.bottom_left)):
            self.button_bottom_left_publisher.publish(new_msg2)
            self.bottom_left = new_msg2.data


        #Bottom right
        #If held down output 1, else output 0
        if msg.buttons[5] > 0:
            new_msg2.data = True
        else:
            new_msg2.data = False

        if (not(new_msg2.data) and (self.bottom_right))or ((new_msg2.data)and not(self.bottom_right)):
            self.button_bottom_right_publisher.publish(new_msg2)
            self.bottom_right = new_msg2.data

            
    def alive_callback(self):
        msg = String()
        #data is a local variable
        msg.data = "driver_station:alive"
        self.alive_publisher.publish(msg)



def main(args=None):
    rclpy.init(args=args)

    teleop_drive = TeleopDrive()

    rclpy.spin(teleop_drive)

    teleop_drive.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()