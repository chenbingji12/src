"""Bring up the treasure robot in Gazebo and start its ros2_control stack."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('treasure_robot')
    urdf_file = os.path.join(pkg_share, 'urdf', 'treasure_car_linkforge.urdf')
    world_file = os.path.join(pkg_share, 'world', 'treasure_robot_world.sdf')
    controllers_file = os.path.join(pkg_share, 'config', 'controllers.yaml')
    rviz_file = os.path.join(pkg_share, 'rviz', 'treasure_car.rviz')

    robot_description = Command(['cat ', urdf_file])
    # ros_gz_sim captures these values when building its launch description.
    os.environ['GZ_SIM_RESOURCE_PATH'] = os.pathsep.join([
        os.path.dirname(pkg_share),
        pkg_share,
        os.path.join(pkg_share, 'world'),
        os.environ.get('GZ_SIM_RESOURCE_PATH', ''),
    ])
    os.environ['GZ_SIM_SYSTEM_PLUGIN_PATH'] = os.pathsep.join([
        '/opt/ros/jazzy/lib',
        os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', ''),
    ])


    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            )
        ),
        launch_arguments={'gz_args': ['-r -v 1 ', world_file]}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(robot_description, value_type=str),
            'use_sim_time': True,
        }],
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'treasure_car',
            '-x', '0.0', '-y', '0.0', '-z', '0.25',
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_controller',
            '--controller-manager', '/controller_manager',
            '--param-file', controllers_file,
        ],
        output='screen',
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    imu_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU'],
        remappings=[('/imu/data', '/imu/data')],
        output='screen',
    )

    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
        ],
        output='screen',
    )

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        output='screen',
    )

    cmd_vel_odom_relay = Node(
        package='treasure_robot',
        executable='cmd_vel_odom_relay.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.pathsep.join([
                os.path.dirname(pkg_share),
                pkg_share,
                os.path.join(pkg_share, 'world'),
                os.environ.get('GZ_SIM_RESOURCE_PATH', ''),
            ]),
        ),
        SetEnvironmentVariable(
            'GZ_SIM_SYSTEM_PLUGIN_PATH',
            os.pathsep.join([
                '/opt/ros/jazzy/lib',
                os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', ''),
            ]),
        ),
        gz_sim,
        robot_state_publisher,
        clock_bridge,
        spawn_robot,
        RegisterEventHandler(
            OnProcessExit(target_action=spawn_robot, on_exit=[joint_state_broadcaster_spawner])
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_spawner],
            )
        ),
        imu_bridge,
        camera_bridge,
        scan_bridge,
        cmd_vel_odom_relay,
        rviz,
    ])
