"""
Feature Extraction using FaceNet (via face_recognition library)
"""
import cv2
import numpy as np
from pathlib import Path
import face_recognition

class FaceNetExtractor:
    """
    Extract 128-dimensional face embeddings using face_recognition library
    
    This uses dlib's ResNet model trained on ~3 million faces
    Reference: https://github.com/ageitgey/face_recognition
    """
    
    def __init__(self, model_path: Path | None = None):
        """
        Initialize FaceNet extractor
        
        Args:
            model_path: Not used - face_recognition has built-in model
        """
        # face_recognition library has built-in pre-trained model
        # No need to load external weights
        print("✅ FaceNet Extractor initialized (using face_recognition dlib ResNet)")
    
    def extract(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract 128-d embedding from face image
        
        Args:
            face_image: Aligned face image (BGR format from OpenCV)
        
        Returns:
            128-dimensional embedding vector
        """
        if face_image is None or face_image.size == 0:
            return None

        # --- ROBUST CONVERSION FILTER ---
        # 1. Ensure 8-bit depth (Fixes "must be 8bit gray or RGB image")
        if face_image.dtype != np.uint8:
            face_image = cv2.convertScaleAbs(face_image)

        # 2. Ensure exactly 3 channels (Handle RGBA/Grayscale) 
        if len(face_image.shape) == 2:
            # Grayscale to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
        elif face_image.shape[2] == 4:
            # RGBA to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGRA2RGB)
        else:
            # Standard BGR to RGB
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Ensure image is contiguous for dlib
        rgb_image = np.ascontiguousarray(rgb_image)
        # ---------------------------------
        
        # Get face encodings (128-d embeddings)
        # Since the image is already aligned and cropped, we tell dlib the whole image is a face
        height, width = rgb_image.shape[:2]
        face_location = (0, width, height, 0)  # top, right, bottom, left
        
        encodings = face_recognition.face_encodings(rgb_image, known_face_locations=[face_location], num_jitters=1)
        
        if len(encodings) == 0:
            return None
        
        # Return encoding
        embedding = encodings[0]
        
        # Ensure it's a numpy array with correct shape
        return np.array(embedding, dtype=np.float64)
    
    def extract_batch(self, face_images: list[np.ndarray]) -> list[np.ndarray]:
        """
        Extract embeddings for multiple faces (batch processing)
        
        Args:
            face_images: List of face images
        
        Returns:
            List of 128-d embeddings
        """
        embeddings = []
        for img in face_images:
            emb = self.extract(img)
            if emb is not None:
                embeddings.append(emb)
        
        return embeddings
