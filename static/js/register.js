/**
 * REGISTER.JS - Registration page logic
 */

let registerStream = null;
const registerVideo = document.getElementById('register-video');
const registerCanvas = document.getElementById('register-canvas');
const startRegisterBtn = document.getElementById('start-register-camera');
const capturePhotoBtn = document.getElementById('capture-photo');
const submitRegisterBtn = document.getElementById('submit-register');
const photosPreview = document.getElementById('photos-preview');
const photoCountSpan = document.getElementById('photo-count');
const registerResult = document.getElementById('register-result');
const registerInfo = document.getElementById('register-info');

let capturedPhotos = [];
const MAX_PHOTOS = 10;
const MIN_PHOTOS = 3;

// Start camera
startRegisterBtn.addEventListener('click', async () => {
    try {
        registerStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: 640, height: 480 }
        });
        registerVideo.srcObject = registerStream;

        capturePhotoBtn.disabled = false;
        startRegisterBtn.textContent = '🎥 Camera đang bật';
        startRegisterBtn.disabled = true;
    } catch (error) {
        alert('Không thể truy cập camera: ' + error.message);
    }
});

// Capture photo
capturePhotoBtn.addEventListener('click', () => {
    if (capturedPhotos.length >= MAX_PHOTOS) {
        alert(`Đã đủ ${MAX_PHOTOS} ảnh!`);
        return;
    }

    // Capture frame
    const context = registerCanvas.getContext('2d');
    registerCanvas.width = registerVideo.videoWidth;
    registerCanvas.height = registerVideo.videoHeight;
    context.drawImage(registerVideo, 0, 0);

    const imageData = registerCanvas.toDataURL('image/jpeg', 0.95);
    capturedPhotos.push(imageData);

    // Update UI
    updatePhotosPreview();
    photoCountSpan.textContent = capturedPhotos.length;

    // Enable submit if enough photos
    if (capturedPhotos.length >= MIN_PHOTOS) {
        submitRegisterBtn.disabled = false;
    }

    // Disable capture if max reached
    if (capturedPhotos.length >= MAX_PHOTOS) {
        capturePhotoBtn.disabled = true;
    }
});

// Update photos preview
function updatePhotosPreview() {
    photosPreview.innerHTML = '';

    capturedPhotos.forEach((photo, index) => {
        const photoItem = document.createElement('div');
        photoItem.className = 'photo-item';
        photoItem.innerHTML = `
            <img src="${photo}" alt="Photo ${index + 1}">
            <button onclick="removePhoto(${index})">×</button>
        `;
        photosPreview.appendChild(photoItem);
    });
}

// Remove photo
window.removePhoto = function (index) {
    capturedPhotos.splice(index, 1);
    updatePhotosPreview();
    photoCountSpan.textContent = capturedPhotos.length;

    // Update button states
    if (capturedPhotos.length < MIN_PHOTOS) {
        submitRegisterBtn.disabled = true;
    }
    if (capturedPhotos.length < MAX_PHOTOS) {
        capturePhotoBtn.disabled = false;
    }
};

// Submit registration
submitRegisterBtn.addEventListener('click', async () => {
    const employeeCode = document.getElementById('employee-code').value.trim();
    const fullName = document.getElementById('full-name').value.trim();
    const department = document.getElementById('department').value.trim() || 'Default';

    if (!employeeCode || !fullName) {
        alert('Vui lòng nhập đầy đủ thông tin!');
        return;
    }

    if (capturedPhotos.length < MIN_PHOTOS) {
        alert(`Cần tối thiểu ${MIN_PHOTOS} ảnh!`);
        return;
    }

    // Disable button
    submitRegisterBtn.disabled = true;
    submitRegisterBtn.textContent = '⏳ Đang xử lý & train model...';

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_code: employeeCode,
                full_name: fullName,
                department: department,
                images: capturedPhotos
            })
        });

        const result = await response.json();

        // Display result
        registerResult.style.display = 'block';

        if (result.status === 'success') {
            registerResult.className = 'result-box success';
            registerInfo.innerHTML = `
                <h3>✅ Đăng ký thành công!</h3>
                <p><strong>Mã NV:</strong> ${result.employee_code}</p>
                <p><strong>Số ảnh xử lý:</strong> ${result.images_processed}/${capturedPhotos.length}</p>
                <p>${result.message}</p>
            `;

            // Reset form
            setTimeout(() => {
                document.getElementById('register-form').reset();
                capturedPhotos = [];
                updatePhotosPreview();
                photoCountSpan.textContent = '0';
                registerResult.style.display = 'none';
            }, 5000);
        } else {
            registerResult.className = 'result-box error';
            registerInfo.innerHTML = `
                <h3>❌ Đăng ký thất bại</h3>
                <p>${result.detail || result.message}</p>
            `;
        }

    } catch (error) {
        registerResult.style.display = 'block';
        registerResult.className = 'result-box error';
        registerInfo.innerHTML = `<h3>❌ Lỗi</h3><p>${error.message}</p>`;
    } finally {
        submitRegisterBtn.disabled = false;
        submitRegisterBtn.textContent = '✅ Đăng ký & Train Model';
    }
});
