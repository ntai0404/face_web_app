/**
 * CHECK-IN.JS - Continuous Recognition with Intelligent Stopping
 */

let checkinStream = null;
let isScanning = false;
let isProcessing = false;
let scanInterval = null;
let selectedAction = 'check-in';
const SCAN_INTERVAL_MS = 2000;

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

// Action selection
function selectAction(action) {
    selectedAction = action;
    const checkinBtn = document.getElementById('action-checkin-btn');
    const checkoutBtn = document.getElementById('action-checkout-btn');
    if (action === 'check-in') {
        checkinBtn.style.background = '#4CAF50'; checkinBtn.style.color = 'white';
        checkoutBtn.style.background = 'transparent'; checkoutBtn.style.color = '#FF9800';
    } else {
        checkoutBtn.style.background = '#FF9800'; checkoutBtn.style.color = 'white';
        checkinBtn.style.background = 'transparent'; checkinBtn.style.color = '#4CAF50';
    }
}

// Start Scanning
startCheckinBtn.addEventListener('click', async () => {
    try {
        checkinStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: 640, height: 480 }
        });
        checkinVideo.srcObject = checkinStream;

        startCheckinBtn.style.display = 'none';
        stopCheckinBtn.style.display = 'inline-block';
        scanningOverlay.style.display = 'flex';
        checkinStatus.style.display = 'block';
        checkinResult.style.display = 'none';

        updateStatus('🔍', 'Đang quét liên tục...', 'scanning');

        isScanning = true;
        isProcessing = false;

        if (scanInterval) clearInterval(scanInterval);
        scanInterval = setInterval(async () => {
            if (!isScanning || isProcessing) return;
            await captureAndRecognize();
        }, SCAN_INTERVAL_MS);

    } catch (error) {
        console.error(error);
        alert('Lỗi camera: ' + error.message);
    }
});

stopCheckinBtn.addEventListener('click', stopEverything);

async function captureAndRecognize() {
    isProcessing = true;
    updateStatus('⌛', 'Đang phân tích...', 'scanning');

    const context = checkinCanvas.getContext('2d');
    checkinCanvas.width = checkinVideo.videoWidth || 640;
    checkinCanvas.height = checkinVideo.videoHeight || 480;
    context.drawImage(checkinVideo, 0, 0);
    const imageData = checkinCanvas.toDataURL('image/jpeg', 0.8);

    try {
        const response = await fetch('/api/check-in', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData, action: selectedAction })
        });
        const result = await response.json();

        // CRITICAL: If we found a specific employee (success OR identified failure like "Already checked in")
        // we MUST STOP the scanning to let user see and act.
        if (result.employee_code) {
            stopEverything(); // Stop camera and interval immediately

            // SHOW CONFIRMATION POPUP ALWAYS (Validation happens later)
            updateStatus('✅', 'Đã nhận diện!', 'success');
            displayResult(result, true);
            showConfirmationPopup(result);
        } else if (result.status === 'retry') {
            updateStatus('🔄', result.message || 'Thử lại...', 'retry');
            isProcessing = false; // Continue scanning
        } else {
            // "Unknown" or no face
            updateStatus('🔍', result.message || 'Tiếp tục quét...', 'scanning');
            isProcessing = false; // Continue scanning
        }
    } catch (error) {
        console.error("Recognition error:", error);
        updateStatus('⚠️', 'Lỗi kết nối', 'error');
        isProcessing = false;
    }
}

// Stop everything
function stopEverything() {
    isScanning = false;
    isProcessing = false;
    if (scanInterval) { clearInterval(scanInterval); scanInterval = null; }
    if (checkinStream) {
        checkinStream.getTracks().forEach(t => t.stop());
        checkinStream = null;
    }
    checkinVideo.srcObject = null;
    scanningOverlay.style.display = 'none';
    startCheckinBtn.style.display = 'inline-block';
    startCheckinBtn.textContent = "Quét tiếp";
    stopCheckinBtn.style.display = 'none';
}

// Global exposure for tab management
window.stopCheckinCamera = stopEverything;

function updateStatus(icon, message, type) {
    statusIcon.textContent = icon;
    statusMessage.textContent = message;
    checkinStatus.className = 'status-text status-' + type;
}

