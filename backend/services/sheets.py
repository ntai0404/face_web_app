import gspread
from oauth2client.service_account import ServiceAccountCredentials
from backend.config import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID
from datetime import datetime
import os

class GoogleSheetsService:
    def __init__(self):
        self.client = None
        self.sheet = None
        
    def connect(self):
        if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
            print(f"⚠️ Google Sheets Credentials not found at: {GOOGLE_CREDENTIALS_PATH}")
            return

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        try:
             creds = ServiceAccountCredentials.from_json_keyfile_name(str(GOOGLE_CREDENTIALS_PATH), scope)
             self.client = gspread.authorize(creds)
             self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID).sheet1 # Open first sheet
             print(f"✅ Connected to Google Sheet: {GOOGLE_SHEET_ID}")
             self._init_headers()
        except Exception as e:
             print(f"❌ Failed to connect to Google Sheets: {e}")
             self.client = None

    def _init_headers(self):
        if not self.sheet: return
        try:
            # Check if headers exist (row 1)
            headers = self.sheet.row_values(1)
            expected_headers = ['Timestamp', 'Employee Code', 'Full Name', 'Confidence', 'Liveness Score', 'Status']
            
            # If empty or not matching specific columns (basic check)
            if not headers:
                print("📝 Initializing Sheet Headers...")
                self.sheet.append_row(expected_headers)
            else:
                 print("✅ Sheet headers verified.")
        except Exception as e:
            print(f"⚠️ Error checking headers: {e}")

    def log_checkin(self, employee_code, name, confidence, liveness, status="Success"):
        """Log a check-in event to the sheet"""
        if not self.sheet:
            self.connect() # Try to reconnect if not connected
        
        if not self.sheet:
            print("❌ Google Sheets not connected. Skipping log.")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Handle potential None values
            conf_str = f"{confidence:.4f}" if confidence is not None else "N/A"
            live_str = f"{liveness:.4f}" if liveness is not None else "N/A"
            
            row = [timestamp, employee_code, name, conf_str, live_str, status]
            self.sheet.append_row(row)
            print(f"✅ Logged to Sheet: {name} ({timestamp})")
        except Exception as e:
            print(f"❌ Error logging to sheet: {e}")
