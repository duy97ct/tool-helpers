// JavaScript để xem trước ảnh và cập nhật ngưỡng
function previewFile() {
    const file = document.querySelector('input[type=file]').files[0];
    const preview = document.getElementById('preview-image');
    const reader = new FileReader();

    reader.addEventListener("load", function () {
        preview.src = reader.result;
        preview.style.display = 'block';
    }, false);

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
    }
}

// Định dạng giá trị để thêm số 0 vào đầu nếu giá trị có một chữ số
function formatValue(value) {
    return value.toString().padStart(2, '0');
}

// Cập nhật giá trị ngưỡng và hiển thị lên giao diện
function updateThresholdValue(value) {
    document.getElementById('thresholdValue').textContent = value;
    updateAndPreview(); // Gọi hàm updateAndPreview khi thay đổi giá trị ngưỡng
}

// Cập nhật giá trị vị trí và hiển thị lên giao diện
function updatePosition(position, value) {
    const formattedValue = formatValue(value);
    document.getElementById(position + 'Value').textContent = formattedValue;
    updateAndPreview(); // Gọi hàm updateAndPreview khi thay đổi giá trị thanh trượt
}

// Hàm để cập nhật và xem trước ảnh khi kéo thanh trượt
function updateAndPreview() {
    const file = document.querySelector('input[type=file]').files[0];
    const formData = new FormData();
    formData.append('image', file);
    formData.append('threshold', document.getElementById('thresholdRange').value);
    formData.append('left', document.getElementById('leftRange').value);
    formData.append('right', document.getElementById('rightRange').value);
    formData.append('top', document.getElementById('topRange').value);
    formData.append('bottom', document.getElementById('bottomRange').value);

    fetch('/crop_preview', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const processedPreview = document.getElementById('processed-preview');
        processedPreview.src = URL.createObjectURL(blob);
        processedPreview.style.display = 'block';
        document.getElementById('downloadButton').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to preview and process the image.');
    });
}

// Hàm tăng giá trị của thanh trượt
function incrementSlider(sliderId) {
    let slider = document.getElementById(sliderId);
    let currentValue = parseInt(slider.value);
    slider.value = currentValue + 1;
    updatePosition(sliderId.replace('Range', ''), slider.value); // Gọi hàm updatePosition để cập nhật giá trị
}

// Hàm giảm giá trị của thanh trượt
function decrementSlider(sliderId) {
    let slider = document.getElementById(sliderId);
    let currentValue = parseInt(slider.value);
    slider.value = currentValue - 1;
    updatePosition(sliderId.replace('Range', ''), slider.value); // Gọi hàm updatePosition để cập nhật giá trị
}


// Xem trước ảnh và hiển thị phần xử lý
function previewAndSubmit() {
    const file = document.querySelector('input[type=file]').files[0];
    const formData = new FormData();
    formData.append('image', file);
    formData.append('threshold', document.getElementById('thresholdRange').value);
    formData.append('left', document.getElementById('leftRange').value);
    formData.append('right', document.getElementById('rightRange').value);
    formData.append('top', document.getElementById('topRange').value);
    formData.append('bottom', document.getElementById('bottomRange').value);

    fetch('/tachnen', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const processedPreview = document.getElementById('processed-preview');
        processedPreview.src = URL.createObjectURL(blob);
        processedPreview.style.display = 'block';
        document.getElementById('downloadButton').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to preview and process the image.');
    });
}

// Sự kiện khi nhấn nút Tải ảnh đã xử lý
document.getElementById('downloadButton').addEventListener('click', function() {
    const processedPreview = document.getElementById('processed-preview');
    const url = processedPreview.src;
    const originalFilename = document.querySelector('input[type=file]').files[0].name;
    const filename = `${originalFilename.split('.')[0]}_tach_nen.png`;
    
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to download the processed image.');
        });
});