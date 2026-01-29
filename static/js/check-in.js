/**
 * CHECK-IN.JS - Auto Face Recognition (Continuous Detection)
 */

let checkinStream = null;
let isScanning = false;
let scanInterval = null;
let lastCheckInTime = 0;
const SCAN_INTERVAL_MS = 2000; // Quét mỗi 2 giây
const COOLDOWN_MS = 10000; // Cooldown 10 giây sau mỗi lần check-in thành công

const checkinVideo = document.getElementById('checkin-video');
const checkinCanvas = document.getElementById('checkin-canvas');
const startCheckinBtn = document.getElementById('start-checkin-camera');
const stopCheckinBtn = document.getElementById('stop-checkin-camera');
const scanningOverlay = document.getElementById('scanning-overlay');
const checkinStatus = document.getElementById('checkin-status');
const statusIcon = document.querySelector('.status-icon');
const statusMessage = document.querySelector('.status-message');
const checkinResult = document.getElementById('checkin-result');
const checkinInfo = document.getElementById('checkin-info');

// Start auto-detection
startCheckinBtn.addEventListener('click', async () => {
    try {
        // Request camera access
        checkinStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: 640, height: 480 }
        });
        checkinVideo.srcObject = checkinStream;

        // Update UI
        startCheckinBtn.style.display = 'none';
        stopCheckinBtn.style.display = 'inline-block';
        scanningOverlay.style.display = 'flex';
        checkinStatus.style.display = 'block';
        checkinResult.style.display = 'none';

        updateStatus('🔍', 'Đang quét khuôn mặt...', 'scanning');

        // Start continuous scanning
        isScanning = true;
        startContinuousScanning();

    } catch (error) {
        alert('Không thể truy cập camera: ' + error.message);
    }
});

// Stop scanning
stopCheckinBtn.addEventListener('click', () => {
    stopScanning();
});

// Start continuous scanning loop
function startContinuousScanning() {
    if (!isScanning) return;

    scanInterval = setInterval(async () => {
        if (!isScanning) return;

        // Check cooldown
        const now = Date.now();
        if (lastCheckInTime > 0 && (now - lastCheckInTime) < COOLDOWN_MS) {
            const remainingSeconds = Math.ceil((COOLDOWN_MS - (now - lastCheckInTime)) / 1000);
            updateStatus('⏳', `Chờ ${remainingSeconds}s để check-in lại...`, 'cooldown');
            return;
        }

        // Capture frame and recognize
        await captureAndRecognize();

    }, SCAN_INTERVAL_MS);
}

// Capture frame and send to API
async function captureAndRecognize() {
    try {
        updateStatus('🔍', 'Đang nhận diện...', 'scanning');

        // Capture frame from video
        const context = checkinCanvas.getContext('2d');
        checkinCanvas.width = checkinVideo.videoWidth;
        checkinCanvas.height = checkinVideo.videoHeight;
        context.drawImage(checkinVideo, 0, 0);

        // Convert to base64
        const imageData = checkinCanvas.toDataURL('image/jpeg', 0.90);

        // Send to backend API
        const response = await fetch('/api/check-in', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const result = await response.json();

        // Handle result
        if (result.status === 'success') {
            // Success - STOP SCANNING PERMANENTLY (User Request)
            isScanning = false;
            if (scanInterval) clearInterval(scanInterval);
            if (checkinStream) {
                checkinStream.getTracks().forEach(track => track.stop());
            }

            updateStatus('✅', `Check-in thành công: ${result.employee_name}!`, 'success');
            displayResult(result, true);

            // Show "Continue" button
            startCheckinBtn.textContent = "Quét tiếp (Scan Next)";
            startCheckinBtn.style.display = 'inline-block';
            stopCheckinBtn.style.display = 'none';
            scanningOverlay.style.display = 'none';

        } else if (result.message.includes('Unknown')) {
            updateStatus('❓', 'Không nhận diện được - vui lòng đăng ký trước', 'unknown');
        } else {
            updateStatus('⚠️', result.message || 'Tiếp tục quét...', 'scanning');
        }

    } catch (error) {
        console.error('Recognition error:', error);
        updateStatus('⚠️', 'Lỗi kết nối - thử lại...', 'error');
    }
}

// Update status display
function updateStatus(icon, message, type) {
    statusIcon.textContent = icon;
    statusMessage.textContent = message;

    // Update status color
    checkinStatus.className = 'status-text status-' + type;
}

// Display result
function displayResult(result, isSuccess) {
    checkinResult.style.display = 'block';

    if (isSuccess) {
        checkinResult.className = 'result-box success';

        // Debug: Log the full result to console
        console.log('Check-in result:', result);

        // Prepare dual-brain display (side-by-side)
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
        } else {
            console.warn('Dual-brain predictions not found in response');
        }

        checkinInfo.innerHTML = `
            <h3>✅ Check-in thành công!</h3>
            <p><strong>Nhân viên:</strong> ${result.employee_name}</p>
            <p><strong>Mã NV:</strong> ${result.employee_code}</p>
            <p><strong>Độ tin cậy:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
            <p><strong>Liveness:</strong> ${(result.liveness_score * 100).toFixed(1)}%</p>
            <p><strong>Thời gian:</strong> ${new Date(result.timestamp).toLocaleString('vi-VN')}</p>
            ${brainInfo}
        `;
    } else {
        checkinResult.className = 'result-box error';
        checkinInfo.innerHTML = `
            <h3>❌ Check-in thất bại</h3>
            <p>${result.message}</p>
        `;
    }
}

// Stop scanning
function stopScanning() {
    isScanning = false;

    if (scanInterval) {
        clearInterval(scanInterval);
        scanInterval = null;
    }

    if (checkinStream) {
        checkinStream.getTracks().forEach(track => track.stop());
        checkinStream = null;
    }

    // Reset UI
    startCheckinBtn.style.display = 'inline-block';
    stopCheckinBtn.style.display = 'none';
    scanningOverlay.style.display = 'none';
    checkinStatus.style.display = 'none';
    checkinResult.style.display = 'none';

    lastCheckInTime = 0;
}
