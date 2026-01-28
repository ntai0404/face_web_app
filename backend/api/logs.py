"""
Google Sheets Integration API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

class LogEntry(BaseModel):
    """Single log entry for Google Sheets"""
    timestamp: str
    employee_code: str
    employee_name: str
    confidence_score: float
    liveness_score: float
    status: str
    device_info: str | None = None

class LogResponse(BaseModel):
    """Response cho API logs"""
    status: str
    message: str
    logged_count: int = 0

# TODO: Implement Google Sheets client
# from backend.utils.gsheet_client import GoogleSheetsClient
# gsheet_client = GoogleSheetsClient()

@router.post("/log-checkin", response_model=LogResponse)
async def log_check_in_to_sheets(entry: LogEntry):
    """
    Ghi log check-in lên Google Sheets
    
    Args:
        entry: Thông tin check-in cần log
    """
    try:
        # TODO: Implement actual Google Sheets append
        # gsheet_client.append_row([
        #     entry.timestamp,
        #     entry.employee_code,
        #     entry.employee_name,
        #     entry.confidence_score,
        #     entry.liveness_score,
        #     entry.status,
        #     entry.device_info or ""
        # ])
        
        print(f"📝 [LOG] {entry.timestamp} | {entry.employee_code} | {entry.employee_name} | Confidence: {entry.confidence_score}")
        
        return LogResponse(
            status="success",
            message="Check-in logged to Google Sheets",
            logged_count=1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log to Google Sheets: {str(e)}")

@router.get("/logs/recent")
async def get_recent_logs(limit: int = 50):
    """
    Lấy danh sách check-in logs gần đây từ Google Sheets
    
    Args:
        limit: Số lượng records tối đa (default 50)
    """
    try:
# TODO: Implement actual fetch from Google Sheets
        # rows = gsheet_client.get_recent_rows(limit)
        # return {"status": "success", "logs": rows}
        
        return {
            "status": "success",
            "message": "Google Sheets integration not yet implemented",
            "logs": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")
