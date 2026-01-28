Chào bạn, tôi là Senior Web Solution Architect. Dựa trên tài liệu mô tả hệ thống gốc (Mobile App) và các yêu cầu chuyển đổi công nghệ bạn đưa ra, tôi đã soạn thảo bản Tài liệu Đặc tả Kỹ thuật (Technical Implementation Spec) dưới đây.
Tài liệu này được tối ưu hóa để các AI Coding Agent (Cursor, Copilot) có thể hiểu và sinh mã nguồn chính xác cho môi trường Web.

--------------------------------------------------------------------------------
TECHNICAL IMPLEMENTATION SPECIFICATION
Project: Web-based Face Attendance System (Hệ thống Điểm danh Khuôn mặt trên Web) Version: 1.0.0 Status: Ready for Development
1. TECH STACK & ARCHITECTURE
1.1. High-Level Architecture
Hệ thống chuyển từ mô hình Mobile-First sang Web-Centric. Client chịu trách nhiệm phát hiện khuôn mặt sơ bộ (để giảm tải băng thông), Server chịu trách nhiệm xử lý logic AI chuyên sâu.
1.2. Technology Stack
Frontend (Client-side):
• Core: ReactJS (hoặc HTML5/Vanilla JS tùy chọn).
• Face Detection: MediaPipe Face Detection (Google) - Thay thế Vision Framework của iOS.
    ◦ Nhiệm vụ: Real-time detection trên trình duyệt, crop khuôn mặt, convert sang Base64.
• HTTP Client: Axios/Fetch API.
Backend (Server-side):
• Framework: FastAPI (Python) - Được chọn vì hiệu năng cao và hỗ trợ bất đồng bộ tốt như mô tả trong tài liệu nguồn.
• AI/ML Core:
    ◦ TensorFlow/Keras: Chạy các model Deep Learning (MobileNetV2, FaceNet).
    ◦ Scikit-learn: Triển khai thuật toán SVM (Support Vector Machine) để phân loại danh tính - Thay thế Cosine Similarity.
    ◦ MTCNN: Thư viện mtcnn hoặc facenet-pytorch để căn chỉnh khuôn mặt.
• Database: SQLite + SQLAlchemy (ORM).

--------------------------------------------------------------------------------
2. DATABASE SCHEMA DESIGN (SQLite)
Mặc dù thuật toán nhận diện chuyển sang SVM (lưu trọng số trong file model .pkl), ta vẫn cần Database để quản lý thông tin nhân viên và lưu trữ dự phòng vector (phục vụ việc huấn luyện lại SVM khi có nhân viên mới mà không cần nhân viên cũ chụp lại ảnh).
Table: employees
Column Name
Data Type
Constraints
Description
id
Integer
PK, Auto-increment
ID nội bộ.
employee_code
String
Unique, Not Null
Mã nhân viên (VD: NV001).
full_name
String
Not Null
Tên hiển thị.
created_at
DateTime
Default: Now
Thời gian đăng ký.
Table: face_embeddings (Dùng cho Re-training SVM)
Thay thế bảng users chứa 3 cột embedding cố định trong tài liệu gốc, bảng này cho phép lưu N mẫu training cho mỗi nhân viên để SVM học tốt hơn.
Column Name
Data Type
Constraints
Description
id
Integer
PK
ID bản ghi.
employee_id
Integer
FK -> employees.id
Liên kết nhân viên.
vector
Blob/Pickle
Not Null
Vector đặc trưng (128-d) từ FaceNet.

--------------------------------------------------------------------------------
3. PIPELINE XỬ LÝ ẢNH (BACKEND CORE)
Coder cần triển khai một hàm process_face_pipeline(image_base64) thực hiện tuần tự 3 bước sau. Nếu bất kỳ bước nào thất bại, trả về Exception.
Bước 1: Liveness Detection (Chống giả mạo)
• Input: Ảnh crop từ Client.
• Model: MobileNetV2 (đã fine-tune trên tập CelebA-Spoof).
• Tiền xử lý:
    ◦ Resize ảnh về 224x224 pixels.
    ◦ Chuẩn hóa pixel về khoảng  (chia cho 255).
• Architecture Head (Theo tài liệu gốc):
    ◦ Base: MobileNetV2 (freeze 100 layers đầu).
    ◦ Head: GlobalAveragePooling2D -> Dense(1024, ReLU) -> Dropout(0.5) -> Dense(1, Linear).
• Logic:
    ◦ Output > Threshold (ví dụ 0.5) => Real.
    ◦ Output <= Threshold => Spoof (Trả lỗi ngay lập tức).
