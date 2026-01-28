
import cv2
import numpy as np
from backend.services.alignment import FaceAligner
import os

def test_alignment():
    print("🚀 Testing REAL MTCNN Alignment...")
    aligner = FaceAligner()
    
    # Find a test image in dataset
    dataset_dir = "dataset"
    test_img_path = None
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.endswith((".jpg", ".png")):
                test_img_path = os.path.join(root, file)
                break
        if test_img_path: break
        
    if not test_img_path:
        print("❌ No images found in dataset/")
        return
        
    print(f"📸 Loading test image: {test_img_path}")
    img = cv2.imread(test_img_path)
    
    if img is None:
        print("❌ Failed to load image")
        return
        
    aligned, info = aligner.align(img)
    
    if aligned is not None:
        print("✅ Alignment SUCCESSFUL")
        print(f"📊 Info: {info}")
        # Save for manual verification if needed
        os.makedirs("models", exist_ok=True)
        cv2.imwrite("models/test_aligned.jpg", aligned)
        print("💾 Saved aligned face to 'models/test_aligned.jpg'")
    else:
        print("❌ Alignment FAILED (No face detected or error)")

if __name__ == "__main__":
    test_alignment()
