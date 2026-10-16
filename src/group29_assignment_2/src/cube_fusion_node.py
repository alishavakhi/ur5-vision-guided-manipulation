#!/usr/bin/env python3
from typing import Dict, Optional

import rclpy
from rclpy.node import Node
from rclpy.time import Time as RclTime

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String, Float32


class CubeFusionNode(Node):
    def __init__(self):
        super().__init__("cube_fusion_node")

        self.declare_parameter("tag.ids", [1, 10])

        self.declare_parameter("cube_a_topic", "/cube_a_pose")
        self.declare_parameter("cube_b_topic", "/cube_b_pose")

        self.declare_parameter("pose_timeout_sec", 0.6)
        self.declare_parameter("backup_hold_sec", 3.0)
        self.declare_parameter("publish_rate_hz", 10.0)

        self.declare_parameter("print_period_sec", 1.0)

        self.tag_ids = [int(x) for x in self.get_parameter("tag.ids").value]
        self.cube_a_id = self.tag_ids[0] if len(self.tag_ids) >= 1 else 1
        self.cube_b_id = self.tag_ids[1] if len(self.tag_ids) >= 2 else 10

        self.pose_timeout = float(self.get_parameter("pose_timeout_sec").value)
        self.backup_hold = float(self.get_parameter("backup_hold_sec").value)
        self.print_period = float(self.get_parameter("print_period_sec").value)

        self.pub_a = self.create_publisher(PoseStamped, str(self.get_parameter("cube_a_topic").value), 10)
        self.pub_b = self.create_publisher(PoseStamped, str(self.get_parameter("cube_b_topic").value), 10)

        self.last_pose: Dict[int, Optional[PoseStamped]] = {tid: None for tid in self.tag_ids}
        self.last_pose_time: Dict[int, Optional[RclTime]] = {tid: None for tid in self.tag_ids}

        self.last_color: Dict[int, str] = {tid: "Unknown" for tid in self.tag_ids}
        self.last_conf: Dict[int, float] = {tid: 0.0 for tid in self.tag_ids}
        self.last_rgb: Dict[int, str] = {tid: "(nan, nan, nan)" for tid in self.tag_ids}
        self.last_hsv: Dict[int, str] = {tid: "(nan, nan, nan)" for tid in self.tag_ids}

        for tid in self.tag_ids:
            self.create_subscription(PoseStamped, f"/tag_{tid}/pose_base", lambda m, t=tid: self.pose_cb(m, t), 10)
            self.create_subscription(String, f"/tag_{tid}/color", lambda m, t=tid: self.color_cb(m, t), 10)
            self.create_subscription(Float32, f"/tag_{tid}/color_conf", lambda m, t=tid: self.conf_cb(m, t), 10)
            self.create_subscription(String, f"/tag_{tid}/color_rgb", lambda m, t=tid: self.rgb_cb(m, t), 10)
            self.create_subscription(String, f"/tag_{tid}/color_hsv", lambda m, t=tid: self.hsv_cb(m, t), 10)

        rate = float(self.get_parameter("publish_rate_hz").value)
        self.create_timer(1.0 / max(1.0, rate), self.timer_cb)
        self.create_timer(self.print_period, self.print_timer_cb)

    def pose_cb(self, msg: PoseStamped, tid: int):
        self.last_pose[tid] = msg
        self.last_pose_time[tid] = RclTime.from_msg(msg.header.stamp)

    def color_cb(self, msg: String, tid: int):
        self.last_color[tid] = msg.data

    def conf_cb(self, msg: Float32, tid: int):
        self.last_conf[tid] = float(msg.data)

    def rgb_cb(self, msg: String, tid: int):
        self.last_rgb[tid] = msg.data

    def hsv_cb(self, msg: String, tid: int):
        self.last_hsv[tid] = msg.data

    def _age_sec(self, tid: int) -> float:
        if self.last_pose_time[tid] is None:
            return 1e9
        now = self.get_clock().now()
        return (now - self.last_pose_time[tid]).nanoseconds * 1e-9

    def _is_fresh(self, tid: int) -> bool:
        return self.last_pose[tid] is not None and self._age_sec(tid) <= self.pose_timeout

    def _in_backup_window(self, tid: int) -> bool:
        return self.last_pose[tid] is not None and self._age_sec(tid) <= self.backup_hold

    def timer_cb(self):
        if self._is_fresh(self.cube_a_id) or self._in_backup_window(self.cube_a_id):
            self.pub_a.publish(self.last_pose[self.cube_a_id])
        if self._is_fresh(self.cube_b_id) or self._in_backup_window(self.cube_b_id):
            self.pub_b.publish(self.last_pose[self.cube_b_id])

    def _format_pose_xyz(self, tid: int) -> str:
        p = self.last_pose.get(tid)
        if p is None:
            return "(nan,nan,nan)"
        return f"({p.pose.position.x:.3f},{p.pose.position.y:.3f},{p.pose.position.z:.3f})"

    def _print_one(self, tid: int):
        color = self.last_color.get(tid, "Unknown")
        conf = self.last_conf.get(tid, 0.0)
        rgb = self.last_rgb.get(tid, "(nan, nan, nan)")
        hsv = self.last_hsv.get(tid, "(nan, nan, nan)")
        pose_xyz = self._format_pose_xyz(tid)

        self.get_logger().info(
            f"ID {tid}: {color} (conf:{conf:.2f}) | RGB:{rgb} HSV:{hsv} | Pose:{pose_xyz}"
        )

    def print_timer_cb(self):
        self._print_one(self.cube_a_id)
        self._print_one(self.cube_b_id)


def main():
    rclpy.init()
    node = CubeFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
