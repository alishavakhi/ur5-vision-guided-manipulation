#!/usr/bin/env python3
import math
from typing import Optional, Tuple

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped, TransformStamped, PolygonStamped, Point32

from cv_bridge import CvBridge
import tf2_ros
import tf2_geometry_msgs

from dt_apriltags import Detector


def rotation_matrix_to_quaternion(R: np.ndarray) -> Tuple[float, float, float, float]:
    R = np.asarray(R, dtype=float)
    t = float(np.trace(R))

    if t > 0.0:
        S = math.sqrt(t + 1.0) * 2.0
        qw = 0.25 * S
        qx = (R[2, 1] - R[1, 2]) / S
        qy = (R[0, 2] - R[2, 0]) / S
        qz = (R[1, 0] - R[0, 1]) / S
    else:
        if (R[0, 0] > R[1, 1]) and (R[0, 0] > R[2, 2]):
            S = math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
            qw = (R[2, 1] - R[1, 2]) / S
            qx = 0.25 * S
            qy = (R[0, 1] + R[1, 0]) / S
            qz = (R[0, 2] + R[2, 0]) / S
        elif R[1, 1] > R[2, 2]:
            S = math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
            qw = (R[0, 2] - R[2, 0]) / S
            qx = (R[0, 1] + R[1, 0]) / S
            qy = 0.25 * S
            qz = (R[1, 2] + R[2, 1]) / S
        else:
            S = math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
            qw = (R[1, 0] - R[0, 1]) / S
            qx = (R[0, 2] + R[2, 0]) / S
            qy = (R[1, 2] + R[2, 1]) / S
            qz = 0.25 * S

    n = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
    if n < 1e-12:
        return 0.0, 0.0, 0.0, 1.0
    return qx / n, qy / n, qz / n, qw / n


