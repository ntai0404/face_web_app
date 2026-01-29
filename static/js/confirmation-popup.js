// Confirmation popup function
let confirmationTimeout = null;

function showConfirmationPopup(result) {
    // Create popup overlay
    const overlay = document.createElement('div');
    overlay.id = 'confirmation-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;

    const popup = document.createElement('div');
    popup.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        max-width: 450px;
        text-align: center;
        color: white;
        animation: slideIn 0.3s ease;
    `;

    const actionIcon = result.action_type === 'check-out' ? '👋' : '✅';
    const actionText = result.action_type === 'check-out' ? 'CHECK-OUT' : 'CHECK-IN';
    const actionColor = result.action_type === 'check-out' ? '#FF9800' : '#4CAF50';

    popup.innerHTML = `
        <h2 style="margin: 0 0 20px 0; font-size: 2em;">${actionIcon} Xác nhận danh tính</h2>
        <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin: 0 0 10px 0; font-size: 1.3em; font-weight: bold;">${result.employee_name}</p>
            <p style="margin: 0 0 5px 0; font-size: 0.9em; opacity: 0.9;">Mã NV: ${result.employee_code}</p>
            <p style="margin: 0; font-size: 1.1em; color: ${actionColor}; font-weight: bold;">${actionText}</p>
        </div>
        <p style="margin: 0 0 20px 0; font-size: 1em; opacity: 0.9;">Đây có phải là bạn không?</p>
        <div style="display: flex; gap: 15px; justify-content: center;">
            <button id="confirm-yes" style="
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            ">✅ Đúng, là tôi</button>
            <button id="confirm-no" style="
                padding: 15px 30px;
                background: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            ">❌ Không phải</button>
        </div>
        <p id="countdown" style="margin: 15px 0 0 0; font-size: 0.85em; opacity: 0.7;">Tự động hủy sau <span id="timer">10</span>s</p>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Countdown timer
    let timeLeft = 10;
    const timerSpan = document.getElementById('timer');
    const countdownInterval = setInterval(() => {
        timeLeft--;
        timerSpan.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            handleConfirmationCancel(overlay);
        }
    }, 1000);

    // Event listeners
    document.getElementById('confirm-yes').addEventListener('click', () => {
        clearInterval(countdownInterval);
        handleConfirmationYes(result, overlay);
    });

    document.getElementById('confirm-no').addEventListener('click', () => {
        clearInterval(countdownInterval);
        handleConfirmationCancel(overlay);
    });

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        #confirm-yes:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(76,175,80,0.4); }
        #confirm-no:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(244,67,54,0.4); }
    `;
    document.head.appendChild(style);
}

function handleConfirmationYes(result, overlay) {
    // Remove popup
    overlay.remove();

    // Call backend to confirm and log attendance
    fetch('/api/confirm-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            employee_code: result.employee_code,
            action: result.action_type,
            confidence: result.confidence,
            liveness_score: result.liveness_score
        })
    })
        .then(response => response.json())
        .then(confirmResult => {
            if (confirmResult.status === 'success') {
                // Show success and display result
                updateStatus('✅', confirmResult.message, 'success');
                displayResult(result, true);
            } else {
                updateStatus('❌', confirmResult.message || 'Lỗi xác nhận', 'error');
            }
        })
        .catch(error => {
            console.error('Confirmation error:', error);
            updateStatus('❌', 'Lỗi kết nối - Vui lòng thử lại', 'error');
        });
}

function handleConfirmationCancel(overlay) {
    // Remove popup
    overlay.remove();

    // Show cancelled message
    updateStatus('❌', 'Đã hủy - Vui lòng quét lại nếu cần', 'error');
}
