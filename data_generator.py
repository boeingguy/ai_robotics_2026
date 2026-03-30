import psycopg2
import json
import random
import numpy as np

# Connection to your robotics_db (Host mode)
DB_CONFIG = "host=localhost port=5433 dbname=semantic_map user=robot password=robotics"

def generate_mock_data():
    conn = psycopg2.connect(DB_CONFIG)
    cur = conn.cursor()
    
    # Define some "Places" and "Objects" for our maze
    places = [
        {"name": "Kitchen", "x": 1.0, "y": 1.0},
        {"name": "Hallway", "x": 4.0, "y": 1.0},
        {"name": "Lab", "x": 7.0, "y": 1.0}
    ]
    
    objects = [
        {"label": "cup", "place": "Kitchen", "offset": 0.2},
        {"label": "chair", "place": "Kitchen", "offset": -0.3},
        {"label": "fire_extinguisher", "place": "Hallway", "offset": 0.1},
        {"label": "laptop", "place": "Lab", "offset": 0.5}
    ]

    print("--- Starting Mock Data Injection ---")

    # 1. Clear existing data for a clean test
    cur.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id SERIAL PRIMARY KEY,
        label TEXT,
        confidence FLOAT,
        embedding vector(512)
    );
""")
    cur.execute("TRUNCATE detections RESTART IDENTITY;")
    
    # 2. Inject Detections with "Fake" CLIP Embeddings (512-D)
    for obj in objects:
        for i in range(3):  # Simulate seeing each object 3 times from different angles
            # Generate a "near-identical" vector for the same object class
            base_vector = np.zeros(512)
            base_vector[objects.index(obj)] = 1.0 # Unique signature per class
            noise = np.random.normal(0, 0.05, 512)
            embedding = (base_vector + noise).tolist()
            
            cur.execute(
                "INSERT INTO detections (label, confidence, embedding) VALUES (%s, %s, %s)",
                (obj['label'], 0.95 - (i * 0.02), embedding)
            )
    
    conn.commit()
    print(f"Successfully injected {len(objects) * 3} detections into PostgreSQL.")

    # 3. Inject Graph Nodes into Apache AGE
    # We use Cypher to link these together
    for p in places:
        cur.execute(f"""
            SELECT * FROM cypher('maze_graph', $$
                CREATE (:Place {{name: '{p['name']}', x: {p['x']}, y: {p['y']}}})
            $$) as (v agtype);
        """)
    
    # Linking Objects to Places in the Graph
    # This fulfills the "Object -> Place" edge requirement of the assignment
    for obj in objects:
        cur.execute(f"""
            SELECT * FROM cypher('maze_graph', $$
                MATCH (p:Place {{name: '{obj['place']}'}})
                CREATE (o:Object {{label: '{obj['label']}'}})-[:LOCATED_IN]->(p)
            $$) as (v agtype);
        """)

    conn.commit()
    cur.close()
    conn.close()
    print("--- Graph Nodes and Edges Created ---")

if __name__ == "__main__":
    generate_mock_data()
