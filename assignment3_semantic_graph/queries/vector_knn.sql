-- =====================================================
-- Query 1: Vector KNN Search (pgvector)
-- Top-k visually similar detections using CLIP embeddings
-- =====================================================

SELECT 
    d.det_id,
    d.class_label,
    d.confidence,
    k.map_x,
    k.map_y,
    k.map_yaw,
    (d.embedding <=> $1::vector) AS cosine_distance,
    1.0 - (d.embedding <=> $1::vector) AS similarity_score
FROM detections d
JOIN keyframes k ON d.keyframe_id = k.keyframe_id
ORDER BY d.embedding <=> $1::vector
LIMIT 10;
