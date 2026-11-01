#!/usr/bin/env python3
"""Expose standard /cmd_vel and /odom interfaces for diff_drive_controller."""

import rclpy
from geometry_msgs.msg import Twist, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy


class CmdVelOdomRelay(Node):
    """Bridge standard Twist/Odometry topics to controller-specific topics."""

    def __init__(self):
        super().__init__('cmd_vel_odom_relay')

        controller_qos = QoSProfile(depth=10)
        controller_qos.reliability = ReliabilityPolicy.BEST_EFFORT

        self.cmd_pub = self.create_publisher(
            TwistStamped, '/diff_drive_controller/cmd_vel', controller_qos
        )
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        self.create_subscription(Twist, '/cmd_vel', self.on_cmd_vel, 10)
        self.create_subscription(
            Odometry, '/diff_drive_controller/odom', self.on_odom, 10
        )

        self.get_logger().info(
            'Relaying /cmd_vel (Twist) -> /diff_drive_controller/cmd_vel '
            '(TwistStamped), and /diff_drive_controller/odom -> /odom'
        )

    def on_cmd_vel(self, msg: Twist):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = 'base_footprint'
        stamped.twist = msg
        self.cmd_pub.publish(stamped)

    def on_odom(self, msg: Odometry):
        self.odom_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelOdomRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
