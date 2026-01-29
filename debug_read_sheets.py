from backend.services.sheets import GoogleSheetsService
from backend.config import GOOGLE_SHEET_ID
import json

def test_read_sheet():
    service = GoogleSheetsService()
    service.connect()
    if not service.sheet:
        print("Failed to connect")
        return
    
    print(f"Reading sheet: {GOOGLE_SHEET_ID}")
    records = service.sheet.get_all_records()
    print(f"Found {len(records)} records")
    
    for i, r in enumerate(records[-5:]): # Show last 5
        print(f"{i}: {r}")

if __name__ == "__main__":
    test_read_sheet()
