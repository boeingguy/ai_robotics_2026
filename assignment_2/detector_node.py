#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import zenoh, json, uuid, time
import numpy as np

class DetectorNode(Node):
    def __init__(self):
        super().__init__('detector_node')
        self.robot_id = "tb3_sim"
        self.run_id = str(uuid.uuid4())
        
        # Zenoh Setup
        self.zenoh_session = zenoh.open()
        self.pub = self.zenoh_session.declare_publisher(f"maze/{self.robot_id}/{self.run_id}/detections/v1/*")
        
        self.get_logger().info(f"Detector initialized for Run: {self.run_id}")
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.sequence = 0

    def timer_callback(self):
        self.sequence += 1
        event_id = str(uuid.uuid4())
        
        # Mocking detection of assets
        # coke_can -> bottle (39), plastic_cup -> cup (41), red_box -> suitcase (28)
        detections = [
            {"det_id": str(uuid.uuid4()), "class_id": 39, "class_name": "bottle", "confidence": 0.95, "bbox_xyxy": [120, 300, 180, 450]},
            {"det_id": str(uuid.uuid4()), "class_id": 41, "class_name": "cup", "confidence": 0.88, "bbox_xyxy": [250, 310, 300, 400]}
        ]

        payload = {
            "schema": "maze.detection.v1",
            "event_id": event_id,
            "run_id": self.run_id,
            "robot_id": self.robot_id,
            "sequence": self.sequence,
            "image": {
                "topic": "/camera/image_raw",
                "stamp": {"sec": int(time.time()), "nanosec": 0},
                "frame_id": "camera_link",
                "width": 640, "height": 480, "encoding": "rgb8",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            },
            "odometry": {"x": 1.5, "y": -2.0, "yaw": 0.0, "vx": 0.1, "vy": 0.0, "wz": 0.01},
            "tf": {
                "base_frame": "base_footprint",
                "camera_frame": "camera_link",
                "t_base_camera": list(np.eye(4).flatten()),
                "tf_ok": True
            },
            "detections": detections
        }

        key = f"maze/{self.robot_id}/{self.run_id}/detections/v1/{event_id}"
        self.zenoh_session.put(key, json.dumps(payload))
        self.get_logger().info(f"Published event {self.sequence}")

def main():
    rclpy.init()
    node = DetectorNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
