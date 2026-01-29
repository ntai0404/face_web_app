"""
Script to clean up Google Sheets - Remove all "Tài" records
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.services.sheets import GoogleSheetsService

def cleanup_tai_records():
    print("🧹 Cleaning up Google Sheets - Removing 'Tài' records...")
    
    # Connect to Google Sheets
    sheets = GoogleSheetsService()
    sheets.connect()
    
    if not sheets.sheet:
        print("❌ Failed to connect to Google Sheets")
        return
    
    # Get all records
    all_records = sheets.sheet.get_all_records()
    print(f"📊 Total records: {len(all_records)}")
    
    # Find rows with "Tài"
    rows_to_delete = []
    for idx, record in enumerate(all_records, start=2):  # Start from row 2 (row 1 is header)
        employee_name = record.get('Employee Name', '')
        if 'Tài' in employee_name or 'tài' in employee_name.lower():
            rows_to_delete.append(idx)
            print(f"  Found: Row {idx} - {employee_name}")
    
    if not rows_to_delete:
        print("✅ No 'Tài' records found. Sheet is clean!")
        return
    
    print(f"\n🗑️ Deleting {len(rows_to_delete)} rows...")
    
    # Delete rows in reverse order (to avoid index shifting)
    for row_num in reversed(rows_to_delete):
        sheets.sheet.delete_rows(row_num)
        print(f"  ✓ Deleted row {row_num}")
    
    print(f"\n✅ Cleanup complete! Deleted {len(rows_to_delete)} records.")
    print(f"📊 Remaining records: {len(all_records) - len(rows_to_delete)}")

if __name__ == "__main__":
    cleanup_tai_records()
