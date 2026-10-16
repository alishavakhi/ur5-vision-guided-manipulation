cmake_minimum_required(VERSION 3.22)
project(ir_movit_config)

find_package(ament_cmake REQUIRED)

find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)



ament_package()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launch")
  install(
    DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
    PATTERN "setup_assistant.launch" EXCLUDE)
endif()

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})

# Install the config folder
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)


add_executable(short_joint_state_publisher src/short_joint_state_publisher.cpp)
ament_target_dependencies(short_joint_state_publisher rclcpp sensor_msgs)

install(TARGETS
  short_joint_state_publisher
  DESTINATION lib/${PROJECT_NAME}
)


