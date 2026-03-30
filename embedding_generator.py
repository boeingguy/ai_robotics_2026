import psycopg2
import numpy as np
from math import hypot

# Connection to isolated Port 5433
DB_CONFIG = "host=localhost port=5433 dbname=semantic_map user=robot password=robotics"

class EmbeddingGenerator:
    def __init__(self):
        self.conn = psycopg2.connect(DB_CONFIG)
        self.cur = self.conn.cursor()
        self.last_pose = (0.0, 0.0, 0.0) # (x, y, yaw)
        self.kf_count = 0

    def check_keyframe_gate(self, x, y, yaw):
        """Professor's Rule: Move > 0.5m OR Rotate > 15 degrees"""
        dist = hypot(x - self.last_pose, y - self.last_pose)
        angle_diff = abs(yaw - self.last_pose)
        
        if dist > 0.5 or angle_diff > 15.0:
            return True
        return False

    def process_detection(self, label, conf, x, y, yaw):
        if not self.check_keyframe_gate(x, y, yaw):
            return "Skipped: Gate not met"

        self.kf_count += 1
        self.last_pose = (x, y, yaw)
        det_id = f"run1_kf{self.kf_count}_{label}"
        
        # Simulate CLIP ViT-B/32 512-dim L2-normalized vector
        vec = np.random.rand(512)
        embedding = (vec / np.linalg.norm(vec)).tolist()

        self.cur.execute("""
            INSERT INTO detections (det_id, label, confidence, map_x, map_y, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (det_id) DO NOTHING
        """, (det_id, label, conf, x, y, embedding))
        self.conn.commit()
        return f"Inserted: {det_id}"

# Example Usage for Report:
gen = EmbeddingGenerator()
print(gen.process_detection("airport_bench", 0.92, 3.5, -1.0, 0.0))
