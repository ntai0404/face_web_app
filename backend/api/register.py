"""
Register API Endpoint
POST /api/register
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import base64
import cv2
import numpy as np
from typing import List
import os
from pathlib import Path

from backend.config import DATASET_DIR, LIVENESS_ENABLED

router = APIRouter()

class RegisterRequest(BaseModel):
    """Request body cho API register"""
    employee_code: str
    full_name: str
    department: str | None = "Default"
    images: List[str]  # List of base64 encoded images (3-15 ảnh)

class RegisterResponse(BaseModel):
    """Response cho API register"""
    status: str
    message: str
    employee_code: str | None = None
    images_processed: int = 0

@router.post("/register", response_model=RegisterResponse)
async def register_employee(
    request: RegisterRequest,
    app_request: Request
):
    """
    API Đăng ký nhân viên mới
    
    Processing:
    1. Validate input
    2. Create employee folder in dataset/
    3. Process each image:
       - Liveness Detection
       - Face Alignment
       - Feature Extraction
       - Save to metadata JSON
       - Save image to dataset folder
    4. Retrain SVM model với toàn bộ embeddings
    """
    
    try:
        # Step 1: Validate input
        if len(request.images) < 3:
            raise HTTPException(
                status_code=400,
                detail="Cần tối thiểu 3 ảnh để đăng ký nhân viên mới"
            )
        
        # Get services from app state
        metadata = app_request.app.state.metadata
        liveness_detector = app_request.app.state.liveness_detector
        face_aligner = app_request.app.state.face_aligner
        facenet_extractor = app_request.app.state.facenet_extractor
        svm_classifier = app_request.app.state.svm_classifier
        
        # Check if employee already exists
        if metadata.employee_exists(request.employee_code):
            raise HTTPException(
                status_code=400,
                detail=f"Nhân viên với mã {request.employee_code} đã tồn tại"
            )
        
        # Step 2: Create employee folder in dataset
        # Sanitize folder name (remove Vietnamese diacritics for Windows compatibility)
        import unicodedata
        def remove_accents(text):
            """Remove Vietnamese accents for safe folder names"""
            nfd = unicodedata.normalize('NFD', text)
            return ''.join([c for c in nfd if unicodedata.category(c) != 'Mn'])
        
        safe_folder_name = remove_accents(request.full_name).replace(' ', '_')
        employee_folder = Path(DATASET_DIR) / safe_folder_name
        employee_folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created folder: {employee_folder}")
        
        # Create employee in metadata
        metadata.create_employee(
            employee_code=request.employee_code,
            full_name=request.full_name,
            department=request.department
        )
        
        # Step 3: Process each image
        processed_count = 0
        failed_images = []
        
        for idx, image_b64 in enumerate(request.images):
            try:
                # Decode image
                if ',' in image_b64:
                    image_data = image_b64.split(',')[1]
                else:
                    image_data = image_b64
                
                img_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(img_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    failed_images.append(f"Image {idx+1}: Cannot decode")
                    continue
                
                # Liveness Detection
                if LIVENESS_ENABLED:
                    is_real, liveness_score = liveness_detector.predict(image)
                else:
                    is_real, liveness_score = True, 1.0  # Bypass for demo
                
                if not is_real:
                    failed_images.append(f"Image {idx+1}: Spoof detected")
                    continue
                
                # Face Alignment
                aligned_face, _ = face_aligner.align(image)
                if aligned_face is None:
                    failed_images.append(f"Image {idx+1}: No face detected")
                    continue
                
                # Feature Extraction
                embedding = facenet_extractor.extract(aligned_face)
                
                # Save embedding to metadata
                metadata.add_embedding(request.employee_code, embedding)
                
                # Save image to dataset folder (Ensure absolute path + no accents)
                img_filename = f"{safe_folder_name}_{processed_count + 1}.jpg"
                img_path = (employee_folder / img_filename).resolve()
                
                success = cv2.imwrite(str(img_path), image)
                if not success:
                    print(f"❌ Failed to save image to {img_path}")
                    failed_images.append(f"Image {idx+1}: Disk write failed")
                    continue
                
                # Verify file exists
                if not img_path.exists():
                     print(f"⚠️ Warning: imwrite returned True but file NOT FOUND at {img_path}")
                     failed_images.append(f"Image {idx+1}: Verify save failed")
                     continue

                print(f"📸 Saved image: {img_path}")
                processed_count += 1
                
            except Exception as e:
                print(f"❌ Error processing image {idx+1}: {str(e)}")
                failed_images.append(f"Image {idx+1}: {str(e)}")
                continue
        
        # Save metadata immediately to disk
        metadata.save()
        print(f"💾 Metadata saved for {request.employee_code}")
        
        # Kiểm tra số lượng ảnh thành công
        if processed_count < 3:
            # Rollback: xóa employee khỏi metadata và folder
            metadata.delete_employee(request.employee_code)
            if employee_folder.exists():
                import shutil
                shutil.rmtree(employee_folder)
            
            raise HTTPException(
                status_code=400,
                detail=f"Chỉ xử lý thành công {processed_count}/{len(request.images)} ảnh. Cần tối thiểu 3 ảnh hợp lệ. Lỗi: {', '.join(failed_images)}"
            )
        
        # Step 4: Retrain both SVM and KNN models
        print(f"🔄 Retraining models with {len(request.images)} new images for {request.full_name}...")
        embeddings, labels = metadata.get_all_embeddings_for_training()
        
        if len(embeddings) > 0:
            # Train SVM
            svm_classifier.train(embeddings, labels)
            print(f"✅ SVM Retrained successfully.")
            
            # Train KNN
            knn_classifier = app_request.app.state.knn_classifier
            knn_classifier.train(embeddings, labels)
            print(f"✅ KNN Retrained successfully.")
            
            print(f"✅ Both models ready. New employee {request.employee_code} is active.")
            
            return RegisterResponse(
                status="success",
                message=f"Đã đăng ký nhân viên {request.full_name} thành công và huấn luyện lại cả 2 model (SVM + KNN)",
                employee_code=request.employee_code,
                images_processed=processed_count
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Không có dữ liệu để huấn luyện SVM"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
