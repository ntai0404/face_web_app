"""
SVM Classifier Service
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.svm import SVC
from typing import Tuple, Optional

class SVMClassifier:
    """
    SVM classifier để nhận diện danh tính dựa trên embedding vectors
    """
    
    def __init__(self, model_path: Path, threshold: float = 0.7):
        """
        Args:
            model_path: Đường dẫn đến file .pkl của SVM model
            threshold: Ngưỡng xác suất tối thiểu để nhận diện
        """
        self.model_path = model_path
        self.threshold = threshold
        self.model: Optional[SVC] = None
        
        # Load model nếu đã tồn tại
        if model_path.exists():
            self.load_model()
        else:
            print(f"⚠️ SVM model not found at {model_path}. Need to train first.")
    
    def load_model(self):
        """Load trained SVM model"""
        self.model = joblib.load(self.model_path)
        print(f"✅ SVM model loaded from {self.model_path}")
    
    def train(self, embeddings: list[np.ndarray], labels: list[str]):
        """
        Huấn luyện SVM với embeddings và labels
        
        Args:
            embeddings: List of 128-d vectors
            labels: List of employee codes
        """
        if len(embeddings) == 0:
            raise ValueError("No training data provided")
        
        X = np.array(embeddings)
        y = np.array(labels)
        
        print(f"Training SVM with {len(X)} samples, {len(set(y))} classes...")
        
        # Train SVM
        self.model = SVC(
            kernel='linear',  # Linear kernel is often better for 128-d embeddings
            probability=True,
            C=1.0,
            class_weight='balanced'
        )
        self.model.fit(X, y)
        
        # Save model
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        print(f"✅ SVM training complete. Model saved to {self.model_path}")
    
    def predict(self, embedding: np.ndarray) -> Tuple[str, float]:
        """
        Dự đoán danh tính từ embedding vector
        
        Args:
            embedding: 128-d vector
        
        Returns:
            (employee_code, confidence)
            - employee_code: Mã nhân viên (hoặc "Unknown")
            - confidence: Xác suất (0-1)
        """
        if self.model is None:
            return "Unknown", 0.0
        
        # Reshape để predict
        X = embedding.reshape(1, -1)
        
        # Get probabilities
        probabilities = self.model.predict_proba(X)[0]
        max_prob_idx = np.argmax(probabilities)
        max_prob = probabilities[max_prob_idx]
        
        # Check threshold
        if max_prob < self.threshold:
            return "Unknown", float(max_prob)
        
        # Get class label
        predicted_label = self.model.classes_[max_prob_idx]
        
        return str(predicted_label), float(max_prob)
