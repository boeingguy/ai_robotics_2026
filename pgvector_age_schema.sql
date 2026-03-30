-- Enable Vector Extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Visual Landmark Table
CREATE TABLE detections (
    id SERIAL PRIMARY KEY,
    det_id TEXT UNIQUE,          -- Unique Join Key: {run}_{kf_id}_{det_idx}
    label TEXT,                 -- e.g., 'red_block', 'airport_bench'
    confidence FLOAT,
    map_x FLOAT,                -- Robot X-pose
    map_y FLOAT,                -- Robot Y-pose
    embedding vector(512)       -- CLIP ViT-B/32 Normalized Features
);

-- Performance Index for Similarity Search
CREATE INDEX ON detections USING hnsw (embedding vector_cosine_ops);
