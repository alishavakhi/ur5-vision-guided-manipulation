#!/usr/bin/env python3
import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from geometry_msgs.msg import PolygonStamped
from std_msgs.msg import String, Float32
from cv_bridge import CvBridge


@dataclass
class ColorDetectorConfig:
    roi_expand: float = 0.7
    band_inner_px: int = 6
    band_outer_px: int = 25

    min_pixels: int = 60
    hsv_s_min: int = 10
    hsv_v_min: int = 0
    hsv_v_max: int = 255

    neutral_s_max: float = 35.0
    black_v_max: float = 70.0
    white_v_min: float = 185.0


class ColorDetector:
    def __init__(self, cfg: Optional[ColorDetectorConfig] = None):
        self.cfg = cfg if cfg is not None else ColorDetectorConfig()

    def roi_from_corners(self, bgr_img: np.ndarray, corners_xy: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        if bgr_img is None or corners_xy is None or len(corners_xy) < 4:
            return None, None

        h_img, w_img = bgr_img.shape[:2]
        corners_xy = np.asarray(corners_xy, dtype=np.float32)

        xs = corners_xy[:, 0]
        ys = corners_xy[:, 1]
        x0, x1 = float(xs.min()), float(xs.max())
        y0, y1 = float(ys.min()), float(ys.max())

        bw = max(1.0, x1 - x0)
        bh = max(1.0, y1 - y0)
        pad_x = self.cfg.roi_expand * bw
        pad_y = self.cfg.roi_expand * bh

        rx0 = int(max(0, math.floor(x0 - pad_x)))
        ry0 = int(max(0, math.floor(y0 - pad_y)))
        rx1 = int(min(w_img, math.ceil(x1 + pad_x)))
        ry1 = int(min(h_img, math.ceil(y1 + pad_y)))

        if rx1 <= rx0 or ry1 <= ry0:
            return None, None

        roi = bgr_img[ry0:ry1, rx0:rx1].copy()
        corners_roi = corners_xy.copy()
        corners_roi[:, 0] -= rx0
        corners_roi[:, 1] -= ry0
        return roi, corners_roi

    def band_mask(self, h: int, w: int, corners_roi: np.ndarray) -> np.ndarray:
        base = np.zeros((h, w), dtype=np.uint8)
        poly = corners_roi.astype(np.int32)
        cv2.fillConvexPoly(base, poly, 255)

        inner_k = max(1, int(self.cfg.band_inner_px))
        outer_k = max(inner_k + 1, int(self.cfg.band_outer_px))

        kernel_in = np.ones((inner_k, inner_k), np.uint8)
        kernel_out = np.ones((outer_k, outer_k), np.uint8)

        inner = cv2.dilate(base, kernel_in, iterations=1)
        outer = cv2.dilate(base, kernel_out, iterations=1)

        return cv2.bitwise_and(outer, cv2.bitwise_not(inner))

    @staticmethod
    def classify_hue(h: float) -> str:
        if (h <= 10) or (h >= 170):
            return "red"
        if 11 <= h <= 25:
            return "orange"
        if 26 <= h <= 35:
            return "yellow"
        if 36 <= h <= 85:
            return "green"
        if 86 <= h <= 135:
            return "blue"
        if 136 <= h <= 169:
            return "purple"
        return "unknown"

    def detect(self, roi_bgr: np.ndarray, corners_roi: np.ndarray) -> Tuple[str, Tuple[float, float, float], Tuple[float, float, float], float]:
        if roi_bgr is None or corners_roi is None or roi_bgr.size == 0:
            nan = float("nan")
            return "Unknown", (nan, nan, nan), (nan, nan, nan), 0.0

        h, w = roi_bgr.shape[:2]
        mask = self.band_mask(h, w, corners_roi)

        hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
        H = hsv[:, :, 0]
        S = hsv[:, :, 1]
        V = hsv[:, :, 2]

        valid0 = (mask == 255) & (V >= self.cfg.hsv_v_min) & (V <= self.cfg.hsv_v_max)
        n0 = int(np.count_nonzero(valid0))
        if n0 < self.cfg.min_pixels:
            nan = float("nan")
            return "Unknown", (nan, nan, nan), (nan, nan, nan), 0.0

        H0 = H[valid0].astype(np.uint8)
        S0 = S[valid0].astype(np.float32)
        V0 = V[valid0].astype(np.float32)

        h_mean0 = float(np.mean(H0))
        s_mean0 = float(np.mean(S0))
        v_mean0 = float(np.mean(V0))

        bgr0 = roi_bgr[valid0].astype(np.float32)
        b_mean, g_mean, r_mean = np.mean(bgr0, axis=0).tolist()
        rgb = (float(r_mean), float(g_mean), float(b_mean))
        hsv_mean = (float(h_mean0), float(s_mean0), float(v_mean0))

        if s_mean0 < self.cfg.neutral_s_max:
            if v_mean0 < self.cfg.black_v_max:
                return "black", rgb, hsv_mean, 1.0
            if v_mean0 > self.cfg.white_v_min:
                return "white", rgb, hsv_mean, 1.0
            return "gray", rgb, hsv_mean, 1.0

        valid = valid0 & (S >= self.cfg.hsv_s_min)
        n = int(np.count_nonzero(valid))
        if n < self.cfg.min_pixels:
            valid = valid0

        Hs = H[valid].astype(np.uint8)
        hist = np.bincount(Hs, minlength=180).astype(np.float32)
        peak = int(np.argmax(hist))
        conf = float(hist[peak] / max(1.0, float(hist.sum())))

        name = self.classify_hue(float(np.mean(Hs)))
        return name, rgb, hsv_mean, conf


class ColorDetectorNode(Node):
    def __init__(self):
        super().__init__("color_detector_node")

        self.declare_parameter("image_topic", "/rgb_camera/image")
        self.declare_parameter("tag.ids", [1, 10])
        self.declare_parameter("corners_topic_prefix", "/tag_")

        self.declare_parameter("roi_expand", 0.7)
        self.declare_parameter("band_inner_px", 6)
        self.declare_parameter("band_outer_px", 25)

        self.declare_parameter("min_pixels", 60)
        self.declare_parameter("hsv_s_min", 10)
        self.declare_parameter("hsv_v_min", 0)
        self.declare_parameter("hsv_v_max", 255)

        self.declare_parameter("neutral_s_max", 35.0)
        self.declare_parameter("black_v_max", 70.0)
        self.declare_parameter("white_v_min", 185.0)

        self.tag_ids = [int(x) for x in self.get_parameter("tag.ids").value]
        self.corners_topic_prefix = str(self.get_parameter("corners_topic_prefix").value)

        cfg = ColorDetectorConfig(
            roi_expand=float(self.get_parameter("roi_expand").value),
            band_inner_px=int(self.get_parameter("band_inner_px").value),
            band_outer_px=int(self.get_parameter("band_outer_px").value),
            min_pixels=int(self.get_parameter("min_pixels").value),
            hsv_s_min=int(self.get_parameter("hsv_s_min").value),
            hsv_v_min=int(self.get_parameter("hsv_v_min").value),
            hsv_v_max=int(self.get_parameter("hsv_v_max").value),
            neutral_s_max=float(self.get_parameter("neutral_s_max").value),
            black_v_max=float(self.get_parameter("black_v_max").value),
            white_v_min=float(self.get_parameter("white_v_min").value),
        )

        self.detector = ColorDetector(cfg)
        self.bridge = CvBridge()

        self.latest_bgr: Optional[np.ndarray] = None
        self.latest_corners: Dict[int, Optional[np.ndarray]] = {tid: None for tid in self.tag_ids}

        self.pub_color = {tid: self.create_publisher(String, f"/tag_{tid}/color", 10) for tid in self.tag_ids}
        self.pub_conf = {tid: self.create_publisher(Float32, f"/tag_{tid}/color_conf", 10) for tid in self.tag_ids}
        self.pub_rgb = {tid: self.create_publisher(String, f"/tag_{tid}/color_rgb", 10) for tid in self.tag_ids}
        self.pub_hsv = {tid: self.create_publisher(String, f"/tag_{tid}/color_hsv", 10) for tid in self.tag_ids}

        self.create_subscription(
            Image,
            str(self.get_parameter("image_topic").value),
            self.image_cb,
            qos_profile_sensor_data,
        )

        for tid in self.tag_ids:
            self.create_subscription(
                PolygonStamped,
                f"{self.corners_topic_prefix}{tid}/corners",
                lambda msg, t=tid: self.corners_cb(msg, t),
                10,
            )

    def corners_cb(self, msg: PolygonStamped, tid: int):
        if len(msg.polygon.points) < 4:
            return
        pts = np.array([[p.x, p.y] for p in msg.polygon.points[:4]], dtype=np.float32)
        self.latest_corners[tid] = pts

    def image_cb(self, msg: Image):
        try:
            self.latest_bgr = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception:
            return

        bgr = self.latest_bgr
        if bgr is None:
            return

        for tid, corners in self.latest_corners.items():
            if corners is None:
                continue

            roi, corners_roi = self.detector.roi_from_corners(bgr, corners)
            name, rgb_f, hsv_f, conf = self.detector.detect(roi, corners_roi)

            s = String()
            s.data = name

            c = Float32()
            c.data = float(conf)

            rgb_s = String()
            hsv_s = String()

            if name == "Unknown":
                rgb_s.data = "(nan, nan, nan)"
                hsv_s.data = "(nan, nan, nan)"
            else:
                rgb_s.data = f"({int(round(rgb_f[0]))}, {int(round(rgb_f[1]))}, {int(round(rgb_f[2]))})"
                hsv_s.data = f"({int(round(hsv_f[0]))}, {int(round(hsv_f[1]))}, {int(round(hsv_f[2]))})"

            self.pub_color[tid].publish(s)
            self.pub_conf[tid].publish(c)
            self.pub_rgb[tid].publish(rgb_s)
            self.pub_hsv[tid].publish(hsv_s)


def main():
    rclpy.init()
    node = ColorDetectorNode()
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
