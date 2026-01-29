"""
Script to delete an employee from metadata
This will remove their embeddings completely
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.metadata import EmployeesMetadata
from backend.config import EMPLOYEES_METADATA_PATH

def delete_employee(employee_code: str):
    print(f"🗑️ Deleting employee: {employee_code}")
    
    metadata = EmployeesMetadata(EMPLOYEES_METADATA_PATH)
    
    if employee_code not in metadata.data:
        print(f"❌ Employee {employee_code} not found in metadata!")
        print(f"Available employees: {list(metadata.data.keys())[:10]}...")
        return
    
    # Delete from metadata
    metadata.delete_employee(employee_code)
    print(f"✅ Deleted {employee_code} from metadata")
    print(f"💾 Metadata saved. Remaining employees: {len(metadata.data)}")
    print()
    print("⚠️ IMPORTANT: Run 'python retrain_models.py' to update the models!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_employee.py <EMPLOYEE_CODE>")
        print("Example: python delete_employee.py EMP_NGUYEN_XUAN_TAI")
        sys.exit(1)
    
    employee_code = sys.argv[1]
    delete_employee(employee_code)
