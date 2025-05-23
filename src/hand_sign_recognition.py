#!/usr/bin/python3
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from gesture_recognition import *
from cvfpscalc import CvFpsCalc
from cv_bridge import CvBridge, CvBridgeError
import cv2

class HandSignRecognition:

    def __init__(self):
        # Creates a node with name 'hand_sign_recognition' and make sure it is a
        # unique node (using anonymous=True).
        rospy.init_node('hand_sign_recognition', anonymous=True)

        self.image_subcriber = rospy.Subscriber(rospy.get_param("hand_sign_recognition/subscribe_image_topic"), 
                                                Image, self.callback)
        # Publisher which will publish to the topic 
        self.gesture_publisher = rospy.Publisher(rospy.get_param("hand_sign_recognition/publish_gesture_topic"), 
                                                String, queue_size=10)

        # Create a gesture recognition object that loads labels and train model
        self.gesture_detector = GestureRecognition(rospy.get_param("hand_sign_recognition/keypoint_classifier_label"),
                                                rospy.get_param("hand_sign_recognition/keypoint_classifier_model"))
        self.bridge = CvBridge()
        
        self.cv_fps_calc = CvFpsCalc(buffer_len=10)

    def callback(self, image_msg):
        """A callback function for the image subscriber"""
        try:
            # OpenCV图像转换
            cv_image = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding="bgr8")
            # 水平翻转
            cv_image = cv2.flip(cv_image, 1)

            # 识别手势
            debug_image, gesture = self.gesture_detector.recognize(cv_image)

            self.gesture_publisher.publish(gesture)

            # 显示图像（可选）
            if rospy.get_param("hand_sign_recognition/show_image"):
                # fps = self.cv_fps_calc.get() # Calculate FPS
                # debug_image = self.gesture_detector.draw_fps_info(debug_image, fps)
                cv2.imshow('ROS Gesture Recognition', debug_image)
                cv2.waitKey(10) # wait for 10 ms
        except CvBridgeError as error:
            print(error)



if __name__=="__main__":
    try:
        hand_sign = HandSignRecognition()
        rospy.spin()
    # If we press control + C, the node will stop.
    except rospy.ROSInternalException:
        cv.destroyAllWindows()
        pass