function displayResult(result, isSuccess) {
    checkinResult.style.display = 'block';
    checkinResult.className = 'result-box ' + (isSuccess ? 'success' : 'error');

    if (isSuccess) {
        checkinInfo.innerHTML = `
            <h3>👤 Kết quả nhận diện</h3>
            <p><strong>Nhân viên:</strong> ${result.employee_name}</p>
            <p><strong>Mã:</strong> ${result.employee_code}</p>
            <p style="color:#4CAF50; font-weight:bold;">Vui lòng xác nhận trên Form!</p>
        `;
    } else {
        checkinInfo.innerHTML = `
            <h3>⚠️ Thông báo</h3>
            <p>${result.message || 'Lỗi không xác định'}</p>
            <p>Nhấp <strong>"Quét tiếp"</strong> nếu bạn muốn thử lại.</p>
        `;
    }
}

// POPUP LOGIC
function showConfirmationPopup(result) {
    const old = document.getElementById('confirmation-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'confirmation-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);display:flex;justify-content:center;align-items:center;z-index:999999;';

    const actionText = result.action_type === 'check-out' ? 'CHECK-OUT' : 'CHECK-IN';
    const actionColor = result.action_type === 'check-out' ? '#FF9800' : '#4CAF50';

    overlay.innerHTML = `
        <div style="background:white; padding:40px; border-radius:15px; text-align:center; max-width:400px; color:#333; box-shadow:0 0 30px rgba(0,0,0,0.5);">
            <h2 style="margin-top:0;">Xác nhận danh tính</h2>
            <div style="margin:20px 0; padding:20px; background:#f8f9fa; border-radius:10px;">
                <p style="font-size:1.5em; font-weight:bold; margin:0;">${result.employee_name}</p>
                <p style="margin:5px 0; color:#666;">Mã: ${result.employee_code}</p>
                <div style="display:inline-block; margin-top:10px; padding:5px 15px; background:${actionColor}; color:white; border-radius:20px; font-weight:bold;">
                    ${actionText}
                </div>
            </div>
            <p>Đây có phải là bạn không?</p>
            <div style="display:flex; gap:15px; justify-content:center; margin-top:25px;">
                <button id="btn-confirm-yes" style="padding:12px 30px; background:#4CAF50; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">Đúng</button>
                <button id="btn-confirm-no" style="padding:12px 30px; background:#e74c3c; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">Không</button>
            </div>
            <p style="margin-top:15px; font-size:0.85em; color:#999;">Đóng sau <span id="pop-timer">10</span>s</p>
        </div>
    `;

    document.body.appendChild(overlay);

    let timeLeft = 10;
    const timer = setInterval(() => {
        timeLeft--;
        const el = document.getElementById('pop-timer');
        if (el) el.textContent = timeLeft;
        if (timeLeft <= 0) { clearInterval(timer); overlay.remove(); }
    }, 1000);

    document.getElementById('btn-confirm-yes').onclick = async () => {
        clearInterval(timer);
        overlay.remove();
        updateStatus('⌛', 'Đang lưu...', 'scanning');
        try {
            const resp = await fetch('/api/confirm-attendance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    employee_code: result.employee_code,
                    action: result.action_type,
                    confidence: result.svm_prediction ? result.svm_prediction.confidence : result.confidence,
                    liveness_score: result.liveness_score
                })
            });
            const res = await resp.json();
            if (res.status === 'success') {
                updateStatus('✅', res.message, 'success');
                displayResult(result, true); // Update box with final confirm message
                checkinInfo.innerHTML = `
                    <div style="text-align:center;">
                        <h2 style="color:#4CAF50;">🎉 Thành công</h2>
                        <p style="font-size:1.1em;">${res.message}</p>
                    </div>
                `;
            } else {
                updateStatus('❌', 'Thất bại', 'error');
                displayResult(res, false); // Show the specific error message (e.g. "Already checked in")
            }
        } catch (e) {
            updateStatus('❌', 'Lỗi ghi nhận', 'error');
        }
    };

    document.getElementById('btn-confirm-no').onclick = () => {
        clearInterval(timer);
        overlay.remove();
        updateStatus('❌', 'Đã hủy', 'error');
    };
}
