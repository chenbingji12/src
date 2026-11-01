"""Start the real-robot line-following vision and chassis control nodes."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    line_follow_node = Node(
        package='treasure_robot_sensor',
        executable='line_follow_node',
        output='screen',
    )

    speed_control_node = Node(
        package='treasure_robot_control',
        executable='speed_control_node',
        output='screen',
    )

    return LaunchDescription([
        line_follow_node,
        speed_control_node,
    ])
