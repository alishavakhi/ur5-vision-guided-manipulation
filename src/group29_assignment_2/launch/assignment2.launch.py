from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource, AnyLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    manipulation_node = Node(
        package="group29_assignment_2",
        executable="manipulation_node",
        name="manipulation_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    tag_detector_node = Node(
        package="group29_assignment_2",
        executable="tag_detector_node.py",
        name="tag_detector_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    color_detector_node = Node(
        package="group29_assignment_2",
        executable="color_detector_node.py",
        name="color_detector_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    cube_fusion_node = Node(
        package="group29_assignment_2",
        executable="cube_fusion_node.py",
        name="cube_fusion_node",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    prof_pkg_share = get_package_share_directory("ir_launch")

    prof_launch_path = os.path.join(
        prof_pkg_share,
        "launch",
        "assignment_2.launch.py"
    )

    prof_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(prof_launch_path),
        launch_arguments={
            "use_sim_time": "true",
        }.items(),
    )

    return LaunchDescription([
        prof_launch,
        tag_detector_node,
        color_detector_node,
        cube_fusion_node,
        TimerAction(period=2.0, actions=[manipulation_node]),
    ])
