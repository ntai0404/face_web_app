"""
One-time script to train KNN model with existing dataset
Run this once to initialize the KNN classifier
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.metadata import EmployeesMetadata
from backend.services.knn_classifier import KNNClassifier
from backend.config import EMPLOYEES_METADATA_PATH, MODELS_DIR

def train_knn():
    print("🔄 Training KNN model with existing dataset...")
    
    # Load metadata
    metadata = EmployeesMetadata(EMPLOYEES_METADATA_PATH)
    
    # Get all embeddings
    embeddings, labels = metadata.get_all_embeddings_for_training()
    
    if len(embeddings) == 0:
        print("❌ No training data found!")
        return
    
    print(f"📊 Found {len(embeddings)} samples from {len(set(labels))} employees")
    
    # Train KNN
    knn = KNNClassifier(MODELS_DIR / "knn_classifier.pkl", n_neighbors=1)
    knn.train(embeddings, labels)
    
    print("✅ KNN model trained and saved successfully!")

if __name__ == "__main__":
    train_knn()
