import zenoh
import json
import numpy as np
import cv2
from ultralytics import YOLO

# 1. Setup
model = YOLO('yolov8n.pt')
DOCKER_IP = "172.23.42.150"

def on_image_callback(sample):
    payload = sample.payload.to_bytes()
    # Assuming 640x480 RGB (Adjust if Step 1 output was different)
    h, w, c = 480, 640, 3
    expected_size = h * w * c

    if len(payload) >= expected_size:
        raw_pixels = payload[-expected_size:]
        img = np.frombuffer(raw_pixels, dtype=np.uint8).reshape((h, w, c))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        results = model(img, verbose=False)
        for result in results.boxes:
            label = model.names[int(result.cls)]
            conf = float(result.conf)
            if conf > 0.4:
                print(f"🎯 DETECTED: {label} ({conf:.2f})")
                # Publish to Ingestor
                session.put(f"bot/detections/{label}", json.dumps({"class": label, "confidence": conf}))

# 2. Force Connection to Docker
conf = zenoh.Config()
conf.insert_json5('connect/endpoints', f'["tcp/{DOCKER_IP}:7447"]')
session = zenoh.open(conf)

print(f"📡 Connected to Bridge at {DOCKER_IP}. Waiting for pixels...")
sub = session.declare_subscriber("rt/camera/image_raw", on_image_callback)

try:
    while True: import time; time.sleep(1)
except KeyboardInterrupt:
    session.close()
