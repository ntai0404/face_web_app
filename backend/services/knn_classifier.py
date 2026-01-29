"""
KNN Classifier Service
Alternative to SVM for face recognition using distance-based matching
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from typing import Tuple, Optional

class KNNClassifier:
    """
    KNN classifier for identity recognition based on embedding vectors.
    Uses distance-based confidence scoring (more intuitive than SVM probability).
    """
    
    def __init__(self, model_path: Path, n_neighbors: int = 1):
        """
        Args:
            model_path: Path to .pkl file for KNN model
            n_neighbors: Number of neighbors to consider (default=1 for strict matching)
        """
        self.model_path = model_path
        self.n_neighbors = n_neighbors
        self.model: Optional[KNeighborsClassifier] = None
        
        # Load model if exists
        if model_path.exists():
            self.load_model()
        else:
            print(f"⚠️ KNN model not found at {model_path}. Need to train first.")
    
    def load_model(self):
        """Load trained KNN model"""
        self.model = joblib.load(self.model_path)
        print(f"✅ KNN model loaded from {self.model_path}")
    
    def train(self, embeddings: list[np.ndarray], labels: list[str]):
        """
        Train KNN with embeddings and labels
        
        Args:
            embeddings: List of 128-d vectors
            labels: List of employee codes
        """
        if len(embeddings) == 0:
            raise ValueError("No training data provided")
        
        X = np.array(embeddings)
        y = np.array(labels)
        
        print(f"Training KNN with {len(X)} samples, {len(set(y))} classes...")
        
        # Train KNN with Euclidean distance
        self.model = KNeighborsClassifier(
            n_neighbors=self.n_neighbors,
            metric='euclidean',
            weights='distance'  # Weight by inverse distance
        )
        self.model.fit(X, y)
        
        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        print(f"✅ KNN training complete. Model saved to {self.model_path}")
    
    def predict(self, embedding: np.ndarray) -> Tuple[str, float]:
        """
        Predict identity from embedding vector
        
        Args:
            embedding: 128-d vector
        
        Returns:
            (employee_code, confidence)
            - employee_code: Employee ID
            - confidence: Similarity score (0-1), higher is better
        """
        if self.model is None:
            return "Unknown", 0.0
        
        # Reshape for prediction
        X = embedding.reshape(1, -1)
        
        # Get prediction
        predicted_label = self.model.predict(X)[0]
        
        # Calculate confidence based on distance to nearest neighbor
        distances, indices = self.model.kneighbors(X)
        nearest_distance = distances[0][0]
        
        # Convert distance to similarity score (0-1)
        # Using exponential decay: confidence = e^(-distance)
        # This gives ~90% for distance=0.1, ~60% for distance=0.5, ~37% for distance=1.0
        confidence = np.exp(-nearest_distance)
        
        # Alternative: Linear inverse (uncomment if preferred)
        # max_distance = 2.0  # Typical max distance in embedding space
        # confidence = max(0, 1 - (nearest_distance / max_distance))
        
        return str(predicted_label), float(confidence)
