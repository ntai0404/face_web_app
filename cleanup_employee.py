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
from backend.services.sheets import GoogleSheetsService

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
        
    # 5. Cleanup Google Sheets (Today's records)
    print(f"📄 Cleaning up Google Sheets records for {employee_code} (Today only)...")
    try:
        sheets = GoogleSheetsService()
        sheets.connect()
        if sheets.sheet:
            all_records = sheets.sheet.get_all_records()
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find matching rows (Search from bottom to handle row shift better)
            rows_to_delete = []
            for idx, record in enumerate(all_records):
                rec_date = sheets._parse_date(record.get('Date', ''))
                rec_code = str(record.get('Employee Code', '')).strip().lower()
                if rec_code == employee_code.lower() and rec_date == today:
                    rows_to_delete.append(idx + 2) # +2 for header and 1-indexing
            
            if rows_to_delete:
                # Delete rows from bottom up to avoid index shifting
                for row_idx in sorted(rows_to_delete, reverse=True):
                    sheets.sheet.delete_rows(row_idx)
                    print(f"🗑️ Deleted sheet row {row_idx}")
                print(f"✅ Removed {len(rows_to_delete)} records from Google Sheets.")
            else:
                print("ℹ️ No records found today in Google Sheets.")
    except Exception as e:
        print(f"⚠️ Error cleaning up Google Sheets: {e}")
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
