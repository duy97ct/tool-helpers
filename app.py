import os
import requests
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import io
import convertapi
import cv2
import numpy as np
import random
import string

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static' 
app.secret_key = 'supersecretkey'
# Cấu hình thư mục upload
app.config['UPLOAD_FOLDER'] = 'static/uploads'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# API Key của ConvertAPI
CONVERTAPI_SECRET = 'RUMrVe9vYn2ZUICI'

convertapi.api_secret = CONVERTAPI_SECRET

# Hàm loại bỏ nền của ảnh sử dụng OpenCV
def remove_background(image_bytes, threshold=200, left=0, right=100, top=0, bottom=100):
    try:
        # Đọc ảnh từ byte
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Cắt ảnh theo vị trí đã chọn
        height, width = image.shape[:2]
        left_px = int(width * (left / 100))
        right_px = int(width * (right / 100))
        top_px = int(height * (top / 100))
        bottom_px = int(height * (bottom / 100))
        cropped_image = image[top_px:bottom_px, left_px:right_px]

        # Chuyển đổi sang ảnh xám
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

        # Áp dụng ngưỡng để tạo mặt nạ
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

        # Tạo ảnh alpha để giữ lại nền trong suốt
        b, g, r = cv2.split(cropped_image)
        alpha = cv2.bitwise_not(mask)
        result = cv2.merge([b, g, r, alpha])

        # Chuyển đổi ảnh thành mảng byte để gửi về client
        _, img_encoded = cv2.imencode('.png', result)
        return img_encoded.tobytes()
    
    except Exception as e:
        print(f"Exception: {e}")
        return None




# Hàm chuyển đổi PDF sang PNG sử dụng ConvertAPI
def convert_pdf_to_images(pdf_bytes, filename):
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(temp_pdf_path, 'wb') as f:
        f.write(pdf_bytes)

    result = convertapi.convert('png', {
        'File': temp_pdf_path
    }, from_format='pdf')

    if result:
        first_image_url = result.files[0].url
        return first_image_url
    return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tachnen', methods=['GET', 'POST'])
def tachnen():
    image_file = request.args.get('image_file')  # Lấy tên file từ query string
    image_url = url_for('static', filename=f'uploads/{image_file}') if image_file else None
    
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            image_bytes = file.read()
            threshold = int(request.form.get('threshold', 200))
            left = int(request.form.get('left', 0))
            right = int(request.form.get('right', 100))
            top = int(request.form.get('top', 0))
            bottom = int(request.form.get('bottom', 100))
            processed_file = remove_background(image_bytes, threshold=threshold, left=left, right=right, top=top, bottom=bottom)
            if processed_file:
                original_filename = file.filename.rsplit('.', 1)[0]
                download_name = f'{original_filename}_tach_nen.png'
                return send_file(io.BytesIO(processed_file), mimetype='image/png', as_attachment=True, download_name=download_name)
            else:
                flash("Failed to process image. Please try again.")
                return redirect(url_for('tachnen'))
        else:
            flash("No file uploaded. Please upload an image.")
            return redirect(url_for('tachnen'))
    
    return render_template('tachnen.html', image_url=image_url)

@app.route('/crop_preview', methods=['POST'])
def crop_preview():
    image = request.files['image']
    threshold = int(request.form['threshold'])
    left = int(request.form['left'])
    right = int(request.form['right'])
    top = int(request.form['top'])
    bottom = int(request.form['bottom'])
    
    # Sử dụng hàm remove_background để xử lý ảnh
    image_bytes = image.read()
    processed_file = remove_background(image_bytes, threshold, left, right, top, bottom)
    
    if processed_file:
        return send_file(io.BytesIO(processed_file), mimetype='image/png')
    else:
        flash("Failed to process image preview. Please try again.")
        return redirect(url_for('tachnen'))

@app.route('/pdf2image', methods=['GET', 'POST'])
def pdf2image():
    if request.method == 'POST':
        file = request.files.get('pdf')
        if file:
            pdf_bytes = file.read()
            original_filename = secure_filename(file.filename)
            image_url = convert_pdf_to_images(pdf_bytes, original_filename)
            if image_url:
                return render_template('pdf2image.html', image_url=image_url)
            else:
                flash('Failed to convert PDF to image. Please try again.')
                return redirect(url_for('pdf2image'))
        else:
            flash('No file uploaded. Please upload a PDF file.')
            return redirect(url_for('pdf2image'))
    
    return render_template('pdf2image.html')


@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png', as_attachment=True, download_name=filename)
    else:
        flash('File not found.')
        return redirect(url_for('index'))

@app.route('/save_to_uploads', methods=['POST'])
def save_to_uploads():
    if 'image_url' not in request.form:
        return jsonify({'error': 'No image URL provided'}), 400

    image_url = request.form['image_url']

    # Giả định bạn có cách để lấy hình ảnh từ URL và lưu vào thư mục uploads
    # Ví dụ, bạn có thể sử dụng requests để tải hình ảnh từ URL
    import requests
    from werkzeug.utils import secure_filename
    import os

    # Tải ảnh từ URL và lưu vào thư mục uploads
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = secure_filename('image.png')  # Hoặc tạo tên file phù hợp
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return jsonify({'message': 'Image has been saved successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'Failed to download image'}), 500

def generate_random_string(length=6):
    """Tạo chuỗi ngẫu nhiên dài `length` ký tự."""
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # app.run()