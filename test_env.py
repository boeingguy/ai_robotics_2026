import sys
import rclpy
from rclpy.node import Node
import ultralytics
import zenoh
import cv2
import numpy as np

def verify_environment():
    print("\n" + "="*40)
    print("--- ROS 2 JAZZY ENVIRONMENT CHECK ---")
    print("="*40)
    
    # 1. System Info
    print(f"Python Version: {sys.version.split()}")
    
    # 2. Test ROS 2 Jazzy (rclpy)
    try:
        if not rclpy.ok():
            rclpy.init()
        node = Node('env_test_node')
        print(f"✅ ROS 2 Jazzy: Accessible")
        node.destroy_node()
    except Exception as e:
        print(f"❌ ROS 2 Error: {e}")

    # 3. Test Ultralytics YOLO
    try:
        print(f"✅ YOLO Version: {ultralytics.__version__}")
    except ImportError:
        print("❌ YOLO Error: 'ultralytics' not found in .venv.")

    # 4. Test Zenoh (Amended for Zenoh 1.0.0 API)
    try:
        # Zenoh now requires a Config object passed to open()
        conf = zenoh.Config()
        z_session = zenoh.open(conf)
        print(f"✅ Zenoh API: Session opened successfully")
        z_session.close()
    except Exception as e:
        print(f"❌ Zenoh Error: {e}")

    # 5. Test OpenCV & NumPy Compatibility
    try:
        print(f"✅ OpenCV Version: {cv2.__version__}")
        print(f"✅ NumPy Version: {np.__version__}")
        
        # Critical check for ROS 2 Jazzy / cv_bridge
        if np.__version__.startswith('2.'):
            print("⚠️  Warning: NumPy 2.x detected. ROS 2 Jazzy's 'cv_bridge' may crash.")
            print("   Fix: pip install 'numpy<2.0.0'")
        else:
            print("✅ NumPy Compatibility: Version 1.x is safe for cv_bridge.")
            
    except Exception as e:
        print(f"❌ Vision Library Error: {e}")

    print("="*40 + "\n")

if __name__ == "__main__":
    verify_environment()
