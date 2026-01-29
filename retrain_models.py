"""
Retrain both SVM and KNN models with current metadata
This will remove any cached predictions from deleted employees
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.metadata import EmployeesMetadata
from backend.services.classifier import SVMClassifier
from backend.services.knn_classifier import KNNClassifier
from backend.config import EMPLOYEES_METADATA_PATH, SVM_MODEL_PATH, MODELS_DIR, SVM_CONFIDENCE_THRESHOLD

def retrain_all_models():
    print("🔄 Retraining ALL models with current metadata...")
    print("=" * 60)
    
    # Load metadata
    metadata = EmployeesMetadata(EMPLOYEES_METADATA_PATH)
    
    # Get all embeddings
    embeddings, labels = metadata.get_all_embeddings_for_training()
    
    if len(embeddings) == 0:
        print("❌ No training data found!")
        return
    
    print(f"📊 Found {len(embeddings)} samples from {len(set(labels))} employees")
    print(f"📋 Employee codes: {sorted(set(labels))[:10]}..." if len(set(labels)) > 10 else f"📋 Employee codes: {sorted(set(labels))}")
    print()
    
    # Train SVM
    print("🧠 Training SVM...")
    svm = SVMClassifier(SVM_MODEL_PATH, SVM_CONFIDENCE_THRESHOLD)
    svm.train(embeddings, labels)
    print()
    
    # Train KNN
    print("🧠 Training KNN...")
    knn = KNNClassifier(MODELS_DIR / "knn_classifier.pkl", n_neighbors=1)
    knn.train(embeddings, labels)
    print()
    
    print("=" * 60)
    print("✅ Both models retrained successfully!")
    print("💡 Old cached predictions (e.g., deleted employees) have been removed.")
    print("🔄 Please restart the server for changes to take effect.")

if __name__ == "__main__":
    retrain_all_models()
