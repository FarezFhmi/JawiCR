from flask import Blueprint, render_template, request, redirect, url_for, session, g, send_file, current_app, flash
from functools import wraps
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import pytesseract
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from datetime import datetime
from io import BytesIO
import base64
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)

views = Blueprint('views', __name__)

# Load the model
model = tf.keras.models.load_model('website/static/model/JawiCRs.keras')
class_names = ['ain', 'alif', 'ba', 'ca', 'dal', 'dhad', 'dzal', 'fa', 'ga', 'ghain', 'ha', 'ha bulat', 'hamzah',
               'jim', 'kaf', 'kha', 'lam', 'lam_alif', 'mim', 'nga', 'nun', 'nya', 'pa', 'qaf', 'ro', 'shad',
                 'sin', 'syin', 'ta', 'tha', 'tho', 'va', 'wau', 'ya', 'zal', 'zho']

# Define login_required decorator
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if 'loggedin' in session:
            return route_function(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))  # Redirect to login page if not logged in
    return wrapper

def get_user_role():
    role_id = session.get('rolesID')
    if role_id:
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()
        cursor.execute('SELECT rolesName FROM user_roles WHERE rolesID = %s', (role_id,))
        role = cursor.fetchone()
        return role[0] if role else None
    return None

@views.route('/', methods=['GET', 'POST'])
@login_required
def homeUser():
    user_role = get_user_role()
    source = request.args.get('source', '')

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))

    if source == 'ocr':
        return redirect(url_for('views.ocr_section'))
    elif source == 'cnn':
        return redirect(url_for('views.cnn_section'))
    
    mesage = session.pop('message', None)  # Retrieve and remove the message from the session
    
    return render_template('home.html', mesage=mesage)

@views.route('/homeAdmin', methods=['GET', 'POST'])
@login_required
def homeAdmin():
    user_role = get_user_role()

    if user_role != 'admin':
        return redirect(url_for('views.homeUser'))
    else:
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        # Count users
        cursor.execute('SELECT COUNT(*) FROM users')
        count_user = cursor.fetchone()[0]

        # Count result recognitions
        cursor.execute('SELECT COUNT(*) FROM character_result')
        count_result = cursor.fetchone()[0]

        # Fetch recent user data
        cursor.execute('SELECT userName, userEmail, userDateRegister, userStatus FROM users ORDER BY userDateRegister DESC LIMIT 5')
        user_data = cursor.fetchall()

        # Fetch prediction accuracy
        cursor.execute('SELECT resultProbability FROM character_result')
        result_probabilities = [row[0] for row in cursor.fetchall()]

        return render_template(
            "homeAdmin.html",
            count_user=count_user,
            count_result=count_result,
            user_data=user_data,
            result_probabilities=result_probabilities
        )


@views.route('/ocr_section', methods=['GET','POST'])
@login_required
def ocr_section():
    user_role = get_user_role()
    
    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))
    return render_template('ocr_section.html')

@views.route('/ocr_process', methods=['GET', 'POST'])
@login_required
def ocr_process():
    message = ''
    user_role = get_user_role()
    userId = session.get('userID')

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))

    if request.method == 'POST':
        files = request.files.getlist('imagefile')
        if not files or all(file.filename == '' for file in files):
            message = "No files selected"
            return render_template("home.html", message=message)

        ocr_results = []
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        for imagefile in files:
            if imagefile.filename == '':
                continue

            filename = secure_filename(imagefile.filename)
            img_data = imagefile.read()

            if len(img_data) > current_app.config['MAX_CONTENT_LENGTH']:
                message = "File is too large"
                return render_template("home.html", message=message)

            cursor.execute('INSERT INTO image_user (imgName, imgDate, imgUser, userID) VALUES (%s, %s, %s, %s)',
                           (filename, datetime.now(), img_data, userId))
            mydb.commit()

            # Perform OCR
            np_img = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            boxes = pytesseract.image_to_boxes(image, config="--psm 10 --oem 3")
            char_images = save_characters(image, boxes)

            ocr_results.append({
                'image_id': cursor.lastrowid,
                'char_images': char_images
            })

        if not ocr_results:
            message = "No characters recognized"
            return render_template("ocr_section.html", message=message)

        return render_template('ocr_result.html', ocr_results=ocr_results, enumerate=enumerate)

    return render_template("ocr_section.html", message=message)

def save_characters(image, boxes):
    height, width, _ = image.shape
    char_images = []
    box_counter = 1

    for box in boxes.splitlines():
        box = box.split(" ")
        x1, y1, x2, y2 = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        
        # Crop the character from the original image
        cropped_img = image[height - y2:height - y1, x1:x2]
        
        # Encode the cropped image as binary data
        _, buffer = cv2.imencode('.png', cropped_img)
        char_images.append(buffer.tobytes())
        box_counter += 1

    return char_images

