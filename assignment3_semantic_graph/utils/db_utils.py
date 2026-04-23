"""
Database utility functions for Assignment 3 Semantic Graph.
Provides clean connection handling and common operations for pgvector + AGE.
"""

import psycopg
from psycopg import sql
import os
from typing import Optional, Dict, Any

class DatabaseConnection:
    """Centralized database connection handler."""

    def __init__(self):
        self.conn_params = {
            "dbname": "semantic_graph",
            "user": "robot",
            "password": "robotpass",
            "host": "semantic-graph",   # Docker service name
            "port": "5432"
        }
        self.conn = None

    def connect(self):
        """Establish connection and configure AGE + search path."""
        if self.conn is None or self.conn.closed:
            self.conn = psycopg.connect(**self.conn_params)
            self._configure_age()
        return self.conn

    def _configure_age(self):
        """Configure Apache AGE for every new connection."""
        with self.conn.cursor() as cur:
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, \"$user\", public;")
            self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute a query and return all results."""
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # If it's a SELECT query
                return cur.fetchall()
            conn.commit()
            return []

    def execute(self, query: str, params: tuple = None):
        """Execute a non-select query (INSERT, UPDATE, etc.)."""
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()


# Global instance
db = DatabaseConnection()


def get_connection():
    """Convenience function to get DB connection."""
    return db.connect()


def insert_keyframe(run_id: int, map_x: float, map_y: float, map_yaw: float, timestamp=None) -> int:
    """Insert a keyframe and return its ID."""
    query = """
        INSERT INTO keyframes (run_id, timestamp, map_x, map_y, map_yaw)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING keyframe_id
    """
    if timestamp is None:
        timestamp = "CURRENT_TIMESTAMP"
    
    result = db.execute_query(query, (run_id, timestamp, map_x, map_y, map_yaw))
    return result[0][0] if result else None


def insert_detection(keyframe_id: int, class_label: str, confidence: float, 
                    bbox: str, embedding: list) -> int:
    """Insert a detection with its CLIP embedding."""
    query = """
        INSERT INTO detections (keyframe_id, class_label, confidence, bbox, embedding)
        VALUES (%s, %s, %s, %s, %s::vector)
        RETURNING det_id
    """
    result = db.execute_query(query, (keyframe_id, class_label, confidence, bbox, embedding))
    return result[0][0] if result else None
