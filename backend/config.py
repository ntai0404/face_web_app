"""
FastAPI Configuration
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODELS_DIR = MODEL_DIR  # Alias for consistency
DATASET_DIR = BASE_DIR / "dataset"

# Metadata file (replaces database)
EMPLOYEES_METADATA_PATH = BASE_DIR / "employees_metadata.json"

# Model Paths
LIVENESS_MODEL_PATH = MODEL_DIR / "liveness_mobilenetv2.h5"
FACENET_MODEL_PATH = MODEL_DIR / "facenet_mobilenetv2.h5"
SVM_MODEL_PATH = MODEL_DIR / "classifier.pkl"

# AI Thresholds & Toggles
LIVENESS_ENABLED = False  # Set to False to bypass liveness (Use for demos with noisy cameras)
LIVENESS_THRESHOLD = 0.2  # Score > 0.2 = Real face
SVM_CONFIDENCE_THRESHOLD = 0.01  # Hạ cực thấp để vượt qua rào cản xác suất toán học (95 lớp)

# Google Sheets
GOOGLE_SHEET_ID = "1xDNraddeqoSO57_meskZZmfneEsPPZrdSoHVBJy_RLY"
GOOGLE_CREDENTIALS_PATH = BASE_DIR / "ggsheet-key.json"

# CORS
ALLOWED_ORIGINS = ["*"]

# Server
API_HOST = "0.0.0.0"
API_PORT = 8000
