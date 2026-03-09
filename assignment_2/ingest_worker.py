import zenoh, json, psycopg2, time

DB_PARAMS = "dbname=postgres user=postgres password=postgres host=localhost"

def handle_detection(sample):
    try:
        data = json.loads(sample.payload.decode('utf-8'))
        conn = psycopg2.connect(DB_PARAMS)
        cur = conn.cursor()
        
        # Insert Event (Idempotent)
        cur.execute("""
            INSERT INTO detection_events (event_id, run_id, robot_id, sequence, stamp, x, y, yaw, raw_event)
            VALUES (%s, %s, %s, %s, to_timestamp(%s), %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING;
        """, (data['event_id'], data['run_id'], data['robot_id'], data['sequence'], 
              data['image']['stamp']['sec'], data['odometry']['x'], data['odometry']['y'], 
              data['odometry']['yaw'], json.dumps(data)))

        # Insert Detections
        for d in data['detections']:
            cur.execute("""
                INSERT INTO detections (event_id, det_id, class_name, confidence, x1, y1, x2, y2)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (event_id, det_id) DO NOTHING;
            """, (data['event_id'], d['det_id'], d['class_name'], d['confidence'], 
                  d['bbox_xyxy'][0], d['bbox_xyxy'][1], d['bbox_xyxy'][2], d['bbox_xyxy'][3]))
            
        conn.commit()
        print(f"Ingested event: {data['sequence']}")
    except Exception as e:
        print(f"Ingest Error: {e}")
    finally:
        if 'conn' in locals(): conn.close()

session = zenoh.open()
sub = session.declare_subscriber("maze/**/detections/v1/*", handle_detection)
print("Ingest Worker listening on maze/**/detections/v1/* ...")
while True: time.sleep(1)
