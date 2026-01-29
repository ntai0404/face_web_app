
# Add this to the end of check_in.py

class ConfirmAttendanceRequest(BaseModel):
    """Request for confirming attendance after user verification"""
    employee_code: str
    action: str  # "check-in" or "check-out"
    confidence: float
    liveness_score: float

@router.post("/confirm-attendance")
async def confirm_attendance(
    request: ConfirmAttendanceRequest,
    background_tasks: BackgroundTasks,
    app_request: Request
):
    """
    Confirm and log attendance after user verification in popup
    """
    sheets_service = app_request.app.state.sheets_service
    metadata = app_request.app.state.metadata
    
    # Get employee info
    employee_info = metadata.get_employee(request.employee_code)
    if not employee_info:
        return {"status": "fail", "message": "Employee not found"}
    
    if not sheets_service:
        return {"status": "fail", "message": "Sheets service not available"}
    
    # Perform the action
    if request.action.lower() == "check-out":
        success = sheets_service.log_checkout(
            employee_code=request.employee_code,
            name=employee_info['full_name']
        )
    else:
        success = sheets_service.log_checkin(
            employee_code=request.employee_code,
            name=employee_info['full_name'],
            confidence=request.confidence,
            liveness=request.liveness_score
        )
    
    if success:
        action_text = "Check-out" if request.action.lower() == "check-out" else "Check-in"
        return {
            "status": "success",
            "message": f"{action_text} thành công cho {employee_info['full_name']}!"
        }
    else:
        return {
            "status": "fail",
            "message": "Không thể ghi nhận. Vui lòng thử lại."
        }
