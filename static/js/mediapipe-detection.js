/**
 * MEDIAPIPE-DETECTION.JS
 * Client-side face detection using MediaPipe (optional, for validation)
 */

class MediaPipeFaceDetector {
    constructor() {
        this.faceDetection = null;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        try {
            // Initialize MediaPipe Face Detection
            this.faceDetection = new FaceDetection({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
                }
            });

            this.faceDetection.setOptions({
                model: 'short',
                minDetectionConfidence: 0.5
            });

            this.initialized = true;
            console.log('✅ MediaPipe Face Detection initialized');
        } catch (error) {
            console.warn('⚠️ MediaPipe not available:', error);
            this.initialized = false;
        }
    }

    async detectFace(imageElement) {
        if (!this.initialized) {
            return { detected: true, message: 'MediaPipe not initialized, skipping validation' };
        }

        return new Promise((resolve) => {
            this.faceDetection.onResults((results) => {
                if (results.detections && results.detections.length > 0) {
                    resolve({ detected: true, count: results.detections.length });
                } else {
                    resolve({ detected: false, message: 'No face detected' });
                }
            });

            this.faceDetection.send({ image: imageElement });
        });
    }
}

// Export singleton instance
const mediapipeDetector = new MediaPipeFaceDetector();
