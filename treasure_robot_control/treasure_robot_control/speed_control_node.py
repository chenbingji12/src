import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

class SpeedControlNode(Node):
    def __init__(self):
        super().__init__('speed_control_node')

        self.speed_publish=self.create_publisher(Twist,'cmd_vel',10)

        self.v_sub=self.create_subscription(Float32,'/line_follow/v_speed',self.v_callback,10)
        self.w_sub=self.create_subscription(Float32,'/line_follow/w_speed',self.w_callback,10)
        self.scan_w_sub=self.create_subscription(Float32,'/scan/w_speed',self.scan_w_callback,10)

        self.v=0.0
        self.w=0.0
        self.line_follow_w=0.0
        self.scan_w=0.0

        self.control_timer=self.create_timer(0.01,self.control_callback)

        self.i=0
        
        self.get_logger().info('小车速度控制节点启动成功')

    def v_callback(self,msg):
        self.v=msg.data

    def w_callback(self,msg):
        self.line_follow_w=msg.data

    def scan_w_callback(self,msg):
        self.scan_w=msg.data

    def control_callback(self):
        msg=Twist()
        self.w=self.line_follow_w+self.scan_w
        if self.w>0.8:
            self.w=0.8
        elif self.w<-0.8:
            self.w=-0.8
        msg.linear.x=self.v
        msg.angular.z=self.w
        self.speed_publish.publish(msg)

        # 打印发布速度指令,每100次打印一次
        self.i+=1
        if self.i>100:
            self.i=0
            self.get_logger().info(f'发布速度指令: {msg}')

def main():
    rclpy.init()
    node=SpeedControlNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop=Twist()
        node.speed_publish.publish(stop)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
