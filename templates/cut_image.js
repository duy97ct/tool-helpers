// Cập nhật vị trí cắt và hiển thị lên giao diện
function updatePosition(direction, value) {
    document.getElementById(direction + 'Value').textContent = value;
}

// Sự kiện khi thay đổi giá trị trên thanh trượt
document.getElementById('leftRange').addEventListener('input', function() {
    updatePosition('left', this.value);
});

document.getElementById('rightRange').addEventListener('input', function() {
    updatePosition('right', this.value);
});

document.getElementById('topRange').addEventListener('input', function() {
    updatePosition('top', this.value);
});

document.getElementById('bottomRange').addEventListener('input', function() {
    updatePosition('bottom', this.value);
});
