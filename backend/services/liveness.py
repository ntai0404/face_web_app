"""
Professional Face Liveness Detection using Frequency Analysis (FFT)
Detects moiré patterns and grid artifacts common in screen captures/spoofs.
"""
import cv2
import numpy as np

class LivenessDetector:
    """
    Detects if a face is real or a digital spoof (photo of screen/print).
    
    Research Strategy:
    1. FFT (Fast Fourier Transform) to detect periodic grid patterns (moiré).
    2. Laplacian Variance to detect blurriness common in low-quality re-captures.
    3. Texture analysis using variation in local intensities.
    """
    
    def __init__(self, model_path: any = None, threshold: float = 0.2):
        self.threshold = threshold
        print("✅ Professional Liveness Detector initialized (Noise-Robust FFT)")
        
    def predict(self, image: np.ndarray) -> tuple[bool, float]:
        if image is None:
            return False, 0.0
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        # Larger crop for better FFT resolution
        size = 120
        cy, cx = h // 2, w // 2
        crop = gray[max(0, cy-size//2):min(h, cy+size//2), max(0, cx-size//2):min(w, cx+size//2)]
        
        f = np.fft.fft2(crop)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-10)
        
        # Calculate energy but ignore the very center (DC) and global horizontal/vertical axes
        # (which catch flicker/scanlines)
        ch, cw = magnitude_spectrum.shape
        magnitude_spectrum[ch//2-2:ch//2+2, :] = 0  # Ignore horizontal scanlines
        magnitude_spectrum[:, cw//2-2:cw//2+2] = 0  # Ignore vertical scanlines
        
        energy = np.mean(magnitude_spectrum[magnitude_spectrum > 0])
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Heuristics adjusted for webcam noise
        norm_energy = np.clip((energy - 60) / 100, 0, 1)
        norm_blur = np.clip(blur_score / 150, 0, 1) # Leanient blur
        
        # If there's some detail (blur > 5) and not insane grid energy, it's likely real
        liveness_score = (norm_blur * 0.4) + ((1.0 - norm_energy) * 0.6)
        
        is_real = liveness_score > self.threshold or (blur_score > 30 and energy < 150)
        
        print(f"DEBUG Liveness: Energy={energy:.1f}, Blur={blur_score:.1f} -> Score={liveness_score:.2f} ({'REAL' if is_real else 'SPOOF'})")
        
        return is_real, float(liveness_score)
