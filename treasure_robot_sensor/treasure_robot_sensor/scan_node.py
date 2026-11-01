import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from rclpy.qos import qos_profile_sensor_data
import math

class ScanNode(Node):
    def __init__(self):
        super().__init__('scan_node')

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile=qos_profile_sensor_data
        )

        self.w_pub = self.create_publisher(Float32, '/scan/w_speed', 10)

        self.kp=0.05

        #设置默认的处理角度范围
        self.min_angle = 135.0
        self.max_angle = 225.0

        #设置悬崖判定阈值
        self.cliff_threshold=5.0

        self.error=0.0

        self.get_logger().info('激光雷达节点启动成功')

    def scan_callback(self, msg):
        #在135度到225度之间取值
        selected_ranges=[]
        for i in enumerate(msg.ranges):
            angle=msg.angle_min+i*msg.angle_increment
            angle=math.degrees(angle)
            if self.min_angle <= angle <= self.max_angle:
                selected_ranges.append(msg.ranges[i])

        #距离突变点作为悬崖
        cliff_points=[]
        for i in range(1, len(selected_ranges)):
            if abs(selected_ranges[i] - selected_ranges[i-1]) > self.cliff_threshold:  # 设置突变阈值
                cliff_points.append(i)

        #如果只有2个悬崖，说明中心在2个悬崖之间
        if len(cliff_points) ==2:
            angle_left = msg.angle_min + cliff_points[0] * msg.angle_increment
            angle_right = msg.angle_min + cliff_points[1] * msg.angle_increment
            self.error=angle_left+angle_right-2*math.pi
        #悬崖数小于2,扩大处理角度范围
        elif len(cliff_points) < 2:
            self.min_angle-=5.0
            self.max_angle+=5.0
        #悬崖数大于2,缩小处理角度范围
        elif len(cliff_points) > 2:
            self.min_angle+=5.0
            self.max_angle-=5.0

        correct=self.kp*self.error
        self.w_pub.publish(Float32(data=correct))

def main():
    rclpy.init()
    scan_node = ScanNode()
    try:
        rclpy.spin(scan_node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()
        scan_node.destroy_node()

if __name__ == '__main__':
    main()

