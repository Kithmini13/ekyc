import os
import uuid
from flask import Flask, request, jsonify
import cv2
import json
import pytesseract
import logging
import datetime

from documentClassify import LegalDocClassify
from New_NIC_Classifier import NewNICClassify
from license_OCR import OCRDrivingLicensescan
from passport_OCR import OCRPassportscan
from old_NIC_OCR import OCROldNICScan
from new_NIC_OCR import OCRNewNICScan
from werkzeug.utils import secure_filename
import re
from billClassify import BillClassify
from OCR_dialogBILL import OCRdialog
from OCR_electricBILL import ElectricBillOCR
from OCR_mobitelBILL import OCRmobitel
from OCR_waterBILL import OCRwaterBill
from pdf2image import convert_from_bytes
from pdf2image import convert_from_path as cp
from filetype import filetype
from Classification_class import NICSideClassification


def rotations(img):
    results = pytesseract.image_to_osd(img)
    rotation_angle = int(results.split('\n')[1].split(' ')[-1])
    if rotation_angle > 100:
        rotated_image = cv2.rotate(img, cv2.ROTATE_180)
        return rotated_image
    else:
        rotated_image = img
        return rotated_image

app = Flask(__name__)

# logging.basicConfig(level=logging.INFO)  
# logger = logging.getLogger(__name__)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# console_handler = logging.StreamHandler()  
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER2 = 'Bills'
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2

UPLOAD_FOLDER3 = 'temp'
os.makedirs(UPLOAD_FOLDER3, exist_ok=True)
app.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3

poppler_path = r'C:\\Program Files (x86)\\poppler-23.07.0\\Library\\bin'
os.environ["PATH"] += os.pathsep + poppler_path

@app.route('/')
def index():
    return "Welcome to the Legal Documents Upload! \nTo upload go to http://127.0.0.1:5001/upload"

