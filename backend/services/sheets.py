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
            expected_headers = ['Date', 'Employee Code', 'Full Name', 'Check-In Time', 'Check-Out Time', 'Duration (hrs)', 'Confidence', 'Liveness', 'Status']
            
            # If empty or not matching specific columns (upgraded to 9 columns)
            if not headers or len(headers) < 9:
                print("📝 Upgrading/Initializing Sheet Headers (9 columns)...")
                # Instead of clear(), we just update row 1 to preserve data
                for i, header in enumerate(expected_headers, start=1):
                    self.sheet.update_cell(1, i, header)
                print("✅ Sheet headers upgraded to 9-column schema.")
            else:
                 print("✅ Sheet headers verified (9 columns).")
        except Exception as e:
            print(f"⚠️ Error checking headers: {e}")

    def get_today_status(self, employee_code):
        """Check if employee has checked in today and return status"""
        if not self.sheet:
            return None
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            all_records = self.sheet.get_all_records()
            
            for idx, record in enumerate(reversed(all_records), start=1):
                rec_date = str(record.get('Date', '')).strip()
                rec_code = str(record.get('Employee Code', '')).strip()
                
                if rec_code == str(employee_code).strip() and rec_date == today:
                    row_num = len(all_records) - idx + 2  # +2 for header and 1-indexing
                    return {
                        'row': row_num,
                        'check_in_time': record.get('Check-In Time'),
                        'check_out_time': record.get('Check-Out Time'),
                        'status': record.get('Status')
                    }
            return None
        except Exception as e:
            print(f"❌ Error checking today status: {e}")
            return None

    def log_checkin(self, employee_code, name, confidence, liveness):
        """Log a check-in event"""
        if not self.sheet:
            self.connect()
        
        if not self.sheet:
            print("❌ Google Sheets not connected. Skipping log.")
            return False

        try:
            # Check if already checked in today
            status = self.get_today_status(employee_code)
            if status and status['check_in_time']:
                print(f"⚠️ {name} already checked in today at {status['check_in_time']}")
                return False
            
            today = datetime.now().strftime("%Y-%m-%d")
            check_in_time = datetime.now().strftime("%H:%M:%S")
            
            # Formatting values for storage
            conf_str = f"{confidence:.4f}" if confidence else "0.0000"
            live_str = f"{liveness:.4f}" if liveness else "0.0000"
            
            row = [today, employee_code, name, check_in_time, '', '', conf_str, live_str, 'Checked-In']
            self.sheet.append_row(row)
            print(f"✅ Check-In logged: {name} ({check_in_time})")
            return True
        except Exception as e:
            print(f"❌ Error logging check-in: {e}")
            return False

    def log_checkout(self, employee_code, name):
        """Log a check-out event"""
        if not self.sheet:
            self.connect()
        
        if not self.sheet:
            print("❌ Google Sheets not connected. Skipping log.")
            return False

        try:
            status = self.get_today_status(employee_code)
            if not status or not status['check_in_time']:
                print(f"⚠️ {name} has not checked in today")
                return False
            
            if status['check_out_time']:
                print(f"⚠️ {name} already checked out at {status['check_out_time']}")
                return False
            
            # Update existing row
            check_out_time = datetime.now().strftime("%H:%M:%S")
            check_in_dt = datetime.strptime(status['check_in_time'], "%H:%M:%S")
            check_out_dt = datetime.strptime(check_out_time, "%H:%M:%S")
            duration = (check_out_dt - check_in_dt).total_seconds() / 3600  # hours
            
            self.sheet.update_cell(status['row'], 5, check_out_time)  # Check-Out Time
            self.sheet.update_cell(status['row'], 6, f"{duration:.2f}")  # Duration
            self.sheet.update_cell(status['row'], 7, 'Completed')  # Status
            
            print(f"✅ Check-Out logged: {name} ({check_out_time}, {duration:.2f}hrs)")
            return True
        except Exception as e:
            print(f"❌ Error logging check-out: {e}")
            return False

