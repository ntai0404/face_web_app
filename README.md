# Hướng Dẫn Sử Dụng Face Recognition Web App

Ứng dụng web nhận diện khuôn mặt tích hợp nhận diện danh tính và phân tích cảm xúc sử dụng Flask, OpenCV, và DeepFace.

## 📋 Yêu cầu hệ thống

Trước khi chạy ứng dụng, hãy đảm bảo bạn đã cài đặt Python và các thư viện sau:

```bash
pip install flask face_recognition opencv-python scikit-learn deepface
```

## 🛠️ Cài đặt và Khởi tạo

1. **Chuẩn bị dữ liệu (Dataset):**
   - Tạo thư mục `dataset/` trong thư mục gốc của dự án.
   - Với mỗi người cần nhận diện, tạo một thư mục con mang tên người đó (ví dụ: `dataset/Nguyen_Van_A/`).
   - Copy các ảnh khuôn mặt của người đó vào thư mục tương ứng (càng nhiều ảnh ở nhiều góc độ khác nhau thì độ chính xác càng cao).

2. **Huấn luyện mô hình (Training):**
   - Bạn có thể huấn luyện mô hình bằng cách chạy file `train/knn_train.py` hoặc nhấn nút **Train Model** trên giao diện web.
   - Kết quả huấn luyện sẽ được lưu vào file `knn_model.pkl`.

## 🚀 Chạy ứng dụng

Khởi động server Flask bằng lệnh:

```bash
python app.py
```

Truy cập địa chỉ `http://127.0.0.1:5000` trên trình duyệt để bắt đầu sử dụng.

## 🔍 Các tính năng chính

### 1. Nhận diện trực tiếp qua Camera
- Truy cập menu **Camera**.
- Hệ thống sẽ sử dụng webcam để nhận diện khuôn mặt và cảm xúc theo thời gian thực.
- Tên người (nếu có trong dataset) và cảm xúc sẽ hiển thị trực tiếp trên khung hình.

### 2. Nhận diện qua ảnh tải lên
- Truy cập menu **Recognize from Image**.
- Tải lên một file ảnh chứa khuôn mặt.
- Hệ thống sẽ phân tích và trả về kết quả gồm: Tên, khoảng cách tương đồng (độ tin cậy) và cảm xúc của từng người trong ảnh.

### 3. Nhận diện cảm xúc
- Hệ thống tự động phân tích cảm xúc (vui, buồn, tức giận, ngạc nhiên...) cho mỗi khuôn mặt được phát hiện bằng thư viện `DeepFace`.

## ⚠️ Lưu ý
- Đảm bảo môi trường đủ ánh sáng khi sử dụng camera.
- Khoảng cách tương đồng (distance) càng nhỏ (~ < 0.5) thì độ chính xác nhận diện danh tính càng cao.
