# Face Attendance System v2.0 🚀

Hệ thống điểm danh khuôn mặt Chuyên nghiệp (Production-Grade) sử dụng các mô hình AI/ML hiện đại để đảm bảo độ chính xác và chống giả mạo.

## 🧠 Kiến trúc Thuật toán (AI Pipeline)

Hệ thống không sử dụng một thư viện đơn lẻ mà kết hợp một chuỗi (pipeline) 5 giai đoạn xử lý chuyên sâu:

### 1. Face Detection & Anti-Spoofing (Liveness)
*   **Công nghệ**: `MobileNetV2` (Deep Learning) + Phân tích tần số (FFT).
*   **Chức năng**:
    *   Phát hiện khuôn mặt trong khung hình.
    *   **Lớp bảo vệ**: Phân tích kết cấu da và quang phổ để phân biệt **Mặt thật** vs **Mặt giả** (ảnh in, màn hình điện thoại).
    *   Nếu phát hiện giả mạo, hệ thống từ chối xử lý ngay lập tức.

### 2. Face Alignment (Căn chỉnh)
*   **Công nghệ**: `MTCNN` (Multi-task Cascaded Convolutional Networks).
*   **Chức năng**:
    *   Xác định toạ độ mắt, mũi, miệng.
    *   Xoay và cắt (crop) khuôn mặt cho thẳng trục (`Alignment`).
    *   **Tại sao cần?**: FaceNet hoạt động kém nếu mặt bị nghiêng. Bước này giúp chuẩn hóa dữ liệu đầu vào.

### 3. Feature Extraction (Trích xuất đặc trưng)
*   **Công nghệ**: `FaceNet` (Inception ResNet v1).
*   **Chức năng**:
    *   Biến đổi hình ảnh khuôn mặt (đã căn chỉnh) thành một vector toán học 128 chiều (`Embedding Vector`).
    *   **Đặc điểm**: Các vector của cùng một người sẽ nằm gần nhau trong không gian Euclide, của người khác nhau sẽ nằm xa nhau.

### 4. Classification (Định danh)
*   **Công nghệ**: `SVM` (Support Vector Machine) với Linear Kernel.
*   **Chức năng**:
    *   Đây là "bộ não" quyết định danh tính. SVM tìm ra ranh giới siêu phẳng (Hyperplane) tối ưu để phân chia 95+ nhân viên.
    *   Khác với so sánh khoảng cách đơn thuần, SVM học được các đặc điểm tinh tế giúp phân biệt những người giống nhau.

### 5. Confidence Scoring (Độ tin cậy Lai - Hybrid)
*   **Công nghệ**: `SVM Probability` + `Cosine Similarity`.
*   **Chức năng**:
    *   Kết hợp xác suất từ SVM và đo khoảng cách Cosine với dữ liệu gốc để đưa ra chỉ số % tin cậy cuối cùng (0-100%).
    *   Khắc phục điểm yếu "xác suất loãng" khi số lượng nhân viên tăng cao.

---

## ✨ Tính năng Nổi bật (v2.0)

1.  **Chống Spam Thông Báo**: Hệ thống dừng quét ngay khi nhận diện thành công (`check-in.js`).
2.  **Google Sheets Sync (Async)**: Dữ liệu chấm công được ghi ngầm vào Google Sheets mà không làm đơ ứng dụng (`Run in Background`).
3.  **Upload Demo Tab**: Cho phép tải ảnh file để test nhận diện (Bypass camera noise).
4.  **Absolute Persistence**: Cơ chế lưu trữ "cứng" đảm bảo không bao giờ mất dữ liệu đăng ký mới.

## 🛠️ Cài đặt & Chạy

1.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Chạy Server**:
    ```bash
    python -m backend.main
    ```

3.  **Truy cập**:
    *   URL: `http://localhost:8000`

---

## 👨‍💼 Quản trị & Bảo trì

### 1. Xóa nhân viên và huấn luyện lại AI
Để xóa hoàn toàn dấu vết của một nhân viên (ảnh, thông tin, dữ liệu AI), hãy chạy lệnh:
```bash
python cleanup_employee.py --code "MÃ_NHÂN_VIÊN"
```
*Lưu ý: Hệ thống sẽ tự động xóa thư mục ảnh và huấn luyện lại các model SVM/KNN để cập nhật danh sách mới.*

### 2. Quản lý Google Sheets
Mọi dữ liệu chấm công được đồng bộ trực tiếp tại link Google Sheet bạn đã cấu hình trong `ggsheet-key.json`.


---
**Tác giả**: [Your Name/Team Name]
**Phiên bản**: 2.0.0
