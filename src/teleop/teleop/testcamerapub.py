#import libraries
import cv2

#import ROS2 package modules and libraries
import rclpy
from sensor_msgs.msg import Image
from rclpy.node import Node
from cv_bridge import CvBridge

#The Node class is a standard ROS2 class. PublisherNodeClass inherits Node class
class PublisherNodeClass(Node):
    def __init__(self):
        super().__init__('publisher_node')
        self.cameraDeviceNumber=0
        self.camera = cv2.VideoCapture(self.cameraDeviceNumber)
        self.bridgeObject = CvBridge()
        self.topicNameFrames = 'topic_camera_image'
        self.queueSize=20
        self.publisher = self.create_publisher(Image, self.topicNameFrames, self.queueSize)
        self.periodCommunication = 0.02
        self.timer = self.create_timer(self.periodCommunication, self.timer_callbackFunction)
        self.i=0

    def timer_callbackFunction(self):
        success, frame = self.camera.read()
        frame = cv2.resize(frame, (820, 640), interpolation=cv2.INTER_CUBIC)
        if success == True:
            ROS2ImageMessage=self.bridgeObject_cv2_to_imgsg(frame)
            self.publish(ROS2ImageMessage)
        self.get_logger().info('Publishing image number %d' % self.i)
        self.i += 1
    def main(args=None):
        rclpy.init(args=args)
        publisherObject.destroy_node()
        rclpy.shutdown()
    if __name__ == '__main__':
        main()