@views.route('/cnn_process', methods=['POST'])
@login_required
def cnn_process():
    user_role = get_user_role()
    userId = session.get('userID')
    source = request.form.get('source', 'ocr')

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))

    selected_images = request.form.getlist('selected_images')
    predictions = []
    mydb = getattr(g, 'mydb', None)
    cursor = mydb.cursor()

    for selected_image in selected_images:
        image_id, idx = selected_image.split('_')
        cursor.execute('SELECT imgUser FROM image_user WHERE image_id = %s', (image_id,))
        result = cursor.fetchone()
        if result is None:
            continue

        img_data = result[0]
        img_array = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Retrieve the specific character image from the array
        char_image = get_character_image(image, int(idx))

        prediction, probability = predict_character(char_image)
        
        # Convert numpy.float32 to float
        probability = float(probability)

        # Encode image data to Base64
        char_image_base64 = base64.b64encode(cv2.imencode('.png', char_image)[1]).decode('utf-8')
        
        # Save prediction details in database
        cursor.execute('INSERT INTO character_result (resultName, resultDate, resultImage, resultProbability, userID) VALUES (%s, %s, %s, %s, %s)',
                       (prediction, datetime.now(), img_data, probability, userId))
        mydb.commit()
        
        predictions.append({
            'image_id': cursor.lastrowid,
            'prediction': prediction,
            'probability': probability,
            'image_base64': char_image_base64
        })

    return render_template('cnn_result.html', predictions=predictions, source=source)

def get_character_image(image, idx):
    # Add logic to extract the specific character image from the image based on idx
    # This should match the cropping logic used in save_characters function
    height, width, _ = image.shape
    boxes = pytesseract.image_to_boxes(image, config="--psm 10 --oem 3").splitlines()
    if idx < len(boxes):
        box = boxes[idx].split(" ")
        x1, y1, x2, y2 = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        char_image = image[height - y2:height - y1, x1:x2]
        return char_image
    return None

def predict_character(image):
    img = cv2.resize(image, (256, 256))
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)

    # Add debug prints for prediction
    print(f"Image shape: {img.shape}")
    print(f"Image data: {img}")

    yhat = model.predict(img)
    print(f"Model output: {yhat}")
    predicted_class_index = np.argmax(yhat)
    predicted_class_probability = yhat[0, predicted_class_index]
    predicted_class_name = class_names[predicted_class_index]

    return predicted_class_name, predicted_class_probability

@views.route('/cnn_section', methods=['GET','POST'])
@login_required
def cnn_section():
    user_role = get_user_role()
    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))
    return render_template('cnn_section.html')

@views.route('/cnn_prediction', methods=['GET', 'POST'])
@login_required
def cnn_prediction():
    message = ''
    user_role = get_user_role()
    userId = session.get('userID')
    source = request.form.get('source', 'cnn')

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))

    if request.method == 'POST':
        files = request.files.getlist('imagefile')
        if not files or all(file.filename == '' for file in files):
            message = "No files selected"
            return render_template("cnn_section.html", message=message)

        predictions = []
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        for imagefile in files:
            if imagefile.filename == '':
                continue

            filename = secure_filename(imagefile.filename)
            img_data = imagefile.read()

            if len(img_data) > current_app.config['MAX_CONTENT_LENGTH']:
                message = "File is too large"
                return render_template("cnn_section.html", message=message)

            cursor.execute('INSERT INTO image_user (imgName, imgDate, imgUser, userID) VALUES (%s, %s, %s, %s)',
                           (filename, datetime.now(), img_data, userId))
            mydb.commit()

            img_array = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            prediction, probability = predict_character(image)

            probability = float(probability)

            img_base64 = base64.b64encode(img_data).decode('utf-8')

            cursor.execute('INSERT INTO character_result (resultName, resultDate, resultImage, resultProbability, userID) VALUES (%s, %s, %s, %s, %s)',
                           (prediction, datetime.now(), img_data, probability, userId))
            mydb.commit()

            predictions.append({
                'image_id': cursor.lastrowid,
                'prediction': prediction,
                'probability': probability,
                'image_base64': img_base64
            })

        return render_template('cnn_result.html', predictions=predictions, source=source)

    return render_template("cnn_section.html", message=message)

@views.route('/image/<int:img_id>')
def image(img_id):
    mydb = getattr(g, 'mydb', None)
    cursor = mydb.cursor()
    cursor.execute('SELECT imgUser FROM image_user WHERE image_id = %s', (img_id,))
    result = cursor.fetchone()
    if result is None:
        return "Image not found", 404
    img_data = result[0]
    return send_file(BytesIO(img_data), mimetype='image/png')

