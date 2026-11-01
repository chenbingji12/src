# treasure_robot

ROS 2 Jazzy + Gazebo Sim package for the Bellator N176 treasure-hunting robot.

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select treasure_robot
source install/setup.bash
```

## View the model in RViz2

```bash
ros2 launch treasure_robot view_car.launch.py
```

Use the sliders in `joint_state_publisher_gui` to rotate the four wheels.
The fixed frame is `base_footprint`.

## Run Gazebo with ros2_control

```bash
ros2 launch treasure_robot sim.launch.py
```

The world contains:

- a static 10 m x 7 m green platform with its top at `z = 0.1 m`;
- the speed bump at `(1.2, 0, 0.1)`;
- the trapezoid stair hill at `(2.4, 0, 0.1)`;
- the car spawned at `(0, 0, 0.1)`.

## Drive the car

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# Stop
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Useful checks:

```bash
ros2 control list_controllers
ros2 topic echo /odom
ros2 topic echo /joint_states
ros2 run tf2_tools view_frames
```

## Interfaces

- Input: `/cmd_vel` (`geometry_msgs/msg/Twist`)
- Output: `/odom`, `/joint_states`, `/tf`, `/imu/data`
- `scripts/cmd_vel_odom_relay.py` maps the standard `/cmd_vel` and `/odom`
  interfaces to the controller-specific topics used by Jazzy.
- Frames: `odom -> base_footprint -> base_link -> car_body -> wheels`
- Wheel joints:
  - `left_front_wheel_joint`
  - `left_rear_wheel_joint`
  - `right_front_wheel_joint`
  - `right_rear_wheel_joint`

## Moving to a real robot

The simulation uses `gz_ros2_control/GazeboSimSystem`. For hardware, replace
only the `<hardware>` plugin in `urdf/treasure_car_ros2_control.xacro` with a
real `hardware_interface::SystemInterface` plugin. Keep the joint names,
controller YAML, frame names, and topics unchanged. A* path planning, OpenCV
vision, and navigation nodes then keep using the same ROS 2 interfaces.

## Layout

```text
urdf/     robot description and ros2_control interfaces
config/   controller_manager and diff_drive_controller parameters
launch/   sim.launch.py and view_car.launch.py
rviz/     RobotModel display configuration
world/    Gazebo world, OBJ meshes, and Blender source files
backup/   original LinkForge files before this configuration change
```
