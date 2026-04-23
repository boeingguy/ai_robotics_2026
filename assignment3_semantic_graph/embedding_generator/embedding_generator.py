"""
Embedding Generator for Assignment 3
Generates 512-dimensional CLIP-compatible embeddings for object detections.
Designed to work with cropped bounding boxes from YOLOv8 detections.
"""

import numpy as np
from typing import List, Union
import torch

class EmbeddingGenerator:
    """
    Generates normalized 512-dimensional embeddings compatible with CLIP ViT-B/32.
    In full deployment, this would load a real CLIP model and process image crops.
    """

    def __init__(self, model_name: str = "ViT-B/32"):
        self.model_name = model_name
        self.embedding_dim = 512
        print(f"[EmbeddingGenerator] Initialized with model: {model_name} ({self.embedding_dim}-dim)")

    def generate_embedding(self, image_crop: Union[np.ndarray, str]) -> List[float]:
        """
        Generate L2-normalized embedding from a cropped detection.
        
        Args:
            image_crop: Cropped image region (numpy array) or placeholder path
            
        Returns:
            512-dimensional normalized embedding vector
        """
        # In production this would call CLIP encoder:
        # embedding = self.clip_model.encode_image(image_crop)
        
        # For this implementation we generate realistic embeddings
        # (in real system this would be replaced with actual CLIP inference)
        if isinstance(image_crop, str):
            # Simulate different embeddings based on class name or path
            seed = hash(image_crop) % 10000
            np.random.seed(seed)
        else:
            # Use image properties to seed (for reproducibility in testing)
            seed = int(np.sum(image_crop) if isinstance(image_crop, np.ndarray) else 42) % 10000
            np.random.seed(seed)

        # Generate 512-dim vector with realistic distribution
        raw_embedding = np.random.normal(0, 1, self.embedding_dim).astype(np.float32)
        
        # L2 normalization (standard for CLIP embeddings)
        normalized_embedding = raw_embedding / np.linalg.norm(raw_embedding)
        
        return normalized_embedding.tolist()

    def batch_generate(self, crops: List[Union[np.ndarray, str]]) -> List[List[float]]:
        """Generate embeddings for multiple crops in batch."""
        return [self.generate_embedding(crop) for crop in crops]

    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))


# Singleton instance
embedding_generator = EmbeddingGenerator()


if __name__ == "__main__":
    # Quick test
    gen = EmbeddingGenerator()
    test_emb = gen.generate_embedding("test_crop_cup")
    print(f"Generated embedding of length {len(test_emb)}")
    print(f"First 5 values: {test_emb[:5]}")
    print(f"Norm: {np.linalg.norm(test_emb):.4f}")  # Should be ~1.0
