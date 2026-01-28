"""
Face Alignment using MTCNN (Multi-task Cascaded Convolutional Networks)
"""
import cv2
import numpy as np
from mtcnn import MTCNN

class FaceAligner:
    """
    Detect and align faces using MTCNN
    
    This performs:
    1. Face detection
    2. Landmark localization (eyes, nose, mouth)
    3. Affine transformation to level the eyes
    """
    
    def __init__(self):
        """Initialize MTCNN detector"""
        # Load MTCNN once
        self.detector = MTCNN()
        print("✅ Face Aligner initialized (MTCNN)")
        
    def align(self, image: np.ndarray) -> tuple[np.ndarray | None, dict]:
        """
        Detect face and align it based on eye positions
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Tuple of (aligned_face, landmarks_dict)
        """
        if image is None:
            return None, {}
            
        # Convert BGR to RGB for MTCNN
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.detector.detect_faces(rgb_image)
        
        if not results:
            return None, {}
            
        # Assume the largest face or first detected face
        face_info = results[0]
        keypoints = face_info['keypoints']
        
        left_eye = keypoints['left_eye']
        right_eye = keypoints['right_eye']
        
        # Calculate angle to rotate
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Eyes center
        eye_center = (
            int((left_eye[0] + right_eye[0]) // 2),
            int((left_eye[1] + right_eye[1]) // 2)
        )
        
        # Rotation matrix
        M = cv2.getRotationMatrix2D(eye_center, angle, scale=1.0)
        
        # Rotate image
        h, w = image.shape[:2]
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC)
        
        # Detect face again in the rotated image for cropping or use the original box
        # For simplicity, we'll crop a standard size around the eyes
        bounding_box = face_info['box']
        x, y, width, height = bounding_box
        
        # Ensure box is within image
        x = max(0, x)
        y = max(0, y)
        
        # Crop from rotated image using the original detection box as a guide
        # (Better: re-detect in rotated image, but this is a common approximation)
        aligned_face = rotated[y:y+height, x:x+width]
        
        if aligned_face.size == 0:
            return None, {}
            
        return aligned_face, {"landmarks": keypoints, "status": "success", "angle": angle}
