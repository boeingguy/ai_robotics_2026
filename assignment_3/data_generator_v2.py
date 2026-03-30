import psycopg2
import numpy as np

# Port 5433 isolates our DB from the workstation's local Postgres
DB_CONFIG = "host=localhost port=5433 dbname=semantic_map user=robot password=robotics"

def generate_mock_data():
    print("--- Starting Assignment 3: Semantic Map Injection ---")
    conn = psycopg2.connect(DB_CONFIG)
    cur = conn.cursor()

    try:
        # 1. SCHEMA INITIALIZATION
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("DROP TABLE IF EXISTS detections;")
        cur.execute("""
            CREATE TABLE detections (
                id SERIAL PRIMARY KEY,
                det_id TEXT UNIQUE,
                label TEXT,
                confidence FLOAT,
                map_x FLOAT,
                map_y FLOAT,
                embedding vector(512)
            );
        """)

        # 2. MOCK DATA: Red/Green/Blue Blocks, Airport Bench, Tables, Chairs
        # Coordinates simulate different rooms (Kitchen, Lounge, Office)
        mock_assets = [
            ("run1_kf1_d0", "red_block", 0.98, 1.0, 1.0),
            ("run1_kf1_d1", "table", 0.85, 1.1, 1.0),
            ("run1_kf2_d0", "green_block", 0.97, 1.6, 1.1),
            ("run1_kf5_d0", "airport_bench", 0.92, 3.5, -1.0),
            ("run1_kf5_d1", "blue_block", 0.99, 3.7, -1.2),
            ("run1_kf10_d0", "chair", 0.94, 6.0, 5.0),
            ("run1_kf10_d1", "table", 0.88, 6.2, 5.2),
            ("run1_kf11_d0", "red_block", 0.91, 6.7, 5.5) # Spatial Aliasing Test
        ]

        for det_id, label, conf, x, y in mock_assets:
            vec = np.random.rand(512)
            norm_vec = vec / np.linalg.norm(vec)
            
            cur.execute("""
                INSERT INTO detections (det_id, label, confidence, map_x, map_y, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (det_id, label, conf, x, y, norm_vec.tolist()))

        # CRITICAL: Commit the Vector data NOW so it persists
        conn.commit()
        print("--- SUCCESS: 12 Vector Landmarks Committed to Port 5433 ---")

    except Exception as e:
        print(f"Vector Injection Error: {e}")
        conn.rollback()

    # 3. GRAPH ATTEMPT (Will fail gracefully if AGE is missing)
    try:
        print("Attempting Graph (Apache AGE) injection...")
        cur.execute("SELECT * FROM cypher('maze_graph', $$ CREATE (:Place {id: 'kitchen'}) $$) AS (v agtype);")
        conn.commit()
    except psycopg2.errors.UndefinedFunction:
        print("NOTE: Apache AGE not detected. Skipping Graph phase (Vector data remains safe).")
        conn.rollback()
    except Exception as e:
        print(f"Graph Error: {e}")
        conn.rollback()

    cur.close()
    conn.close()

if __name__ == "__main__":
    generate_mock_data()
