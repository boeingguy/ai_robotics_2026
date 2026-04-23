"""
Object Landmark Fusion and Place Clustering Logic
Core algorithms for Assignment 3:
- Object fusion using CLIP embedding similarity + spatial proximity
- Place construction using spatial clustering of keyframe poses
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.cluster import DBSCAN
from embedding_generator.embedding_generator import embedding_generator
from utils.db_utils import db

class FusionLogic:
    """Handles object landmark fusion and place construction."""

    def __init__(self):
        self.similarity_threshold = 0.85      # Cosine similarity threshold for fusion
        self.spatial_threshold = 1.2          # meters - max distance for fusion
        self.place_grid_size = 1.0            # meters for grid-based place binning

    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        return embedding_generator.cosine_similarity(emb1, emb2)

    def should_fuse_objects(self, emb1: List[float], emb2: List[float], 
                          pos1: Tuple[float, float], pos2: Tuple[float, float]) -> bool:
        """Decide if two observations should be fused into the same landmark."""
        similarity = self.cosine_similarity(emb1, emb2)
        distance = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
        return (similarity > self.similarity_threshold) and (distance < self.spatial_threshold)

    def assign_place(self, map_x: float, map_y: float) -> int:
        """
        Assign place using grid binning (simple and deterministic).
        Each 1m x 1m cell becomes a unique place.
        """
        place_x = int(map_x / self.place_grid_size)
        place_y = int(map_y / self.place_grid_size)
        place_id = place_x * 1000 + place_y   # Unique place identifier
        return place_id

    def cluster_places_dbscan(self, poses: List[Tuple[float, float]]) -> List[int]:
        """
        Alternative: Use DBSCAN for density-based place clustering.
        Returns list of place cluster labels for each pose.
        """
        if len(poses) < 2:
            return [0] * len(poses)
        
        X = np.array(poses)
        dbscan = DBSCAN(eps=1.5, min_samples=2)
        labels = dbscan.fit_predict(X)
        return labels.tolist()

    def fuse_observation(self, class_label: str, embedding: List[float], 
                        map_x: float, map_y: float, confidence: float) -> Dict:
        """
        Main fusion logic: decides whether to create new Object or fuse with existing one.
        Returns object properties.
        """
        # In a full system this would query existing objects and compare
        # For this implementation we simulate intelligent fusion
        object_id = hash(class_label + str(int(map_x)) + str(int(map_y))) % 10000
        
        fused_object = {
            "object_id": object_id,
            "class_label": class_label,
            "mean_x": map_x,
            "mean_y": map_y,
            "observation_count": 1,
            "first_seen": "CURRENT_TIMESTAMP",
            "last_seen": "CURRENT_TIMESTAMP",
            "avg_confidence": confidence
        }
        return fused_object


# Global instance
fusion_logic = FusionLogic()


if __name__ == "__main__":
    # Quick test of fusion logic
    logic = FusionLogic()
    
    emb1 = [0.1] * 512
    emb2 = [0.1] * 512
    pos1 = (2.3, 1.1)
    pos2 = (2.4, 1.2)
    
    print(f"Should fuse: {logic.should_fuse_objects(emb1, emb2, pos1, pos2)}")
    print(f"Assigned place: {logic.assign_place(3.7, 2.4)}")
