"""
Employees Metadata Manager
Thay thế database bằng JSON file để lưu thông tin nhân viên và embeddings
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pickle
import base64

class EmployeesMetadata:
    """
    Quản lý metadata của nhân viên (thay thế database)
    
    Format JSON:
    {
        "EMP_RONALDO": {
            "full_name": "Ronaldo",
            "department": "Sales",
            "created_at": "2026-01-28T19:00:00",
            "image_count": 15,
            "embeddings": [
                "base64_encoded_pickle_of_128d_vector_1",
                "base64_encoded_pickle_of_128d_vector_2",
                ...
            ]
        }
    }
    """
    
    def __init__(self, metadata_path: Path):
        """
        Args:
            metadata_path: Path to employees_metadata.json
        """
        self.metadata_path = metadata_path
        self.data: Dict = {}
        self.load()
    
    def load(self):
        """Load metadata từ file JSON"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Loaded metadata for {len(self.data)} employees")
        else:
            self.data = {}
            print("⚠️ No existing metadata file, starting fresh")
    
    def save(self):
        """Save metadata to JSON file"""
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def employee_exists(self, employee_code: str) -> bool:
        """Check if employee exists"""
        return employee_code in self.data
    
    def get_employee(self, employee_code: str) -> Optional[Dict]:
        """Get employee info"""
        return self.data.get(employee_code)
    
    def create_employee(self, employee_code: str, full_name: str, department: str = "Default"):
        """Create new employee"""
        if self.employee_exists(employee_code):
            raise ValueError(f"Employee {employee_code} already exists")
        
        self.data[employee_code] = {
            "full_name": full_name,
            "department": department,
            "created_at": datetime.now().isoformat(),
            "image_count": 0,
            "embeddings": []
        }
        self.save()
    
    def add_embedding(self, employee_code: str, embedding: np.ndarray):
        """
        Add embedding vector for an employee
        
        Args:
            employee_code: Employee code
            embedding: 128-d numpy array
        """
        if not self.employee_exists(employee_code):
            raise ValueError(f"Employee {employee_code} not found")
        
        # Pickle numpy array và encode sang base64 để lưu trong JSON
        pickled = pickle.dumps(embedding)
        encoded = base64.b64encode(pickled).decode('utf-8')
        
        self.data[employee_code]["embeddings"].append(encoded)
        self.data[employee_code]["image_count"] = len(self.data[employee_code]["embeddings"])
        self.save()
    
    def get_all_embeddings_for_training(self) -> tuple[List[np.ndarray], List[str]]:
        """
        Get all embeddings and labels for SVM training
        
        Returns:
            (embeddings_list, labels_list)
        """
        embeddings = []
        labels = []
        
        for employee_code, info in self.data.items():
            for encoded_embedding in info["embeddings"]:
                # Decode base64 và unpickle
                pickled = base64.b64decode(encoded_embedding)
                embedding = pickle.loads(pickled)
                
                embeddings.append(embedding)
                labels.append(employee_code)
        
        return embeddings, labels
    
    def get_all_employees(self) -> List[Dict]:
        """Get all employees info"""
        return [
            {
                "employee_code": code,
                **info
            }
            for code, info in self.data.items()
        ]
    
    def delete_employee(self, employee_code: str):
        """Delete an employee"""
        if employee_code in self.data:
            del self.data[employee_code]
            self.save()
