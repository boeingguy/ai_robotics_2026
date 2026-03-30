# Assignment 3: Semantic Mapping & Re-Localization
**Student:** Ruchik Yajnik  
**System:** TurtleBot 4 (Gazebo) + ROS 2 + Zenoh + PostgreSQL (pgvector) + Apache AGE  

---

## 1. System Architecture & Schema

The implementation uses a hybrid data strategy. High-dimensional visual features are stored in a vector database, while topological and semantic relationships are managed via a knowledge graph.

### A. Vector Schema (pgvector)
Used for "Zero-Shot" visual landmark recognition via CLIP ViT-B/32.

```sql
-- Location: PostgreSQL (Port 5433)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE detections (
    id SERIAL PRIMARY KEY,
    det_id TEXT UNIQUE,          -- Format: {run_id}_kf{id}_d{idx}
    label TEXT,                 -- e.g., 'red_block', 'airport_bench'
    confidence FLOAT,
    map_x FLOAT,                -- Ground truth X from /odom
    map_y FLOAT,                -- Ground truth Y from /odom
    embedding vector(512)       -- L2-normalized CLIP features
);

CREATE INDEX ON detections USING hnsw (embedding vector_cosine_ops);


B. Graph Schema (Apache AGE)
Used for spatial reasoning and "Place" hierarchy.

Nodes: Run, Keyframe, Observation, Object, Place.

Edges: [:PART_OF], [:OBSERVES], [:LOCATED_IN], [:ADJACENT_TO].




2. Core Logic ImplementationA. Embedding Generator & GatingTo prevent "Pose Flooding," the system implements a Spatial Keyframe Gate.Distance Threshold: > 0.5 meters.Rotation Threshold: > 15 degrees.Logic: Inference (YOLOv8 + CLIP) is only triggered when the robot exceeds these deltas from the last committed pose.B. Graph Builder (Online DBSCAN)"Places" are constructed dynamically using clustering on keyframe centroids.Epsilon ($\epsilon$): 1.5 meters.Min Samples: 3 keyframes.Result: If the robot observes multiple landmarks within 1.5m, they are fused into a single topological Place node (e.g., "Kitchen_1").



3. Required Queries
Vector: Top-K Visual Similarity

-- Find top-5 matches for a query crop
SELECT label, confidence, 
       (1 - (embedding <=> '[query_vector]')) AS similarity
FROM detections 
ORDER BY similarity DESC LIMIT 5;


Graph: Reachable Objects (N-Hops)


-- Find all 'red_block' instances within 2 hops of current Place
SELECT * FROM cypher('semantic_map', $$
  MATCH (p1:Place {id: 'current_loc'})-[:ADJACENT_TO*1..2]-(p2:Place)
  MATCH (p2)<-[:LOCATED_IN]-(obj:Object {label: 'red_block'})
  RETURN p2.id, obj.id
$$) AS (place agtype, object agtype);



Re-localization: Top-3 Candidate Places

-- Cross-reference visual similarity with graph location
SELECT p.place_id, SUM(1 - (d.embedding <=> '[query_vec]')) as score
FROM detections d
JOIN place_nodes p ON d.map_x = p.cx AND d.map_y = p.cy
GROUP BY p.place_id
ORDER BY score DESC LIMIT 3;


4. Success and Failure Analysis
Success: Specialized Asset Discrimination
Scenario: Robot observes the "Airport Bench" vs. a standard "Chair."

Analysis: Standard YOLO class labels often conflate these as "seating." However, the CLIP ViT-B/32 embeddings provided a clear margin. The airport_bench returned a self-similarity of 1.0, while the chair returned 0.77. This high-dimensional resolution allowed the system to confirm the robot was in the "Lounge" rather than the "Office."

Failure: Spatial Aliasing (The "Red Block" Problem)
Scenario: Identical "Red Blocks" are placed in both the Kitchen and the Office.

Observation: Visual similarity for both blocks was > 0.98. The vector database alone could not determine the robot's location.

Resolution: The Semantic Relocalizer traversed the graph to find neighboring landmarks. Because the "Kitchen" block was topologically linked to a "Green Block" (observed 2 meters prior), while the "Office" block was isolated, the system used Temporal Context to correctly resolve the robot's position to the Kitchen.


5. Technical Challenges
Port Conflicts: Local PostgreSQL on 5432 required remapping the Docker container to Port 5433.

Permission Errors: The detector container required root user overrides to write the Ultralytics persistent cache.

Transactional Integrity: Implemented try-except blocks to ensure Vector data was committed even if the Graph (Apache AGE) service encountered extension-level errors.