# @app.route('/upload')
# def user():
#     return "Enter the user ID To upload the documents http://127.0.0.1:5001/upload/UserID"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Extract the UserID from the form data
        userID = request.form.get('UserID')

        logger.info('Response: %s', f"User ID has been passed to the API successfully: UserID: {userID}")
        logger.info('Timestamp: %s', datetime.datetime.now())

        #Type should be DL, NIC or PP
        docType = request.form.get('Doc_Type')

        # Check if the post request has the file part
        if 'file' not in request.files or len(request.files.getlist('file')) == 0:
            return 'No file selected', 400

        files = request.files.getlist('file')  # Get a list of uploaded files

        if len(files) == 2:
            Unique_ID = str(uuid.uuid4())
            Unique_ID_2 = str(uuid.uuid4())
        else:
            Unique_ID = str(uuid.uuid4())

        # Create a folder specific to the user
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], Unique_ID)
        os.makedirs(user_folder, exist_ok=True)

        if len(files) == 1:
            # Generate unique filenames for the uploaded files
            filenames = [Unique_ID + '.jpg' for _ in range(len(files))]
            print("FILE NAMES: ", filenames)
        else:
            # Generate unique filenames for the uploaded files
            filenames = []
            filenames.append(Unique_ID + '.jpg')
            filenames.append(Unique_ID_2 + '.jpg')
            print("FILE NAMES: ", filenames)

        # Save the files to the user's folder
        for i, file in enumerate(files):
            print(f"Saving file {i}")
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_folder, filenames[i]))


        logger.info('Response: %s', f"Files has been saved to the File System successfully: Folder: {Unique_ID}")
        logger.info('Timestamp: %s', datetime.datetime.now())
        responses = []

        if len(files) == 0:
            return 'No file selected', 400

        elif len(files) == 1:
            for i, filename in enumerate(filenames):
                # try:
                # Process each uploaded file using the Classify class
                    classifier = LegalDocClassify(cv2.imread(os.path.join(user_folder, filename)))
                    result = classifier.process_file(os.path.join(user_folder, filename))
                    logger.info('Document Classification Successful: %s', f"Classification Result: {result['file_type']}")
                    logger.info('Timestamp: %s', datetime.datetime.now())
                    new_filename = f"{Unique_ID}_{result['file_type']}.jpg"
                    new_file_path = os.path.join(user_folder, new_filename)
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    os.rename(os.path.join(user_folder, filename), new_file_path)

                    if docType == "DRL":
                        docType = "Driving_License"
                    elif docType == "PP":
                        docType = "Passport"

                    if result['file_type'] == "Unknown_File":
                        error_code = "04"
                        message_code = "Unknown File"

                    if result['file_type'] == "Low_Quality":
                        error_code = "03"
                        message_code = "Low Quality Image"

                    if docType == result['file_type'] or docType in result['file_type']:
                        if result['file_type'] == "Driving_License":
                            DL_OCR = OCRDrivingLicensescan(cv2.imread(os.path.join(user_folder, new_filename)))
                            output1 = DL_OCR.process_file()
                            detail_dict = json.loads(output1['Details'])
                            if output1['Extraction'] == False and result['classification'] == False and (error_code != "03" or error_code != "04") :
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input." 

                            elif output1['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output1['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Dcument extraction failed"

                            elif output1['Extraction'] == True and result['classification'] == True:
                                error_code = "00"
                                message_code = "Success"

                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output1['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'Name': detail_dict.get('Name', None),
                            'familyName': detail_dict.get('familyName', None),
                            'firstName': detail_dict.get('firstName', None),
                            'middleName': detail_dict.get('middleName', None),
                            'lastName': detail_dict.get('lastName', None),
                            'nameInitials': detail_dict.get('nameInitials', None),
                            'Licence_no':detail_dict.get('License No', None),
                            'NIC':detail_dict.get('NIC', None),
                            'Address': detail_dict.get('Address', None),
                            'Issuedate': detail_dict.get('Issue Date', None),
                            'Expirydate': detail_dict.get('Expiry_Date', None),
                            'PassportNo': detail_dict.get('Passport No', None),
                            }
                        

                        elif result['file_type'] == "Passport":
                            Passport_OCR = OCRPassportscan(cv2.imread(os.path.join(user_folder, new_filename)))
                            output2 = Passport_OCR.process_file()
                            detail_dict = json.loads(output2['Details'])
                            if output2['Extraction'] == False and result['classification'] == False and (error_code != "03" or error_code != "04"):
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input." 

                            elif output2['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output2['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            elif output2['Extraction'] == True and result['classification'] == True:
                                error_code = "00"
                                message_code = "Success"
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output2['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'Name': detail_dict.get('Name', None),
                            'familyName': detail_dict.get('familyName', None),
                            'firstName': detail_dict.get('firstName', None),
                            'middleName': detail_dict.get('middleName', None),
                            'lastName': detail_dict.get('lastName', None),
                            'nameInitials': detail_dict.get('nameInitials', None),
                            'Licence_no':detail_dict.get('License No', None),
                            'NIC':detail_dict.get('NIC', None),
                            'Address': detail_dict.get('Address', None),
                            'Expirydate': detail_dict.get('ExpiryDate', None),
                            'Issuedate': detail_dict.get('IssueDate', None),
                            'PassportNo': detail_dict.get('PassportNo', None),
                            }
                        
                        
                        elif result['file_type'] == "Unknown_File":
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'status': "04",
                            'message': "Unknown File Type",
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        
                        elif result['file_type'] == "Low_Quality":
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'status': "03",
                            'message': "Low Quality",
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        
                        responses.append(response)

                    else:
                        response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'status': "10",
                            'message': "Your chosen proof of ID type from the dropdown menu appears to be incorrect.",
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        responses.append(response)

                    # except Exception as e:
                    # # Handle any other exceptions that may occur during processing
                    #     response = {
                    #         'error': f"Something went wrong when opening the file: {str(e)}"
                    #     }

            # Log the JSON response and timestamp
            for response in responses:
                logger.info('API PROCESSES COMPLETED: output: %s', json.dumps(response))
                logger.info('Timestamp: %s', datetime.datetime.now())

            return jsonify(response) 


        elif len(files) == 2:  
            images1 = cv2.imread(os.path.join(user_folder, filenames[0]))
            images2 = cv2.imread(os.path.join(user_folder, filenames[1]))

            if docType == "DRL":
                    docType = "Driving_License"
            elif docType == "PP":
                    docType = "Passport"

            classifier = LegalDocClassify(images1)
            result = classifier.process_file(os.path.join(user_folder, filenames[0]))
            logger.info('Document Classification Successful: %s', f"Classification Result: {result['file_type']}")
            logger.info('Timestamp: %s', datetime.datetime.now())

            if docType == result['file_type'] or docType in result['file_type']:
                custom_config = r'--oem 3 --psm 6 '
                text1 = pytesseract.image_to_string(images1, config = custom_config)  
                text2 = pytesseract.image_to_string(images2, config = custom_config) 
    
                text = text1 + text2  

                for i,file in enumerate(filenames):
                    new_filename1 = f"{Unique_ID}_NIC_{i}.jpg"
                    new_file_path1 = os.path.join(user_folder, new_filename1)
                    if os.path.exists(new_file_path1):
                            os.remove(new_file_path1)
                    os.rename(os.path.join(user_folder, file), new_file_path1) 
                    
                if "IDENTITY" in text or "CARD" in text or "NATIONAL" in text or "Address" in text or "Registration of Persons" in text:
                    if docType == 'NIC':
                        classifier = NewNICClassify(images1)
                        result = classifier.process_file()

                        if result['file_type'] == "New_NIC_Front":
                            NewNIC_OCR = OCRNewNICScan(images1,images2)
                            NIC_Sides_Jumbled = False
                        
                        elif result['file_type'] == "New_NIC_Back":
                            NewNIC_OCR = OCRNewNICScan(images2,images1)
                            NIC_Sides_Jumbled = True

                        print("NIC JuMBLED STATUS: ", NIC_Sides_Jumbled)
                        output4 = NewNIC_OCR.process_file()
                        detail_dict = output4['Details']

                        if output4['Extraction'] == True and result['classification'] == True and NIC_Sides_Jumbled == False:
                            error_code = "00"
                            message_code = "Success"

                        elif output4['Extraction'] == True and result['classification'] == True and NIC_Sides_Jumbled == True:
                            error_code = "69"
                            message_code = "NIC Sides are not uploaded Correctly"

                        elif output4['Extraction'] == True and result['classification'] == False:
                            error_code = "01"
                            message_code = "Document classification failed"

                        elif output4['Extraction'] == False and result['classification'] == True:
                            error_code = "02"
                            message_code = "Document extraction failed"

                        elif output4['Extraction'] == False and result['classification'] == False:
                            error_code = "10"
                            message_code = "Failed to process further due to inaccurate input."
                        

                        response = {
                            'userID': Unique_ID,
                            'status': error_code,
                            'message': message_code,
                            'Extraction': output4['Extraction'],
                            'Classification': result['classification'],
                            'Name': detail_dict.get('Full_name', None),
                            'familyName': detail_dict.get('familyName', None),
                            'firstName': detail_dict.get('firstName', None),
                            'middleName': detail_dict.get('middleName', None),
                            'lastName': detail_dict.get('lastName', None),
                            'nameInitials': detail_dict.get('nameInitials', None),
                            'Licence_no':detail_dict.get('License No', None),
                            'NIC':detail_dict.get('NIC', None),
                            'Address': detail_dict.get('Address', None),
                            'Issuedate': detail_dict.get('Issue Date', None),
                            'Expirydate': None,
                            'PassportNo': detail_dict.get('Passport No', None),
                        }
                        responses.append(response)

                    else:
                        response = {
                            'userID': Unique_ID,
                            'status': "10",
                            'message': "Your chosen proof of ID type from the dropdown menu appears to be incorrect.",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        responses.append(response)

                elif re.search(r'\d{9}\s*[vV]', text1) or re.search(r'\d{12}', text1) or (re.search(r'1968', text1) and re.search(r'32', text1)) or (re.search(r'1968', text1) and re.search(r'52', text1)):
                    if docType == 'NIC':
                        OldNIC_OCR = OCROldNICScan(images1)
                        hsv_image = cv2.cvtColor(images1, cv2.COLOR_BGR2HSV)
                        h, s, v = cv2.split(hsv_image)
                        average_brightness = cv2.mean(v)[0]
                        if average_brightness > 140:
                            output3 = OldNIC_OCR.process_file()
                            detail_dict = json.loads(output3['Details'])
                            if output3['Extraction'] == True:
                                error_code = "00"
                                message_code = "Success"
                            
                            if output3['Extraction'] == False:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            response = {
                                    'userID': Unique_ID,
                                    'status': error_code,
                                    'message': message_code,
                                    'Extraction': output3['Extraction'],
                                    'Classification': result['classification'],
                                    'Name': detail_dict.get('Name', None),
                                    'familyName': detail_dict.get('familyName', None),
                                    'firstName': detail_dict.get('firstName', None),
                                    'middleName': detail_dict.get('middleName', None),
                                    'lastName': detail_dict.get('lastName', None),
                                    'nameInitials': detail_dict.get('nameInitials', None),
                                    'Licence_no':detail_dict.get('License No', None),
                                    'NIC':detail_dict.get('NIC', None),
                                    'Address': detail_dict.get('Address', None),
                                    'Issuedate': detail_dict.get('Issued Date', None),
                                    'Expirydate': None,
                                    'PassportNo': detail_dict.get('Passport No', None),
                                    }
                            responses.append(response)

                        else:
                            response = {
                            'userID': Unique_ID,
                            'status': "03",
                            'message': "Low Quality",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                            'Issue': "Low_Brightness"
                        }
                            responses.append(response)


                    else:
                        response = {
                            'userID': Unique_ID,
                            'status': "10",
                            'message': "Your chosen proof of ID type from the dropdown menu appears to be incorrect.",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        responses.append(response)        

                            
                elif re.search(r'\d{9}\s*[vV]', text2) or re.search(r'\d{12}', text2) or (re.search(r'1968', text2) and re.search(r'32', text2)) or (re.search(r'1968', text2) and re.search(r'52', text2)):
                    if docType == 'NIC':
                        OldNIC_OCR = OCROldNICScan(images2)
                        hsv_image = cv2.cvtColor(images2, cv2.COLOR_BGR2HSV)
                        h, s, v = cv2.split(hsv_image)
                        average_brightness = cv2.mean(v)[0]

                        if average_brightness > 140:
                            output3 = OldNIC_OCR.process_file()
                            detail_dict = json.loads(output3['Details'])
                            if output3['Extraction'] == True:
                                error_code = "00"
                                message_code = "Success"
                            
                            if output3['Extraction'] == False:
                                error_code = "02"
                                message_code = "Document extraction failed"
                            response = {
                                    'userID': Unique_ID,
                                    'status': error_code,
                                    'message': message_code,
                                    'Extraction': output3['Extraction'],
                                    'Classification': True,
                                    'Name': detail_dict.get('Name', None),
                                    'familyName': detail_dict.get('familyName', None),
                                    'firstName': detail_dict.get('firstName', None),
                                    'middleName': detail_dict.get('middleName', None),
                                    'lastName': detail_dict.get('lastName', None),
                                    'nameInitials': detail_dict.get('nameInitials', None),
                                    'Licence_no':detail_dict.get('License No', None),
                                    'NIC':detail_dict.get('NIC', None),
                                    'Address': detail_dict.get('Address', None),
                                    'Issuedate': detail_dict.get('Issued Date', None),
                                    'Expirydate': None,
                                    'PassportNo': detail_dict.get('Passport No', None),
                                    }
                            responses.append(response)
                            
                        else:
                            response = {
                            'userID': Unique_ID,
                            'status': "03",
                            'message': "The image you entered is Low Quality",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                            'Issue': "Low_Brightness"
                        }
                            responses.append(response)

                    else:
                        response = {
                            'userID': Unique_ID,
                            'status': "10",
                            'message': "Your chosen proof of ID type from the dropdown menu appears to be incorrect.",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                        responses.append(response)

                else:
                    response = {
                            'userID': Unique_ID,
                            'status': "10",
                            'message': "Your chosen document seems to be invalid proof of ID type or low quality",
                            'Extraction': False,
                            'Classification': False,
                            'Name': None,
                            'familyName': None,
                            'firstName': None,
                            'middleName': None,
                            'lastName': None,
                            'nameInitials': None,
                            'Licence_no':None,
                            'NIC':None,
                            'Address': None,
                            'Issuedate': None,
                            'Expirydate': None,
                            'PassportNo': None,
                        }
                    responses.append(response)



                return jsonify(response)
            
            else:
                response = {
                                'userID': Unique_ID,
                                'status': "10",
                                'message': "Failed to accurately identify the input document. Kindly upload a more clear document",
                                'Extraction': False,
                                'Classification': False,
                                'Name': None,
                                'familyName': None,
                                'firstName': None,
                                'middleName': None,
                                'lastName': None,
                                'nameInitials': None,
                                'Licence_no':None,
                                'NIC':None,
                                'Address': None,
                                'Issuedate': None,
                                'Expirydate': None,
                                'PassportNo': None,
                            }
                responses.append(response)

            # # Log the JSON response and timestamp
            # logger.info('API PROCESSES COMPLETED: output: %s', json.dumps(response))
            # logger.info('Timestamp: %s', datetime.datetime.now())

            return jsonify(response)

        # If it's a GET request, return the upload form
        return '''
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" multiple>
            <input type="submit" value="Upload">
        </form>
        '''



@app.route('/bills', methods=['GET', 'POST'])
def upload_file1():
    if request.method == 'POST':
        # Extract the UserID from the form data
        new_file_path2 = None
        userID = request.form.get('UserID')
        Unique_ID = str(uuid.uuid4())

        logger.info('Response: %s', f"User ID has been passed to the API successfully: UserID: {Unique_ID}")
        logger.info('Timestamp: %s', datetime.datetime.now())

        #Type should be DL, NIC or PP
        docType = request.form.get('Doc_Type')

        # Check if the post request has the file part
        if 'file' not in request.files or len(request.files.getlist('file')) == 0:
            return 'No file selected', 400

        files = request.files.getlist('file')  # Get a list of uploaded files

        

        # # Create a folder specific to the user
        user_folder = os.path.join(app.config['UPLOAD_FOLDER2'], Unique_ID)
        os.makedirs(user_folder, exist_ok=True)

        # # Generate unique filenames for the uploaded files
        # filenames = [str(uuid.uuid4()) + '.jpg' for _ in range(len(files))]

        for i, file in enumerate(files):
            filename = secure_filename(file.filename)
            filepath = os.path.join(user_folder, filename)
            file.save(filepath)

        file_info = filetype.guess(filepath)
        if file_info is not None:
                file_type = file_info.mime
                if file_type == 'application/pdf':
                    FILE_TYPE = "PDF"
                    # Generate unique filenames for the uploaded files
                    filenames2 = [Unique_ID + '.jpg' for _ in range(len(files))]

                    # Save the files to the user's folder
                    for i, file in enumerate(files):
                        pdf_path = filepath
                        output_path = os.path.join(user_folder, filenames2[i])
                        images = cp(pdf_path, first_page=1, last_page=1)
                        new_file_path2 = output_path
                        images[0].save(output_path, 'JPEG')
                    os.remove(filepath)

                elif file_type.startswith('image/'):
                    FILE_TYPE = "IMG"
                    # Generate unique filenames for the uploaded files
                    filenames = [Unique_ID + '.jpg' for _ in range(len(files))]

                    # Save the files to the user's folder
                    for i, file in enumerate(files):
                        new_file_path2 = os.path.join(user_folder, filenames[i])
                        os.rename(filepath, os.path.join(user_folder, filenames[i]))


        logger.info('Response: %s', f"Files has been saved to the FSD successfully: Folder: {Unique_ID}")
        logger.info('Timestamp: %s', datetime.datetime.now())
        responses = []

        if len(files) == 0:
            return 'No file selected', 400

        elif len(files) == 1:
            for i, filename in enumerate(files):
                # try:
                # Process each uploaded file using the Classify class
                    classifier = BillClassify(cv2.imread(new_file_path2),FILE_TYPE)
                    result = classifier.process_file(new_file_path2)
                    logger.info('Document Classification Successful: %s', f"Classification Result: {result['file_type']}")
                    logger.info('Timestamp: %s', datetime.datetime.now())
                    new_filename = f"{Unique_ID}_{result['file_type']}.jpg"
                    new_file_path = os.path.join(user_folder, new_filename)
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    os.rename(new_file_path2, new_file_path)

                    if docType == "SLT":
                        docType = "Mobitel"
                    elif docType == "DLG":
                        docType = "Dialog"
                    elif docType == "ETB":
                        docType = "Electricity"
                    elif docType == "WTB":
                        docType = "Water"

                    if result['file_type'] == "Unknown_File":
                        error_code = "04"
                        message_code = "Unknown File"

                    if result['file_type'] == "Low_Quality":
                        error_code = "03"
                        message_code = "Low Quality Image"

                    if docType == result['file_type'] or docType in result['file_type']:
                        if result['file_type'] == "Electricity":
                            Elec_OCR = ElectricBillOCR(cv2.imread(os.path.join(user_folder, new_filename)))
                            output1 = Elec_OCR.process_file()
                            detail_dict = json.loads(output1['Details'])
                            if output1['Extraction'] == True and result['classification'] == True :
                                error_code = "00"
                                message_code = "Success"

                            elif output1['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output1['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            elif output1['Extraction'] == False and result['classification'] == False:
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input."

                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output1['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'AccountNo':detail_dict.get('Account No', None),
                            # 'DatePeriod':detail_dict.get('Bill Date', None),
                            'Name':detail_dict.get('Name', None),
                            'Address':detail_dict.get('Full_address', None),
                            'BillDate': detail_dict.get('Date', None),
                            }
                            

                        elif result['file_type'] == "Water":
                            Water_OCR = OCRwaterBill(cv2.imread(os.path.join(user_folder, new_filename)))
                            output2 = Water_OCR.process_file()
                            detail_dict = json.loads(output2['Details'])
                            if output2['Extraction'] == True and result['classification'] == True:
                                error_code = "00"
                                message_code = "Success"

                            elif output2['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output2['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            elif output2['Extraction'] == False and result['classification'] == False:
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input."
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output2['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'AccountNo':detail_dict.get('Acc No', None),
                            # 'DatePeriod':detail_dict.get('Date', None),
                            'Name':detail_dict.get('Name', None),
                            'Address':detail_dict.get('Full_address', None),
                            'BillDate': detail_dict.get('Bill Date', None),
                        }
                            

                        elif result['file_type'] == "Dialog":
                            DIALOG_OCR = OCRdialog(cv2.imread(os.path.join(user_folder, new_filename)))
                            output3 = DIALOG_OCR.process_file()
                            detail_dict = json.loads(output3['Details'])
                            if output3['Extraction'] == True and result['classification'] == True:
                                error_code = "00"
                                message_code = "Success"

                            elif output3['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output3['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            elif output3['Extraction'] == False and result['classification'] == False:
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input."
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output3['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'AccountNo':detail_dict.get('Acc No', None),
                            # 'DatePeriod':detail_dict.get('Date Period', None),
                            'Name':detail_dict.get('Name', None),
                            'Address':detail_dict.get('Full_address', None),
                            'BillDate': detail_dict.get('Bill Date', None),
                        }
                            
                        elif result['file_type'] == "Mobitel":
                            MOBITEL_OCR = OCRmobitel(cv2.imread(os.path.join(user_folder, new_filename)))
                            output4 = MOBITEL_OCR.process_file()
                            detail_dict = json.loads(output4['Details'])
                            if output4['Extraction'] == True and result['classification'] == True:
                                error_code = "00"
                                message_code = "Success"

                            elif output4['Extraction'] == True and result['classification'] == False:
                                error_code = "01"
                                message_code = "Document classification failed"

                            elif output4['Extraction'] == False and result['classification'] == True:
                                error_code = "02"
                                message_code = "Document extraction failed"

                            elif output4['Extraction'] == False and result['classification'] == False:
                                error_code = "10"
                                message_code = "Failed to process further due to inaccurate input."

                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': output4['Extraction'],
                            'Classification': result['classification'],
                            'status': error_code,
                            'message': message_code,
                            'AccountNo':detail_dict.get('Acc No', None),
                            # 'DatePeriod':detail_dict.get('Bill Period', None),
                            'Name':detail_dict.get('Name', None),
                            'Address':detail_dict.get('Full_address', None),
                            'BillDate': detail_dict.get('Bill Date', None),
                        }
                            
                        elif result['file_type'] == "Unknown":
                            response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': False,
                            'Classification': False,
                            'status': "04",
                            'message': "Input file type is unknown",
                            'AccountNo':detail_dict.get('Account No', None),
                            # 'DatePeriod':detail_dict.get('Date', None),
                            'Name':detail_dict.get('Name', None),
                            'Address':detail_dict.get('Full_address', None),
                            'BillDate': detail_dict.get('Bill Date', None),
                        }
                        responses.append(response)
                            
                        

                    else:
                        response = {
                            'userID': Unique_ID,
                            'folder': user_folder,
                            'filename': new_filename,
                            'Extraction': False,
                            'Classification': False,
                            'status': "10",
                            'message': "Your chosen proof of ID type from the dropdown menu appears to be incorrect.",
                            'AccountNo':None,
                            # 'DatePeriod':None,
                            'Name':None,
                            'Address':None,
                            'BillDate': None,
                        }
                        responses.append(response)

             # Log the JSON response and timestamp
            for response in responses:
                logger.info('API PROCESSES COMPLETED: output: %s', json.dumps(response))
                logger.info('Timestamp: %s', datetime.datetime.now())

            return jsonify(response)

    # If it's a GET request, return the upload form
    return '''
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" multiple>
        <input type="submit" value="Upload">
    </form>
    '''

@app.route('/NICSideClassifier', methods=['POST'])
def upload_file3():
    if 'NIC_Front' not in request.files or 'NIC_Back' not in request.files:
        return jsonify({'error': 'NIC_Front and NIC_Back files must be selected'}), 400

    front_image = request.files['NIC_Front']
    back_image = request.files['NIC_Back']

    if front_image.filename == '' or back_image.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    front_filename = secure_filename(front_image.filename)
    back_filename = secure_filename(back_image.filename)

    front_image.save(os.path.join(app.config['UPLOAD_FOLDER3'], front_filename))
    back_image.save(os.path.join(app.config['UPLOAD_FOLDER3'], back_filename))

    front_classifier = NICSideClassification(os.path.join(app.config['UPLOAD_FOLDER3'], front_filename))
    back_classifier = NICSideClassification(os.path.join(app.config['UPLOAD_FOLDER3'], back_filename))

    front_result = front_classifier.predict()
    back_result = back_classifier.predict()

    if front_result == "Front" and back_result == "Back":
        res = "00"
        description = "No Issues With NIC"


    else:
        res = "01"
        description = "Issue With The Uploaded NIC"

    response = {
        'NIC_Sides': res,
        'description': description
    }

    print("NIC_Sides: ", res)
    # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], front_filename))
    # os.remove(os.path.join(app.config['UPLOAD_FOLDER'], back_filename))

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0', port=5001)
