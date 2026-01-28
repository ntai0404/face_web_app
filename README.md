# Face Recognition Attendance System

## Khởi động server

```bash
python -m backend.main
```

Sau đó mở trình duyệt: http://localhost:8000

---

## Cấu trúc file quan trọng

```
face-web-app/
├── employees_metadata.json          # Data 95 nhân viên + embeddings
├── models/
│   ├── classifier.pkl               # SVM model đã train
│   ├── confusion_matrix.png         # Confusion matrix
│   ├── confidence_distribution.png  # Confidence chart
│   └── samples_distribution.png     # Samples chart
├── dataset/                         # 95 thư mục ảnh training
├── backend/
│   ├── main.py                      # FastAPI server
│   ├── services/                    # AI services
│   └── api/                         # API endpoints
└── templates/
    └── index.html                   # Web UI (3 tabs)
```

---

## API Endpoints

- `GET /` - Web UI
- `POST /api/check-in` - Auto face recognition
- `POST /api/register` - Đăng ký user mới + retrain
- `GET /api/health` - Health check

---

## Tech Stack

- **Backend:** FastAPI + Python 3.11
- **AI:** face_recognition (dlib ResNet) + SVM
- **Frontend:** HTML/CSS/JS + MediaPipe CDN
- **Data:** JSON metadata (không dùng database)
