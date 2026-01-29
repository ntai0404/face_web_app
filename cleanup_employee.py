"""
Script to completely remove an employee's data and retrain models.
Usage: python cleanup_employee.py --code <EMPLOYEE_CODE>
"""
import os
import argparse
import shutil
from pathlib import Path
import unicodedata

from backend.config import DATASET_DIR, EMPLOYEES_METADATA_PATH, MODELS_DIR
from backend.utils.metadata import EmployeesMetadata
from backend.services.classifier import SVMClassifier
from backend.services.knn_classifier import KNNClassifier

def remove_accents(text):
    """Remove Vietnamese accents for safe folder names"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join([c for c in nfd if unicodedata.category(c) != 'Mn'])

def cleanup(employee_code: str):
    print(f"🧹 Starting cleanup for employee: {employee_code}")
    
    # 1. Load Metadata
    metadata = EmployeesMetadata(Path(EMPLOYEES_METADATA_PATH))
    
    if not metadata.employee_exists(employee_code):
        print(f"❌ Employee {employee_code} not found in metadata.")
        return
    
    employee_info = metadata.get_employee(employee_code)
    full_name = employee_info.get('full_name', 'Unknown')
    
    # 2. Delete Dataset Folder
    safe_folder_name = remove_accents(full_name).replace(' ', '_')
    employee_folder = Path(DATASET_DIR) / safe_folder_name
    
    if employee_folder.exists():
        print(f"🗑️ Deleting images at: {employee_folder}")
        shutil.rmtree(employee_folder)
    else:
        print(f"⚠️ Dataset folder not found at: {employee_folder}")
    
    # 3. Delete from Metadata
    print(f"📝 Removing {employee_code} from employees.json")
    metadata.delete_employee(employee_code)
    
    # 4. Retrain Models
    print(f"🔄 Retraining models (SVM + KNN)...")
    embeddings, labels = metadata.get_all_embeddings_for_training()
    
    if len(embeddings) > 0:
        # Retrain SVM
        svm_path = Path(MODELS_DIR) / "classifier.pkl"
        svm = SVMClassifier(svm_path)
        svm.train(embeddings, labels)
        print(f"✅ SVM Retrained.")
        
        # Retrain KNN
        knn_path = Path(MODELS_DIR) / "knn_classifier.pkl"
        knn = KNNClassifier(knn_path)
        knn.train(embeddings, labels)
        print(f"✅ KNN Retrained.")
    else:
        print("⚠️ No employees left in system. Skipping retraining.")
        # Optionally remove old model files if system is empty
        for p in [Path(MODELS_DIR) / "classifier.pkl", Path(MODELS_DIR) / "knn_classifier.pkl"]:
            if p.exists():
                p.unlink()

    print(f"✨ Successfully removed all traces of {full_name} ({employee_code}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove employee data and retrain models")
    parser.add_argument("--code", required=True, help="Employee code to remove")
    args = parser.parse_args()
    
    cleanup(args.code)
