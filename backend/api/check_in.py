"""
Check-in API Endpoint
POST /api/check-in
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import base64
import cv2
import numpy as np
from datetime import datetime
from backend.config import LIVENESS_ENABLED

router = APIRouter()

class CheckInRequest(BaseModel):
    """Request body cho API check-in"""
    image: str  # Base64 encoded image
    action: str = "check-in"  # "check-in" or "check-out"

class CheckInResponse(BaseModel):
    """Response cho API check-in"""
    status: str  # "success" hoặc "fail"
    employee_code: str | None = None
    employee_name: str | None = None
    confidence: float | None = None
    liveness_score: float | None = None
    message: str | None = None
    timestamp: str = None
    action_type: str | None = None  # "check-in" or "check-out"
    # Dual-brain predictions
    svm_prediction: dict | None = None  # {"code": "EMP_X", "confidence": 0.09}
    knn_prediction: dict | None = None  # {"code": "EMP_X", "confidence": 0.85}

@router.post("/check-in", response_model=CheckInResponse)
async def check_in(
    request: CheckInRequest,
    app_request: Request,
    background_tasks: BackgroundTasks
):
    """
    API Check-in nhân viên
    
    Pipeline:
    1. Decode base64 image
    2. Liveness Detection (chống giả mạo)
    3. Face Alignment (MTCNN)
    4. Feature Extraction (FaceNet)
    5. SVM Classification
    6. Log to Google Sheets (optional)
    """
    
    try:
        # Step 1: Decode base64 image
        try:
            # Remove data URL prefix if exists
            if ',' in request.image:
                image_data = request.image.split(',')[1]
            else:
                image_data = request.image
            
            img_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Cannot decode image")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        
        # Get services from app state
        metadata = app_request.app.state.metadata
        liveness_detector = app_request.app.state.liveness_detector
        face_aligner = app_request.app.state.face_aligner
        facenet_extractor = app_request.app.state.facenet_extractor
        svm_classifier = app_request.app.state.svm_classifier
        knn_classifier = app_request.app.state.knn_classifier
        
        # Step 2: Liveness Detection
        if LIVENESS_ENABLED:
            is_real, liveness_score = liveness_detector.predict(image)
        else:
            is_real, liveness_score = True, 1.0  # Bypass for demo
        
        if not is_real:
            return CheckInResponse(
                status="fail",
                message="Spoof detected - Please use a real face",
                liveness_score=liveness_score,
                timestamp=datetime.now().isoformat()
            )
        
        # Step 3: Face Alignment
        aligned_face, landmarks = face_aligner.align(image)
        
        if aligned_face is None:
            return CheckInResponse(
                status="fail",
                message="No face detected in image",
                liveness_score=liveness_score,
                timestamp=datetime.now().isoformat()
            )
        
        # Step 4: Feature Extraction
        embedding = facenet_extractor.extract(aligned_face)
        
        # Step 5: Dual-Brain Classification (SVM + KNN)
        svm_code, svm_conf = svm_classifier.predict(embedding)
        knn_code, knn_conf = knn_classifier.predict(embedding)
        
        # Dual-Threshold Validation
        SVM_MIN_THRESHOLD = 0.028  # 2.8%
        KNN_MIN_THRESHOLD = 0.70   # 70% (Used as fallback or secondary check)
        
        # PRIORITIZE SVM as requested
        if svm_conf >= SVM_MIN_THRESHOLD:
            # SVM is confident enough
            employee_code = svm_code
            confidence = svm_conf
            status = "success"
            message = "Nhận diện bằng SVM (Ưu tiên)"
        elif knn_conf >= KNN_MIN_THRESHOLD:
            # Fallback to KNN if SVM is low but KNN is high
            employee_code = knn_code
            confidence = knn_conf
            status = "success"
            message = "Nhận diện bằng KNN (Dự phòng)"
        else:
            # Neither reliable
            return CheckInResponse(
                status="retry",
                message=f"Không có nhân viên trùng khớp\n(SVM: {svm_conf*100:.1f}%, KNN: {knn_conf*100:.1f}%)",
                confidence=svm_conf, # Return SVM confidence as primary
                liveness_score=liveness_score,
                svm_prediction={"code": svm_code, "confidence": svm_conf},
                knn_prediction={"code": knn_code, "confidence": knn_conf},
                timestamp=datetime.now().isoformat()
            )
        
        if employee_code == "Unknown":
            return CheckInResponse(
                status="fail",
                message="Người lạ - Vui lòng đăng ký trước",
                confidence=confidence,
                liveness_score=liveness_score,
                svm_prediction={"code": svm_code, "confidence": svm_conf},
                knn_prediction={"code": knn_code, "confidence": knn_conf},
                timestamp=datetime.now().isoformat()
            )
        
        # Get employee info from metadata
        employee_info = metadata.get_employee(employee_code)
        
        if not employee_info:
            return CheckInResponse(
                status="fail",
                message=f"Employee {employee_code} not found in metadata",
                employee_code=employee_code,
                confidence=confidence,
                liveness_score=liveness_score,
                timestamp=datetime.now().isoformat()
            )
        
        
        
        # Move validation to confirm step. Just return success if identified.
        action_taken = request.action.lower()
        message = f"Nhận diện thành công: {employee_info['full_name']}"
        
        return CheckInResponse(
            status="success",
            employee_code=employee_code,
            employee_name=employee_info['full_name'],
            confidence=confidence,
            liveness_score=liveness_score,
            message=message,
            action_type=action_taken,
            svm_prediction={"code": svm_code, "confidence": svm_conf},
            knn_prediction={"code": knn_code, "confidence": knn_conf},
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Append to check_in.py

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
    
    # -------------------------------------------------------------
    # BUSINESS LOGIC VALIDATION
    # -------------------------------------------------------------
    requested_action = request.action.lower()
    today_status = sheets_service.get_today_status(request.employee_code)
    
    if requested_action == "check-out":
        if not today_status or not today_status['check_in_time']:
            return {
                "status": "fail", 
                "message": f"{employee_info['full_name']} chưa check-in hôm nay. Không thể check-out!"
            }
        if today_status['check_out_time']:
            return {
                "status": "fail", 
                "message": f"{employee_info['full_name']} đã check-out lúc {today_status['check_out_time']}."
            }
    else: # check-in
        if today_status and today_status['check_in_time']:
            return {
                "status": "fail", 
                "message": f"{employee_info['full_name']} đã check-in lúc {today_status['check_in_time']}. Chọn Check-Out để kết thúc!"
            }
    # -------------------------------------------------------------

    # Perform the action
    if requested_action == "check-out":
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
