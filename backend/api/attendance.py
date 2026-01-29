"""
API endpoints for attendance dashboard and statistics
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from backend.services.sheets import GoogleSheetsService

router = APIRouter(prefix="/attendance", tags=["attendance"])

# Dependency to get sheets service
def get_sheets_service():
    from backend.main import app
    return app.state.sheets_service

@router.get("/stats")
async def get_today_stats(sheets: GoogleSheetsService = Depends(get_sheets_service)):
    """Get today's attendance statistics"""
    if not sheets or not sheets.sheet:
        return {
            "total_employees": 0,
            "checked_in": 0,
            "checked_out": 0,
            "currently_working": 0
        }
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        all_records = sheets.sheet.get_all_records()
        
        # Robust filtering
        today_records = []
        for r in all_records:
            r_date = str(r.get('Date', '')).strip()
            if r_date == today:
                today_records.append(r)
        
        checked_in = len([r for r in today_records if r.get('Check-In Time')])
        checked_out = len([r for r in today_records if r.get('Check-Out Time')])
        currently_working = checked_in - checked_out
        
        return {
            "total_employees": len(today_records),
            "checked_in": checked_in,
            "checked_out": checked_out,
            "currently_working": currently_working
        }
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return {
            "total_employees": 0,
            "checked_in": 0,
            "checked_out": 0,
            "currently_working": 0
        }

@router.get("/today")
async def get_today_attendance(sheets: GoogleSheetsService = Depends(get_sheets_service)):
    """Get today's attendance records"""
    if not sheets or not sheets.sheet:
        return {"records": []}
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        all_records = sheets.sheet.get_all_records()
        
        # Robust date filtering: handle potential string mismatch or local formatting
        today_records = []
        for r in all_records:
            r_date = str(r.get('Date', '')).strip()
            if r_date == today:
                today_records.append(r)
        
        # Format records
        formatted_records = []
        for record in today_records:
            check_in = record.get('Check-In Time', '')
            check_out = record.get('Check-Out Time', '')
            
            # Determine status
            if check_out:
                status = "left"
                status_icon = "🔴"
            elif check_in:
                status = "working"
                status_icon = "🟢"
            else:
                status = "not_arrived"
                status_icon = "⚪"
            
            # Convert confidence/liveness to floats if possible
            try:
                conf = float(record.get('Confidence', 0))
            except:
                conf = 0.0
            
            try:
                live = float(record.get('Liveness', 0))
            except:
                live = 0.0
            
            formatted_records.append({
                "employee_code": record.get('Employee Code', ''),
                "full_name": record.get('Full Name', ''),
                "check_in_time": check_in,
                "check_out_time": check_out,
                "duration": record.get('Duration (hrs)', ''),
                "confidence": conf,
                "liveness_score": live,
                "status": status,
                "status_icon": status_icon
            })
        
        return {"records": formatted_records}
    except Exception as e:
        print(f"❌ Error getting today's attendance: {e}")
        return {"records": []}