class TagDetectorNode(Node):
    def __init__(self):
        super().__init__("tag_detector_node")

        self.declare_parameter("family", "36h11")
        self.declare_parameter("size", 0.05)
        self.declare_parameter("max_hamming", 0)

        self.declare_parameter("detector.threads", 4)
        self.declare_parameter("detector.decimate", 2.0)
        self.declare_parameter("detector.blur", 0.0)
        self.declare_parameter("detector.refine", True)
        self.declare_parameter("detector.sharpening", 0.25)
        self.declare_parameter("detector.debug", False)
        self.declare_parameter("detector.publish_tf", True)

        self.declare_parameter("tag.ids", [1, 10])

        self.declare_parameter("camera_info_topic", "/rgb_camera/camera_info")
        self.declare_parameter("image_topic", "/rgb_camera/image")
        self.declare_parameter("camera_frame", "")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("z_offset", 0.03)
        self.declare_parameter("tag_frame_prefix", "tag_")

        fam = str(self.get_parameter("family").value)
        self.tag_family = fam if fam.startswith("tag") else ("tag" + fam)
        self.tag_size = float(self.get_parameter("size").value)
        self.max_hamming = int(self.get_parameter("max_hamming").value)

        threads = int(self.get_parameter("detector.threads").value)
        decimate = float(self.get_parameter("detector.decimate").value)
        blur = float(self.get_parameter("detector.blur").value)
        refine = bool(self.get_parameter("detector.refine").value)
        sharpening = float(self.get_parameter("detector.sharpening").value)
        debug = bool(self.get_parameter("detector.debug").value)
        self.publish_tf = bool(self.get_parameter("detector.publish_tf").value)

        self.tag_ids = [int(x) for x in self.get_parameter("tag.ids").value]
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.z_offset = float(self.get_parameter("z_offset").value)
        self.tag_frame_prefix = str(self.get_parameter("tag_frame_prefix").value)

        self.bridge = CvBridge()
        self.detector = Detector(
            families=self.tag_family,
            nthreads=threads,
            quad_decimate=decimate,
            quad_sigma=blur,
            refine_edges=refine,
            decode_sharpening=sharpening,
            debug=debug,
        )

        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=5.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.cam_params: Optional[Tuple[float, float, float, float]] = None

        self.pub_pose = {
            tid: self.create_publisher(PoseStamped, f"/tag_{tid}/pose_base", 10) for tid in self.tag_ids
        }
        self.pub_corners = {
            tid: self.create_publisher(PolygonStamped, f"/tag_{tid}/corners", 10) for tid in self.tag_ids
        }

        self.create_subscription(
            CameraInfo,
            str(self.get_parameter("camera_info_topic").value),
            self.info_cb,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Image,
            str(self.get_parameter("image_topic").value),
            self.image_cb,
            qos_profile_sensor_data,
        )

    def info_cb(self, msg: CameraInfo):
        fx, fy, cx, cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]
        if fx == 0.0 or fy == 0.0:
            return
        self.cam_params = (fx, fy, cx, cy)

    def _lookup_transform(self, source_frame: str, stamp_time: rclpy.time.Time) -> Optional[TransformStamped]:
        try:
            return self.tf_buffer.lookup_transform(
                self.base_frame, source_frame, stamp_time, timeout=Duration(seconds=0.2)
            )
        except Exception:
            try:
                return self.tf_buffer.lookup_transform(
                    self.base_frame, source_frame, rclpy.time.Time(), timeout=Duration(seconds=0.2)
                )
            except Exception:
                return None

    def _broadcast_tag_tf(self, parent_frame: str, stamp_msg, tag_id: int,
                          x: float, y: float, z: float,
                          qx: float, qy: float, qz: float, qw: float):
        if not self.publish_tf:
            return
        t = TransformStamped()
        t.header.frame_id = parent_frame
        t.header.stamp = stamp_msg
        t.child_frame_id = f"{self.tag_frame_prefix}{tag_id}"
        t.transform.translation.x = float(x)
        t.transform.translation.y = float(y)
        t.transform.translation.z = float(z)
        t.transform.rotation.x = float(qx)
        t.transform.rotation.y = float(qy)
        t.transform.rotation.z = float(qz)
        t.transform.rotation.w = float(qw)
        self.tf_broadcaster.sendTransform(t)

    def _do_transform_pose_robust(self, pose_stamped: PoseStamped, tf: TransformStamped):
        try:
            if hasattr(tf2_geometry_msgs, "do_transform_pose_stamped"):
                ps_out = tf2_geometry_msgs.do_transform_pose_stamped(pose_stamped, tf)
                return ps_out.pose
            return tf2_geometry_msgs.do_transform_pose(pose_stamped.pose, tf)
        except Exception:
            return None

    def image_cb(self, msg: Image):
        if self.cam_params is None:
            return

        try:
            bgr = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception:
            return

        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        try:
            tags = self.detector.detect(
                gray,
                estimate_tag_pose=True,
                camera_params=self.cam_params,
                tag_size=self.tag_size,
            )
        except Exception:
            return

        if not tags:
            return

        source_frame = msg.header.frame_id if msg.header.frame_id else str(self.get_parameter("camera_frame").value)
        if not source_frame:
            return

        stamp_time = rclpy.time.Time.from_msg(msg.header.stamp)
        tf_cam_to_base = self._lookup_transform(source_frame, stamp_time)
        if tf_cam_to_base is None:
            return

        for tag in tags:
            tid = int(tag.tag_id)
            if tid not in self.tag_ids:
                continue

            try:
                if int(tag.hamming) > self.max_hamming:
                    continue
            except Exception:
                pass

            corners = np.array(tag.corners, dtype=np.float32)

            poly = PolygonStamped()
            poly.header = msg.header
            poly.header.frame_id = source_frame
            poly.polygon.points = [
                Point32(x=float(corners[i, 0]), y=float(corners[i, 1]), z=0.0) for i in range(4)
            ]
            self.pub_corners[tid].publish(poly)

            p = PoseStamped()
            p.header = msg.header
            p.header.frame_id = source_frame

            p.pose.position.x = float(tag.pose_t[0][0])
            p.pose.position.y = float(tag.pose_t[1][0])
            p.pose.position.z = float(tag.pose_t[2][0]) 

            try:
                qx, qy, qz, qw = rotation_matrix_to_quaternion(tag.pose_R)
            except Exception:
                qx, qy, qz, qw = 0.0, 0.0, 0.0, 1.0

            p.pose.orientation.x = qx
            p.pose.orientation.y = qy
            p.pose.orientation.z = qz
            p.pose.orientation.w = qw

            self._broadcast_tag_tf(
                parent_frame=source_frame,
                stamp_msg=msg.header.stamp,
                tag_id=tid,
                x=p.pose.position.x, y=p.pose.position.y, z=p.pose.position.z,
                qx=qx, qy=qy, qz=qz, qw=qw,
            )

            base_pose = self._do_transform_pose_robust(p, tf_cam_to_base)
            if base_pose is None:
                continue

            out = PoseStamped()
            out.header.frame_id = self.base_frame
            out.header.stamp = msg.header.stamp
            out.pose = base_pose
            self.pub_pose[tid].publish(out)


def main():
    rclpy.init()
    node = TagDetectorNode()
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
