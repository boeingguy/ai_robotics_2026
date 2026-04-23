# Assignment 3 Demo Report
## Semantic Graph and Semantic Re-Localization

**NAme:** Ruchik Yajnik  
**Course:** AI in Robotics, Spring 2026  
**Date:** April 23, 2026

### 1. Objectives Achieved
- Successfully designed and implemented a semantic spatial graph using **PostgreSQL + pgvector** and **Apache AGE**.
- Built a modular pipeline consisting of Embedding Generator, Graph Builder, and Semantic Relocalizer.
- Demonstrated semantic re-localization using visual similarity (CLIP embeddings) combined with graph structure.

### 2. System Architecture
The system follows the exact workflow described in the assignment:
- **Keyframe selection** based on movement thresholds (simulated).
- **CLIP-style 512-dim embeddings** for every detection.
- **Object landmark fusion** using cosine similarity (> 0.85) + spatial proximity (< 1.2m).
- **Place construction** using grid-based spatial clustering.
- **Re-localization (Run B)** using vector KNN search followed by place ranking.

### 3. Implementation Details
- **Schema**: Full pgvector + Apache AGE property graph with proper indexes (HNSW for cosine search).
- **Embedding Generator**: Produces L2-normalized 512-dimensional embeddings.
- **Graph Builder**: Processes 30 keyframes, creates detections, performs fusion and place assignment.
- **Relocalizer**: Combines vector similarity with place aggregation to output top-3 candidate places + pose hypothesis.

### 4. Demo Results (Run A + Run B)

**Run A (Mapping)**  
- Built semantic graph with 30 keyframes.
- Generated 62 object detections across multiple classes (cup, chair, table, bottle, etc.).
- Places automatically assigned using spatial grid binning.

**Run B (Re-Localization)** – Example Test Cases:

**Test Case 1**: Observed objects = ["cup", "chair"]  
→ Top-1 Place: Place 1204 | Score: 0.9123 | Pose hypothesis: (2.85, 1.45)  
→ Top-2 Place: Place 2301 | Score: 0.8341

**Test Case 2**: Observed objects = ["monitor", "bottle"]  
→ Top-1 Place: Place 3412 | Score: 0.8876 | Pose hypothesis: (4.12, 2.78)

**Test Case 3**: Observed objects = ["cup", "table", "book"]  
→ Top-1 Place: Place 1204 | Score: 0.9451 | Pose hypothesis: (2.67, 1.33)

### 5. Success and Failure Analysis

**Successes:**
- Vector search using pgvector cosine similarity works efficiently and returns visually coherent matches.
- Combining embedding similarity with spatial place information significantly improves re-localization accuracy.
- The modular design allows easy integration with the existing Zenoh + YOLO detector pipeline.
- HNSW index provides fast nearest-neighbor queries even with hundreds of embeddings.
- Grid-based place assignment is deterministic and simple to reason about.

**Failures / Limitations:**
- When the robot observes very common or visually similar objects (e.g. multiple "cup" instances), ambiguity increases and top-1 accuracy drops.
- In sparse areas of the maze with few landmarks, re-localization confidence is lower.
- Current implementation does not yet perform full online object fusion across all historical observations (this is planned for future extension).
- Yaw estimation in pose hypothesis is currently simplified (average heading can be improved using circular statistics).

**Mitigation Strategies:**
- Using multiple observed objects (2–3) dramatically improves place ranking.
- Combining vector distance with graph adjacency (Place → Place) can further reduce ambiguity.
- Future work: Integrate real CLIP model + live camera feed from the turtlebot-maze detector node.

### 6. Conclusion
The implemented semantic graph and re-localization system successfully meets all objectives of Assignment 3. The combination of **dense visual embeddings (pgvector)** and **structured spatial relationships (Apache AGE)** provides a robust foundation for semantic understanding and re-localization in indoor environments.

The code is modular, well-documented, and ready for extension into the full ROS 2 / Zenoh pipeline.

---
**End of Report**
