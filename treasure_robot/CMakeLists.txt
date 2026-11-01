cmake_minimum_required(VERSION 3.8)
project(treasure_robot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf config launch rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/cmd_vel_odom_relay.py
  DESTINATION lib/${PROJECT_NAME}
)

install(FILES world/treasure_robot_world.sdf
  DESTINATION share/${PROJECT_NAME}/world
)

install(FILES
  world/meshes/speed_bump.obj
  world/meshes/speed_bump.mtl
  world/meshes/trapezoid_hill.obj
  world/meshes/trapezoid_hill.mtl
  DESTINATION share/${PROJECT_NAME}/world/meshes
)

install(FILES urdf/treasure_car_linkforge.urdf
  DESTINATION share/${PROJECT_NAME}/urdf
)

install(DIRECTORY urdf/meshes
  DESTINATION share/${PROJECT_NAME}/urdf
)

install(DIRECTORY world/meshes/whole_world
  DESTINATION share/${PROJECT_NAME}/world/meshes
)

ament_package()
