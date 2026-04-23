-- =====================================================
-- Query 3: Combined Re-Localization Query
-- Vector search + Graph ranking (most important for Assignment 3)
-- =====================================================

WITH vector_matches AS (
    SELECT 
        d.class_label,
        k.place_id,
        k.map_x,
        k.map_y,
        (d.embedding <=> $1::vector) AS distance
    FROM detections d
    JOIN keyframes k ON d.keyframe_id = k.keyframe_id
    ORDER BY d.embedding <=> $1::vector
    LIMIT 15
)
SELECT 
    place_id,
    COUNT(*) as match_count,
    AVG(1.0 - distance) as avg_similarity,
    AVG(map_x) as estimated_x,
    AVG(map_y) as estimated_y
FROM vector_matches
GROUP BY place_id
HAVING AVG(1.0 - distance) > 0.78
ORDER BY avg_similarity DESC
LIMIT 3;
