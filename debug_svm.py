
import joblib
import numpy as np
from backend.utils.metadata import EmployeesMetadata
from pathlib import Path

def check_raw_accuracy():
    print("🔬 Checking RAW Accuracy (no threshold)...")
    clf = joblib.load("models/classifier.pkl")
    metadata = EmployeesMetadata(Path("employees_metadata.json"))
    
    X, y = metadata.get_all_embeddings_for_training()
    X = np.array(X)
    
    y_pred = clf.predict(X)
    
    accuracy = np.mean(y_pred == y)
    print(f"🎯 Raw Memorization Accuracy: {accuracy*100:.2f}%")
    
    # Check one sample
    idx = 0
    probs = clf.predict_proba(X[idx].reshape(1, -1))[0]
    print(f"👤 Sample 0: True={y[idx]}, Pred={y_pred[idx]}")
    print(f"📊 Confidence (max prob): {np.max(probs):.4f}")
    print(f"📊 Sum of probs: {np.sum(probs):.4f}")

if __name__ == "__main__":
    check_raw_accuracy()
