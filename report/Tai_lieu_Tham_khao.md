# TÀI LIỆU THAM KHẢO & CƠ SỞ KHOA HỌC
**Hệ thống:** Face Attendance System v2.2

Để đảm bảo tính khách quan và khoa học, hệ thống được xây dựng dựa trên các nghiên cứu và công nghệ đã được công nhận toàn cầu trong lĩnh vực Thị giác máy tính (Computer Vision).

## 1. Công nghệ Nhận diện & Trích xuất đặc trưng
- **dlib ResNet-34:** 
    - *Nguồn:* King, D.E., "Dlib-ml: A Machine Learning Toolkit", Journal of Machine Learning Research, 2009.
    - *Chi tiết:* Mô hình Residual Network (ResNet) 34 lớp được huấn luyện trên dataset 3 triệu khuôn mặt, đạt độ chính xác 99.38% trên tập dữ liệu chuẩn LFW (Labeled Faces in the Wild).
- **FaceNet:**
    - *Nguồn:* Schroff, F., et al., "FaceNet: A Unified Embedding for Face Recognition and Clustering", CVPR, 2015.
    - *Nguyên lý:* Sử dụng hàm lỗi Triplet Loss để ánh xạ khuôn mặt vào không gian Vector 128 chiều sao cho khoảng cách Euclide phản ánh trực tiếp độ tương đồng.

## 2. Công nghệ Căn chỉnh & Phát hiện
- **MTCNN (Multi-task Cascaded Convolutional Networks):**
    - *Nguồn:* Zhang, K., et al., "Joint Face Detection and Alignment Using Multitask Cascaded Convolutional Networks", IEEE Signal Processing Letters, 2016.
    - *Chức năng:* Quy trình 3 tầng (P-Net, R-Net, O-Net) giúp hệ thống phát hiện khuôn mặt và 5 điểm mốc (mắt, mũi, miệng) với độ chính xác cực cao ngay cả khi mặt bị che khuất một phần.
- **MediaPipe Face Detection:**
    - *Cơ sở:* Google AI Research - "BlazeFace: Sub-millisecond Neural Face Detection on Mobile GPUs", 2019.
    - *Ưu điểm:* Tốc độ xử lý siêu nhanh trên trình duyệt mà không cần tài nguyên mạnh.

## 3. Thuật toán phân loại & Hạ tầng
- **SVM (Support Vector Machine):**
    - *Cơ sở:* Thư viện Scikit-learn (Pedregosa et al., JMLR 2011). 
    - *Lý do chọn:* SVM được chứng minh là hiệu quả nhất khi làm việc với các Vector Embedding trong bài toán nhận diện 1-nhiều (N-class classification).
- **FastAPI Framework:**
    - *Nguồn:* Sebastian Ramírez (tiangolo).
    - *Đặc điểm:* Dựa trên tiêu chuẩn Starlette và Pydantic, cho phép xử lý đồng thời hàng ngàn Request với độ trễ thấp nhất trong thế giới Python.

---
*Tài liệu này cung cấp nền tảng lý thuyết cho việc triển khai hệ thống nhận diện khuôn mặt tại doanh nghiệp.*
