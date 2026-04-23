-- =====================================================
-- Assignment 3: Semantic Graph and Semantic Re-Localization
-- pgvector + Apache AGE Property Graph Schema
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;

-- Load AGE and set search path
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- =====================================================
-- Create Property Graph
-- =====================================================
SELECT create_graph('semantic_maze_graph');

-- =====================================================
-- Relational Tables (for efficient storage and querying)
-- =====================================================

-- Runs table (Run A = mapping, Run B = relocalization)
CREATE TABLE IF NOT EXISTS runs (
    run_id SERIAL PRIMARY KEY,
    run_type TEXT NOT NULL CHECK (run_type IN ('mapping', 'relocalization')),
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Keyframes table - stores robot pose in map frame
CREATE TABLE IF NOT EXISTS keyframes (
    keyframe_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES runs(run_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    map_x DOUBLE PRECISION NOT NULL,
    map_y DOUBLE PRECISION NOT NULL,
    map_yaw DOUBLE PRECISION NOT NULL,
    place_id INTEGER,
    CONSTRAINT valid_yaw CHECK (map_yaw >= -180 AND map_yaw <= 180)
);

-- Detections table with pgvector embeddings (CLIP ViT-B/32 - 512 dimensions)
CREATE TABLE IF NOT EXISTS detections (
    det_id SERIAL PRIMARY KEY,
    keyframe_id INTEGER REFERENCES keyframes(keyframe_id) ON DELETE CASCADE,
    class_label TEXT NOT NULL,
    confidence DOUBLE PRECISION CHECK (confidence >= 0 AND confidence <= 1),
    bbox TEXT,                          -- Format: "x1,y1,x2,y2"
    embedding vector(512) NOT NULL      -- CLIP embedding
);

-- Create HNSW index for fast cosine similarity search (recommended for pgvector)
CREATE INDEX IF NOT EXISTS idx_detections_embedding 
ON detections USING hnsw (embedding vector_cosine_ops);

-- =====================================================
-- Apache AGE Graph Labels (Vertices)
-- =====================================================
SELECT create_vlabel('semantic_maze_graph', 'Run');
SELECT create_vlabel('semantic_maze_graph', 'Keyframe');
SELECT create_vlabel('semantic_maze_graph', 'Pose');
SELECT create_vlabel('semantic_maze_graph', 'Observation');
SELECT create_vlabel('semantic_maze_graph', 'Object');
SELECT create_vlabel('semantic_maze_graph', 'Place');

-- =====================================================
-- Apache AGE Edge Labels
-- =====================================================
SELECT create_elabel('semantic_maze_graph', 'CONTAINS');
SELECT create_elabel('semantic_maze_graph', 'HAS_POSE');
SELECT create_elabel('semantic_maze_graph', 'HAS_OBSERVATION');
SELECT create_elabel('semantic_maze_graph', 'REFERS_TO');
SELECT create_elabel('semantic_maze_graph', 'LOCATED_IN');
SELECT create_elabel('semantic_maze_graph', 'ADJACENT_TO');

-- =====================================================
-- Sample Data Insertion for Run A (will be populated by graph_builder)
-- =====================================================
INSERT INTO runs (run_type, description) 
VALUES ('mapping', 'Assignment 3 - Mapping Run A - Maze Exploration')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Useful Views
-- =====================================================
CREATE OR REPLACE VIEW v_keyframe_detections AS
SELECT 
    k.keyframe_id,
    k.map_x,
    k.map_y,
    k.map_yaw,
    d.class_label,
    d.confidence,
    d.embedding
FROM keyframes k
JOIN detections d ON k.keyframe_id = d.keyframe_id;

-- End of schema
