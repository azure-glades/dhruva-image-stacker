import os
import numpy as np
from astropy.io import fits

from scipy.ndimage import gaussian_filter
import cv2 as cv
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'
ALLOWED_EXTENSIONS = {'fits'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)


# FUNCTIONS
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_fits(image_list):
    images = [fits.getdata(image) for image in image_list]
    for i, img in enumerate(images):
        print(f"Image {i} shape: {img.shape}")
    norm_images = [img for img in images]
    num = len(norm_images)
    R = sum(norm_images[i] * (0.7 if i % num == 0 else 0.3/(num-1)) for i in range(num)) / num
    G = sum(norm_images[i] * (0.7 if i % num == int(num/2) else 0.3/(num-1)) for i in range(num)) / num
    B = sum(norm_images[i] * (0.7 if i % num == (num-1) else 0.3/(num-1)) for i in range(num)) / num
    rgb_image = np.stack([B, G, R], axis=-1)
    rgb_image = gaussian_filter(rgb_image, sigma=1)
    rgb_image = np.clip(rgb_image, 0, 1)
    rgb_image_8bit = (rgb_image * 255).astype(np.uint8)

    output_image_path = os.path.join(app.config['PROCESSED_FOLDER'], 'stacked_image.png')
    cv.imwrite(output_image_path, rgb_image_8bit)
    print(f"Processed image saved at {output_image_path}")
    
    return output_image_path

# THE WEBPAGES
@app.route('/')
def index():
    print("Rendering index.html from templates")
    return render_template('index.html')

@app.route('/test')
def test():
    print("Test route")
    return

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('files[]')
    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(f"File saved at {file_path}")
            filenames.append(file_path)

    if len(filenames) < 3:
        return 'Not enough data, please upload atleast 3.'
    processed_image_path = process_fits(filenames)

    for file_path in filenames:
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
    
    return render_template('result.html', processed_image_path=f'/{processed_image_path}')