@views.route('/download_history', methods=['GET'])
@login_required
def download_history():
    user_role = get_user_role()
    user_id = session.get('userID')
    username = session.get('userName')  # Assuming you store the username in session

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))

    logging.debug(f"Processing download for user {user_id}")

    mydb = getattr(g, 'mydb', None)
    cursor = mydb.cursor()

    cursor.execute('SELECT * FROM character_result WHERE userID = %s ', (user_id,))
    listdata = cursor.fetchall()

    # Generate the filename for the PDF using the username
    report_name = f"user_report_{username}.pdf"
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []

    data = [['No', 'Image Name', 'Upload Date', 'Image']]
    for idx, row in enumerate(listdata, start=1):
        img_data = row[3]

        try:
            # Verify the image data with PIL
            pil_image = PILImage.open(BytesIO(img_data))
            pil_image.verify()  # Verify that it is an image
            pil_image = PILImage.open(BytesIO(img_data))  # Reopen the image to load it
            img_bytes_io = BytesIO()
            pil_image.save(img_bytes_io, format='PNG')
            img_bytes_io.seek(0)

            # Create ReportLab Image
            img = Image(img_bytes_io, width=50, height=50)

            data.append([str(idx), row[1], row[2].strftime("%Y-%m-%d %H:%M:%S"), img])
        except Exception as e:
            logging.error(f"Error processing image {row[1]}: {e}")
            data.append([str(idx), row[1], row[2].strftime("%Y-%m-%d %H:%M:%S"), 'Invalid image'])

    table = Table(data, colWidths=[30, 200, 150, 60], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    doc.build(elements)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=report_name, mimetype='application/pdf')

@views.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user_role = get_user_role()

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))
    
    return render_template('profilePage.html')

@views.route('/pass', methods=['GET','POST'])
@login_required
def passw():
    user_role = get_user_role()

    if user_role != 'user':
        return redirect(url_for('views.homeAdmin'))
    
    return render_template('changePass.html')

@views.route('/manageuser', methods=['GET','POST'])
@login_required
def manageUser():
    user_role = get_user_role()
    if user_role != 'admin':
        return redirect(url_for('views.homeUser'))
    else:
        mesage=''
        userType = 2
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        cursor.execute('SELECT * FROM users WHERE rolesID = %s ', (userType,))
        listdata = cursor.fetchall()

        user_data = []
        for row in listdata:
            user_data.append({
            "userID": row[0], 
            "userName": row[1],  
            "userEmail": row[2],
            "userDate": row[4],
            "userStatus": row[5]
        })
            
    mesage = session.pop('message', None) 

    return render_template('manageUser.html',user_data=user_data,mesage=mesage)

# Helper function to get the database cursor
def get_db_cursor():
    mydb = getattr(g, 'mydb', None)
    if mydb is None:
        raise Exception("Database connection is not available")
    return mydb.cursor()

@views.route('/manage/<int:user_id>', methods=['GET', 'POST'])
def manage(user_id):
    user_role = get_user_role()
    if user_role != 'admin':
        return redirect(url_for('views.homeUser'))
    else:
        mesage = ''
        try:
            cursor = get_db_cursor()
            cursor.execute('SELECT * FROM users WHERE userID = %s', (user_id,))
            user = cursor.fetchone()

            if request.method == 'POST':
                user_status = request.form.get('userStatus')

                if not user_status:
                    mesage = 'Please select a user status!'
                else:
                    cursor.execute('UPDATE users SET userStatus = %s WHERE userID = %s', (user_status, user_id))
                    g.mydb.commit()

                    mesage = "User status updated successfully!"

                    session['message'] = mesage

                    return redirect(url_for('views.manageUser'))
        except Exception as e:
            logging.error(f"manage user error: {e}")
            mesage = "An error occurred during manage user."

        return render_template('manage.html', mesage=mesage, user=user)
    
@views.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    user_role = get_user_role()
    if user_role != 'admin':
        return redirect(url_for('views.homeUser'))
    else:
        try:
            cursor = get_db_cursor()
            cursor.execute('DELETE FROM users WHERE userID = %s', (user_id,))
            g.mydb.commit()
            mesage = "User deleted successfully!"
            session['message'] = mesage
        except Exception as e:
            logging.error(f"delete user error: {e}")
            flash('An error occurred during user deletion.')

        return redirect(url_for('views.manageUser'))

@views.route('/history', methods=['GET','POST'])
@login_required
def history():
    user_role = get_user_role()
    if user_role != 'admin':
        return redirect(url_for('views.homeUser'))
    else:
        mydb = getattr(g, 'mydb', None)
        cursor = mydb.cursor()

        cursor.execute('SELECT * FROM character_result')
        listdata = cursor.fetchall()

        list_report = []
        for row in listdata:
            list_report.append({
            "resultID": row[0], 
            "resultName": row[1],  
            "resultDate": row[2],
            "resultImage": row[3], 
            "resultProbability": row[4]
        })
    return render_template('report.html',list_report=list_report)