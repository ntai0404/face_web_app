/**
 * UPLOAD-DEMO.JS - Manual image upload recognition for demo
 */

document.addEventListener('DOMContentLoaded', () => {
    const uploadInput = document.getElementById('image-upload');
    const dropzone = document.getElementById('upload-dropzone');
    const preview = document.getElementById('upload-preview');
    const dropzoneContent = document.querySelector('.dropzone-content');
    const uploadResult = document.getElementById('upload-result');
    const uploadInfo = document.getElementById('upload-info');

    // Handle file selection
    uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });

    // Drag and drop events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    });

    async function handleFile(file) {
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64Image = e.target.result;
            preview.src = base64Image;
            preview.style.display = 'block';
            dropzoneContent.style.display = 'none';

            // Perform recognition
            performRecognition(base64Image);
        };
        reader.readAsDataURL(file);
    }

    async function performRecognition(base64Image) {
        uploadResult.style.display = 'block';
        uploadResult.className = 'result-box scanning';
        uploadInfo.innerHTML = '<h3>⏳ Đang xử lý...</h3><p>Hệ thống đang trích xuất đặc trưng và đối chiếu danh tính.</p>';

        try {
            const response = await fetch('/api/check-in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64Image })
            });

            const result = await response.json();

            if (result.status === 'success') {
                uploadResult.className = 'result-box success';
                uploadInfo.innerHTML = `
                    <h3>✅ Nhận diện thành công!</h3>
                    <p><strong>Nhân viên:</strong> ${result.employee_name}</p>
                    <p><strong>Mã NV:</strong> ${result.employee_code}</p>
                    <p><strong>Độ tin cậy:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Thời gian:</strong> ${new Date(result.timestamp).toLocaleString('vi-VN')}</p>
                `;
            } else {
                uploadResult.className = 'result-box error';
                uploadInfo.innerHTML = `
                    <h3>❌ Nhận diện thất bại</h3>
                    <p>${result.message}</p>
                    ${result.confidence ? `<p><strong>Độ tin cậy:</strong> ${(result.confidence * 100).toFixed(1)}%</p>` : ''}
                `;
            }
        } catch (error) {
            uploadResult.className = 'result-box error';
            uploadInfo.innerHTML = `<h3>❌ Lỗi hệ thống</h3><p>${error.message}</p>`;
        } finally {
            // Re-enable selecting files
            uploadInput.value = '';
        }
    }
});
