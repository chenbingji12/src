import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
import numpy as np
import cv2
import time

class LineFollowNode(Node):
    def __init__(self):
        super().__init__('line_follow_node')

        self.bridge = CvBridge()

        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

        #向speed_control_node发布速度topic
        self.publish_v_speed = self.create_publisher(Float32, '/line_follow/v_speed', 10)
        self.publish_w_speed = self.create_publisher(Float32, '/line_follow/w_speed', 10)

        #发布调试图像topic
        self.publish_debug_image = self.create_publisher(Image, '/debug_image', 10)

        self.fps=0.0
        self.start_time=time.time()
        
        self.v_speed = 0.2
        self.w_speed = 0.0

        self.kp=0.05
        self.ki=0.0
        self.kd=0.0

        self.get_logger().info('循线节点启动成功')

    def image_callback(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        debug_image = self.image.copy()

        #转为HSV空间
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        #中值滤波
        self.image = cv2.medianBlur(self.image, 3)

        #HSV白色掩模
        self.lower_white = np.array([0, 0, 200])
        self.upper_white = np.array([180, 40, 255])
        self.mask_white=cv2.inRange(self.image, self.lower_white, self.upper_white)

        #形态学处理
        open_kernel = np.ones((3,3),np.uint8)
        close_kernel = np.ones((5,5),np.uint8)
        self.mask_white = cv2.morphologyEx(self.mask_white, cv2.MORPH_OPEN, open_kernel)
        self.mask_white = cv2.morphologyEx(self.mask_white, cv2.MORPH_CLOSE, close_kernel)

        #滑动窗口，先只看底下1/9的区域
        height, width, _ = self.image.shape
        #滑动窗口设置
        self.window_count=9
        self.window_height=int(height/self.window_count)
        self.window_width=180
        self.min_white_points=10
        image_bottom = self.mask_white[int(height*8/9):,:]
        # 改用质心法找起始点
        M = cv2.moments(image_bottom)
        if M['m00'] > 0:
            white_center_x = int(M['m10'] / M['m00'])
        else:
            white_center_x = width // 2  # 找不到线就用画面中心

        center_point=[]

        #滑动窗口从下到上移动
        for window_index in range(self.window_count):
            y_low=height-self.window_height*window_index
            y_high=y_low-self.window_height
            x_left=white_center_x-self.window_width//2
            x_right=x_left+self.window_width

            # 画出窗口（调试用，实际可注释掉）
            cv2.rectangle(debug_image, (x_left, y_low), (x_right, y_high), (255, 0, 0), 2)

            #提取窗口内所有白色像素点
            white_points=self.mask_white[y_high:y_low,x_left:x_right]
            non_zero_y,non_zero_x=white_points.nonzero()

            #判断是否有足够的白色像素点
            if len(non_zero_x)<self.min_white_points:
                continue

            #把窗口中心移到白色像素点的中心
            white_center_x=int(np.mean(non_zero_x)+x_left)
            white_center_y=int(np.mean(non_zero_y)+y_high)
            #记录当前窗口的中心点
            center_point.append((white_center_x,white_center_y))

        if len(center_point)==0:
            return
        
        error_sum=0.0
        #计算偏差
        for center_index in range(len(center_point)):
            error_sum+=(center_point[center_index][0]-width//2)

        error=error_sum/len(center_point)

        #计算速度
        self.w_speed=-1.0*self.kp*error

        # if self.w_speed>0.5:
        #     self.w_speed=0.5
        # elif self.w_speed<-0.5:
        #     self.w_speed=-0.5

        self.publish_v_speed.publish(Float32(data=float(self.v_speed)))
        self.publish_w_speed.publish(Float32(data=float(self.w_speed)))

        #供rviz调试用
        debug_image = self.bridge.cv2_to_imgmsg(debug_image, 'bgr8')
        debug_image.header=msg.header
        self.publish_debug_image.publish(debug_image)

        #计算当前帧率
        self.fps+=1.0
        if time.time()-self.start_time>=2.0:
            self.fps=self.fps/(time.time()-self.start_time)
            self.get_logger().info(f'当前帧率：{self.fps}')
            self.start_time=time.time()
            self.fps=0.0

def main():
    rclpy.init()
    line_follow_node = LineFollowNode()

    try:
        rclpy.spin(line_follow_node)
    except KeyboardInterrupt:
        pass
    finally:
        line_follow_node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()