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

class CheckInResponse(BaseModel):
    """Response cho API check-in"""
    status: str  # "success" hoặc "fail"
    employee_code: str | None = None
    employee_name: str | None = None
    confidence: float | None = None
    liveness_score: float | None = None
    message: str | None = None
    timestamp: str = None
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
        
        # Use KNN as primary (based on health check results)
        employee_code = knn_code
        confidence = knn_conf
        
        if employee_code == "Unknown":
            return CheckInResponse(
                status="fail",
                message="Unknown person - Please register first",
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
        
        # Log to Google Sheets (Async)
        sheets_service = app_request.app.state.sheets_service
        if sheets_service:
            background_tasks.add_task(
                sheets_service.log_checkin,
                employee_code=employee_code,
                name=employee_info['full_name'],
                confidence=confidence,
                liveness=liveness_score,
                status="Success"
            )
        
        return CheckInResponse(
            status="success",
            employee_code=employee_code,
            employee_name=employee_info['full_name'],
            confidence=confidence,
            liveness_score=liveness_score,
            message=f"Welcome, {employee_info['full_name']}!",
            svm_prediction={"code": svm_code, "confidence": svm_conf},
            knn_prediction={"code": knn_code, "confidence": knn_conf},
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
