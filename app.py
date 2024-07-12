import os
import requests
from flask import Flask, request, render_template, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image
import io
import convertapi
import cv2
import numpy as np


app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# API Key của Remove.bg và ConvertAPI
# API_KEY_REMOVE_BG = '9xgSWw4YiSvStys1iEFrrM7g' # API miễn phí nên mỗi tháng chỉ có 50 lượt dùng chùa
CONVERTAPI_SECRET = 'RUMrVe9vYn2ZUICI'

convertapi.api_secret = CONVERTAPI_SECRET

# Hàm loại bỏ nền của ảnh sử dụng OpenCV
# Hàm loại bỏ nền của ảnh sử dụng OpenCV và ngưỡng từ request
def remove_background(image_bytes, threshold=200):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        _, mask = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY_INV)
        result = cv2.bitwise_and(image, image, mask=mask)

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
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            try:
                image_bytes = file.read()
                threshold = int(request.form.get('threshold', 200))
                original_filename = secure_filename(file.filename)
                processed_file = remove_background(image_bytes, threshold=threshold)
                if processed_file:
                    processed_filename = f"{os.path.splitext(original_filename)[0]}_tach_nen.png"
                    return send_file(io.BytesIO(processed_file), mimetype='image/png', as_attachment=True, download_name=processed_filename)
                else:
                    flash("Failed to process image. Please try again.")
                    return redirect(url_for('tachnen'))
            except Exception as e:
                print(f"Error processing image: {e}")
                flash("Error processing image. Please try again.")
                return redirect(url_for('tachnen'))
        else:
            flash("No file uploaded. Please upload an image.")
            return redirect(url_for('tachnen'))
    return render_template('tachnen.html')

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
