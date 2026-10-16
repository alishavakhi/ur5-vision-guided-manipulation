cmake_minimum_required(VERSION 3.8)
project(group29_assignment_2)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(control_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

# -------- C++ nodes --------
add_executable(manipulation_node src/manipulation_node.cpp)

target_include_directories(manipulation_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
)

target_compile_features(manipulation_node PUBLIC c_std_99 cxx_std_17)

ament_target_dependencies(manipulation_node
  rclcpp
  moveit_ros_planning_interface
  geometry_msgs
  rclcpp_action
  control_msgs
  tf2
  tf2_geometry_msgs
)

install(TARGETS manipulation_node
  DESTINATION lib/${PROJECT_NAME}
)

# -------- Python nodes --------
install(PROGRAMS
  src/tag_detector_node.py
  src/color_detector_node.py
  src/cube_fusion_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY cfg
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
