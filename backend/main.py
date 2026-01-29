"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from backend.config import ALLOWED_ORIGINS, API_HOST, API_PORT, EMPLOYEES_METADATA_PATH
from backend.utils.metadata import EmployeesMetadata

# Import API routers
from backend.api import check_in, register, logs, attendance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events: startup and shutdown
    Dùng để load models một lần khi khởi động server
    """
    # Startup
    print("🚀 Starting Face Attendance System...")
    
    # Initialize metadata (replaces database)
    print("📋 Loading employees metadata...")
    app.state.metadata = EmployeesMetadata(EMPLOYEES_METADATA_PATH)
    
    # Load AI models - Lazy loading with fallbacks
    from backend.services.liveness import LivenessDetector
    from backend.services.alignment import FaceAligner
    from backend.services.extraction import FaceNetExtractor
    from backend.services.classifier import SVMClassifier
    from backend.services.knn_classifier import KNNClassifier
    from backend.config import (
        LIVENESS_MODEL_PATH,
        FACENET_MODEL_PATH,
        SVM_MODEL_PATH,
        LIVENESS_THRESHOLD,
        SVM_CONFIDENCE_THRESHOLD,
        MODELS_DIR
    )
    
    print("📦 Loading AI services...")
    
    # Initialize services (with fallback to dummies if models not available)
    # Initialize services (with fallback to dummies if models not available)
    from backend.services.sheets import GoogleSheetsService
    app.state.sheets_service = GoogleSheetsService()
    app.state.sheets_service.connect()
    
    app.state.liveness_detector = LivenessDetector(LIVENESS_MODEL_PATH, LIVENESS_THRESHOLD)
    app.state.face_aligner = FaceAligner()
    app.state.facenet_extractor = FaceNetExtractor(FACENET_MODEL_PATH)
    app.state.svm_classifier = SVMClassifier(SVM_MODEL_PATH, SVM_CONFIDENCE_THRESHOLD)
    app.state.knn_classifier = KNNClassifier(MODELS_DIR / "knn_classifier.pkl", n_neighbors=1)
    
    print("✅ All models loaded successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Face Attendance System",
    description="Hệ thống điểm danh khuôn mặt với Liveness Detection + SVM",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files và templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===================== ROUTES =====================

# ===================== ROUTES =====================

@app.get("/")
async def root():
    """Main page - serve HTML"""
    from fastapi.responses import HTMLResponse
    with open("templates/index.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check API endpoint"""
    return {
        "status": "running",
        "message": "Face Attendance API v2.0",
        "endpoints": {
            "check_in": "/api/check-in",
            "register": "/api/register",
            "logs": "/api/logs/recent"
        }
    }

# Include API routers
app.include_router(check_in.router, prefix="/api", tags=["check-in"])
app.include_router(register.router, prefix="/api", tags=["register"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
app.include_router(attendance.router, prefix="/api", tags=["attendance"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )
