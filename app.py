from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import cv2
import numpy as np
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    return redirect(url_for('resize_image', filename=file.filename))


@app.route('/resize/<filename>', methods=['GET', 'POST'])
def resize_image(filename):
    if request.method == 'POST':
        operation = request.form.get('operation')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image = cv2.imread(filepath)

        if operation == 'resize':
            width = int(request.form.get('width'))
            height = int(request.form.get('height'))
            resized_image = cv2.resize(image, (width, height))
            output_filename = 'resized_' + filename
            output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
            cv2.imwrite(output_filepath, resized_image)
            result_width, result_height = width, height

        elif operation == 'rotate':
            angle = int(request.form.get('angle', 0))
            keep_original_size = request.form.get('keep_original_size') == 'on'

            original_height, original_width = image.shape[:2]
            center = (original_width // 2, original_height // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

            abs_cos = abs(matrix[0, 0])
            abs_sin = abs(matrix[0, 1])
            new_width = int(original_height * abs_sin + original_width * abs_cos)
            new_height = int(original_height * abs_cos + original_width * abs_sin)

            matrix[0, 2] += (new_width // 2) - center[0]
            matrix[1, 2] += (new_height // 2) - center[1]

            rotated_image = cv2.warpAffine(image, matrix, (new_width, new_height))

            if not keep_original_size:
                width = int(request.form.get('width', new_width))
                height = int(request.form.get('height', new_height))
                rotated_image = cv2.resize(rotated_image, (width, height))
            else:
                width, height = new_width, new_height

            output_filename = 'rotated_' + filename
            output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
            cv2.imwrite(output_filepath, rotated_image)
            result_width, result_height = width, height

        elif operation == 'color_scale':
            color_scale = request.form.get('color_scale')
            keep_original_size = request.form.get('keep_original_size') == 'on'

            if color_scale == 'gray':
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                if not keep_original_size:
                    width = int(request.form.get('width', image.shape[1]))
                    height = int(request.form.get('height', image.shape[0]))
                    gray_image = cv2.resize(gray_image, (width, height))
                else:
                    width, height = image.shape[1], image.shape[0]

                output_filename = 'gray_' + filename
                output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
                cv2.imwrite(output_filepath, gray_image)
                result_width, result_height = width, height

            # Handle color channel extraction (Red, Green, Blue)
            elif color_scale == 'red':
                # Extract Red channel
                red_image = image.copy()
                red_image[:, :, 1] = 0  # Set Green channel to 0
                red_image[:, :, 0] = 0  # Set Blue channel to 0

                if not keep_original_size:
                    width = int(request.form.get('width', image.shape[1]))
                    height = int(request.form.get('height', image.shape[0]))
                    red_image = cv2.resize(red_image, (width, height))
                else:
                    width, height = image.shape[1], image.shape[0]

                output_filename = 'red_' + filename
                output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
                cv2.imwrite(output_filepath, red_image)
                result_width, result_height = width, height

            elif color_scale == 'green':
                # Extract Green channel
                green_image = image.copy()
                green_image[:, :, 0] = 0  # Set Blue channel to 0
                green_image[:, :, 2] = 0  # Set Red channel to 0

                if not keep_original_size:
                    width = int(request.form.get('width', image.shape[1]))
                    height = int(request.form.get('height', image.shape[0]))
                    green_image = cv2.resize(green_image, (width, height))
                else:
                    width, height = image.shape[1], image.shape[0]

                output_filename = 'green_' + filename
                output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
                cv2.imwrite(output_filepath, green_image)
                result_width, result_height = width, height

            elif color_scale == 'blue':
                # Extract Blue channel
                blue_image = image.copy()
                blue_image[:, :, 1] = 0  # Set Green channel to 0
                blue_image[:, :, 2] = 0  # Set Red channel to 0

                if not keep_original_size:
                    width = int(request.form.get('width', image.shape[1]))
                    height = int(request.form.get('height', image.shape[0]))
                    blue_image = cv2.resize(blue_image, (width, height))
                else:
                    width, height = image.shape[1], image.shape[0]

                output_filename = 'blue_' + filename
                output_filepath = os.path.join(UPLOAD_FOLDER, output_filename)
                cv2.imwrite(output_filepath, blue_image)
                result_width, result_height = width, height

        return render_template('result.html', filename=output_filename, width=result_width, height=result_height)

    return render_template('resize.html', filename=filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)



