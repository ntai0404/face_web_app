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

                // Prepare dual-brain display (same as check-in tab)
                let brainInfo = '';
                if (result.svm_prediction && result.knn_prediction) {
                    brainInfo = `
                        <div style="margin-top: 15px; padding: 15px; background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(33,150,243,0.1)); border-radius: 8px; border: 2px solid rgba(255,255,255,0.2);">
                            <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 1.1em;">🧠 Dual-Brain Analysis</p>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                <div style="padding: 10px; background: rgba(33,150,243,0.15); border-radius: 5px; text-align: center;">
                                    <p style="margin: 0; font-size: 0.85em; color: #90CAF9;">SVM (Statistical)</p>
                                    <p style="margin: 5px 0; font-size: 1.3em; font-weight: bold;">
                                        ${(result.svm_prediction.confidence * 100).toFixed(1)}%
                                    </p>
                                    <p style="margin: 0; font-size: 0.8em;">
                                        ${result.svm_prediction.code === result.employee_code ? '✓ Match' : '✗ Mismatch'}
                                    </p>
                                </div>
                                <div style="padding: 10px; background: rgba(76,175,80,0.15); border-radius: 5px; text-align: center; border: 2px solid #4CAF50;">
                                    <p style="margin: 0; font-size: 0.85em; color: #A5D6A7;">KNN (Distance)</p>
                                    <p style="margin: 5px 0; font-size: 1.3em; font-weight: bold; color: #4CAF50;">
                                        ${(result.knn_prediction.confidence * 100).toFixed(1)}%
                                    </p>
                                    <p style="margin: 0; font-size: 0.8em;">
                                        ${result.knn_prediction.code === result.employee_code ? '✓ Match' : '✗ Mismatch'} • PRIMARY
                                    </p>
                                </div>
                            </div>
                        </div>
                    `;
                }


                // Determine action icon and title
                const actionIcon = result.action_type === 'check-out' ? '👋' : '✅';
                const actionTitle = result.action_type === 'check-out' ? 'Check-out thành công!' : 'Nhận diện thành công!';

                uploadInfo.innerHTML = `
                    <h3>${actionIcon} ${actionTitle}</h3>
                    <p><strong>Nhân viên:</strong> ${result.employee_name}</p>
                    <p><strong>Mã NV:</strong> ${result.employee_code}</p>
                    <p><strong>Hành động:</strong> <span style="color: ${result.action_type === 'check-out' ? '#FF9800' : '#4CAF50'}; font-weight: bold;">${result.action_type === 'check-out' ? 'CHECK-OUT' : 'CHECK-IN'}</span></p>
                    <p><strong>Độ tin cậy:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
                    <p><strong>Liveness:</strong> ${(result.liveness_score * 100).toFixed(1)}%</p>
                    <p><strong>Thời gian:</strong> ${new Date(result.timestamp).toLocaleString('vi-VN')}</p>
                    ${brainInfo}
                    <button onclick="location.reload()" style="margin-top: 15px; padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        🔄 Test lại
                    </button>
                `;
            } else if (result.status === 'retry') {
                uploadResult.className = 'result-box error';
                uploadInfo.innerHTML = `
                    <h3>🔄 Độ tin cậy chưa đủ</h3>
                    <p>${result.message}</p>
                    <button onclick="location.reload()" style="margin-top: 15px; padding: 10px 20px; background: #FF9800; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        🔄 Thử lại
                    </button>
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
