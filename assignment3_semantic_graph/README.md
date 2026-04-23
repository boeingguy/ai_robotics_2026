# Assignment 3: Semantic Graph and Semantic Re-Localization

## Overview
This project implements a complete semantic spatial graph system using PostgreSQL with Apache AGE (property graph) and pgvector (vector embeddings). 

The system supports:
- Keyframe selection and processing from robot camera and pose data
- CLIP-style 512-dimensional embeddings for object detections
- Object landmark fusion using visual similarity and spatial proximity
- Place construction through spatial clustering
- Semantic re-localization using vector search combined with graph traversal

## Deliverables
- pgvector + AGE schema
- Embedding generator
- Graph builder (with object fusion and place clustering)
- Semantic relocalizer
- Demo report with success and failure analysis

## Project Structure

assignment3_semantic_graph/
├── schema/                    # Database schema (pgvector + AGE)
├── embedding_generator/       # CLIP embedding generation
├── graph_builder/             # Keyframe processing, fusion, and graph construction
├── semantic_relocalizer/      # Run B re-localization logic
├── queries/                   # Vector, graph, and combined queries
├── utils/                     # Database utilities
├── docker-compose.override.yaml
├── README.md
└── report.md
