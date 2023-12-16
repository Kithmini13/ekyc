import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from getFaceEncodings import RecognizeFace
from face_recog_class import isFace
from io import BytesIO
from PIL import Image
import base64
import logging
import datetime
import json
import sys

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = 'temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return "Welcome to the Face Recognition! To upload the images go to http://127.0.0.1:5002/recognize"

@app.route('/recognize', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'doc_image' not in request.files or 'selfie_image' not in request.files:
            logger.error("Both doc_image and selfie_image files has not been passed to the API")
            logger.error('Timestamp: %s', datetime.datetime.now())
            return 'Both doc_image and selfie_image must be selected', 400
        
        # def image_to_base64(image_path):
        #     with open(image_path, "rb") as image_file:
        #         image_data = image_file.read()
        #     encoded_string = base64.b64encode(image_data).decode("utf-8")
        #     return encoded_string

        def base64_to_image(encoded_string):
            image_data = base64.b64decode(encoded_string)
            image = Image.open(BytesIO(image_data))
            return image
    
        doc_image_file = request.files['doc_image']
        selfie_image_file = request.files['selfie_image']

        # Save the images to the uploads folder
        if 'doc_image' in request.files:
            try:
                doc_image_file_name = secure_filename(doc_image_file.filename)
                doc_image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))
                logger.info('Response: %s', f"doc_image Received to the API: Filename: {doc_image_file_name}")
                logger.info('Timestamp: %s', datetime.datetime.now())
                # str1 = image_to_base64(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))
            except Exception as e:
                logger.error('Error while receiving doc_image: %s')
                sys.exit(1)
            


        if 'selfie_image' in request.files:
            try:    
                selfie_image_file_name = secure_filename(selfie_image_file.filename)
                selfie_image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], selfie_image_file_name))
                logger.info('Response: %s', f"selfie_image Received to the API:  Filename: {selfie_image_file_name}")
                logger.info('Timestamp: %s', datetime.datetime.now())
                # str2 = image_to_base64(os.path.join(app.config['UPLOAD_FOLDER'], selfie_image_file_name))
            except Exception as e:
                logger.error('Error while receiving selfie_image: %s')
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))
                sys.exit(1)


        if 'doc_image' not in request.files and 'selfie_image' not in request.files:
            return 'No file selected', 400

        elif 'doc_image' in request.files and 'selfie_image' in request.files:
            classifier = RecognizeFace(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name),os.path.join(app.config['UPLOAD_FOLDER'], selfie_image_file_name))
            result = classifier.process_file()
            logger.info('API PROCESSES COMPLETED: output: %s', json.dumps({'Result': result['Result'], 'Probability': result['Probability']}))
            logger.info('Timestamp: %s', datetime.datetime.now())
            # img_roi = base64_to_image(result['roi'])
            # print(img_roi)
            response = {
                'Result': result['Result'],
                'Probability': result['Probability'],
                'Z_Base64_ROI_docImg': result['roi'],
                'Z_Base64_ROI_selfieImg': result['roi2'],
                # 'Z_Base64_doc_image': str1,
                # 'Z_Base64_selfie_image': str2,
            }
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], selfie_image_file_name))
            return jsonify(response)

        else:
            logger.error("Both doc_image and selfie_image files has not been passed to the API")
            logger.error('Timestamp: %s', datetime.datetime.now())
            

    # If it's a GET request, return the upload form
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="doc_image">
        <input type="file" name="selfie_image">
        <input type="submit" value="Upload">
    </form>
    '''

@app.route('/isFace', methods=['POST'])
def upload_file2():
    if request.method == 'POST':
        if 'image' not in request.files:
                return 'image file must be selected', 400

        input = request.files['image']        

        if 'image' in request.files:
                doc_image_file_name = secure_filename(input.filename)
                input.save(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))

        if 'image' not in request.files:
                return 'No file selected', 400   

        elif 'image' in request.files:                
            classifier = isFace(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))   
            result = classifier.process()   
            if result == "Face_Detected!":
                  resultStatus = "00"
                  description = "Face Detected Successfully"  
            else:
                  resultStatus = "01"
                  description = "Face Detection Failed"
                  
            response = {
                    'resultStatus': resultStatus,
                    'description': description
                    }

            print("Output Result: ", description)  
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], doc_image_file_name))
            return jsonify(response)   
         

        else:
                return f"request.content_length: {request.content_length}"

    # If it's a GET request, return the upload form
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" multiple>
        <input type="submit" value="Upload">
    </form>
    '''    

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5002)






    
    