Bước 2: Face Alignment (Căn chỉnh)
• Input: Ảnh gốc (đã qua bước Liveness).
• Model: MTCNN (Multi-task Cascaded CNN).
• Nhiệm vụ:
    ◦ Phát hiện lại khuôn mặt để lấy 5 điểm mốc (landmarks): mắt trái, mắt phải, mũi, khóe miệng trái, khóe miệng phải.
    ◦ Affine Transformation: Xoay ảnh sao cho đường nối 2 mắt nằm ngang. Đây là bước quan trọng để FaceNet trích xuất đặc trưng chuẩn xác.
• Output: Ảnh khuôn mặt đã xoay thẳng (Aligned Face).
Bước 3: Feature Extraction (Trích xuất đặc trưng)
• Input: Ảnh đã Align.
• Model: FaceNet (Backbone: MobileNetV2 để tối ưu tốc độ).
• Tiền xử lý: Resize ảnh về kích thước input của FaceNet (thường là 160x160 hoặc 224x224 tùy weights).
• Output: Vector 128 chiều (Embedding).

--------------------------------------------------------------------------------
4. MATCHING STRATEGY (SVM CLASSIFIER)
Thay đổi so với tài liệu gốc: Không dùng Cosine Similarity so sánh 1-1.
• Model: sklearn.svm.SVC (Support Vector Classification).
• Configuration:
    ◦ kernel='linear' hoặc rbf.
    ◦ probability=True (để lấy độ tin cậy).
• Inference (Nhận diện):
    ◦ Đưa vector 128-d vào model SVM.
    ◦ Hàm predict_proba trả về xác suất thuộc về từng class (từng nhân viên).
    ◦ Nếu xác suất cao nhất < Threshold (ví dụ 0.7) => Unknown (Người lạ).
    ◦ Ngược lại => Trả về employee_code.

--------------------------------------------------------------------------------
5. API SPECIFICATION
5.1. API Check-in
• Endpoint: POST /api/check-in
• Request Body:
• Processing Flow:
    1. Decode Base64 -> CV2 Image.
    2. Chạy Pipeline Bước 1 (Liveness). Nếu Spoof -> Return 400 "Spoof Detected".
    3. Chạy Pipeline Bước 2 (MTCNN Align).
    4. Chạy Pipeline Bước 3 (FaceNet Embedding).
    5. Load SVM Model (classifier.pkl).
    6. Predict danh tính.
• Response:
• Hoặc lỗi: {"status": "fail", "reason": "Spoof detected"}.
5.2. API Register (Huấn luyện lại SVM)
• Endpoint: POST /api/register
• Request Body:
• Processing Flow:
    1. Tạo record trong bảng employees.
    2. Với mỗi ảnh:
        ▪ Chạy Pipeline (Liveness -> Align -> Embed).
        ▪ Lưu vector vào bảng face_embeddings.
    3. Trigger Retraining:
        ▪ Load toàn bộ vectors và labels từ bảng face_embeddings.
        ▪ Fit lại model SVC.
        ▪ Lưu model đè lên file classifier.pkl.
• Response: {"status": "success", "message": "User registered and model retrained"}.

--------------------------------------------------------------------------------
6. IMPLEMENTATION GUIDELINES (LƯU Ý CHO CODER)
1. MediaPipe vs MTCNN:
    ◦ Ở Client, dùng MediaPipe chỉ để UX nhanh (vẽ khung hình chữ nhật) và crop sơ bộ.
    ◦ Gửi ảnh crop về Server nên để dư lề (padding) khoảng 20% để MTCNN ở Server có không gian xử lý chính xác các điểm mốc.
2. Xử lý Liveness (MobileNetV2 Custom Head):
    ◦ Coder cần chú ý load đúng weights đã train trên CelebA-Spoof.
    ◦ Lớp cuối cùng của model Liveness phải là Dense(1, activation='linear') như tài liệu mô tả. Khi inference, cần áp dụng hàm sigmoid thủ công hoặc kiểm tra giá trị logits tùy vào cách loss function được cấu hình (from_logits=True).
3. Quản lý Model SVM:
    ◦ SVM cần được retrain mỗi khi có nhân viên mới. Với số lượng nhân viên nhỏ (<1000), việc retrain mất < 1 giây.
    ◦ Sử dụng joblib để save/load model .pkl cho tốc độ cao.
    ◦ Luôn kiểm tra confidence score của SVM. Nếu score thấp, hãy yêu cầu nhân viên thử lại hoặc báo "Không nhận diện được".
4. MTCNN Performance:
    ◦ MTCNN gồm 3 mạng con (P-Net, R-Net, O-Net) chạy tuần tự. Để tối ưu tốc độ trên Server, chỉ khởi tạo (load graph) MTCNN một lần khi khởi động FastAPI (@app.on_event("startup")), không load lại trong mỗi request.
5. Environment:
    ◦ Python 3.9+.
    ◦ Cài đặt opencv-python-headless để tránh lỗi dependencies GUI trên Server.