import zenoh
import json
import psycopg2
from datetime import datetime

# Database connection settings
DB_CONFIG = {
    "dbname": "postgres",
    "user": "ruchikyajnik",
    "password": "your_password", # Replace with yours
    "host": "localhost"
}

def handle_detection(sample):
    try:
        # 1. Parse the JSON from Zenoh
        data = json.loads(sample.payload.decode('utf-8'))
        
        # 2. Extract fields
        ts_float = float(data['header']['timestamp'])
        dt_object = datetime.fromtimestamp(ts_float)
        
        obj_class = data['object']['class']
        conf = data['object']['confidence']
        x = data['robot_state']['pose']['x']
        y = data['robot_state']['pose']['y']
        yaw = data['robot_state']['pose']['yaw']

        # 3. Connect and Insert (Idempotent)
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO object_detections (event_timestamp, class_label, confidence, robot_x, robot_y, robot_yaw)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_timestamp, class_label) DO NOTHING;
        """
        
        cur.execute(insert_query, (dt_object, obj_class, conf, x, y, yaw))
        
        if cur.rowcount > 0:
            print(f"✅ Stored new detection: {obj_class} at {x:.2f}, {y:.2f}")
        else:
            print(f"⏭️  Duplicate ignored: {obj_class}")

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error processing Zenoh sample: {e}")

def main():
    conf = zenoh.Config()
    session = zenoh.open(conf)
    
    # Subscribe to all detections under the 'bot/detections/' hierarchy
    sub = session.declare_subscriber("bot/detections/**", handle_detection)
    
    print("📥 Ingest Worker is running. Listening for Zenoh events...")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Ingest Worker...")
    finally:
        session.close()

if __name__ == "__main__":
    main()
