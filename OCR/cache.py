#PLEASE IGNORE THIS FILE. THIS IS ONLY USED TO KEEP TRACK OF THE CODE BEFORE EDITING FURTHER ON,

# import os
# import uuid
# from flask import Flask, request, jsonify
# import cv2
# import pytesseract
# from documentClassify import LegalDocClassify
# from license_OCR import OCRDrivingLicensescan
# from passport_OCR import OCRPassportscan
# from old_NIC_OCR import OCROldNICScan
# from new_NIC_OCR import OCRNewNICScan

# app = Flask(__name__)

# # Set the folder where the uploaded images will be stored
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/')
# def index():
#     return "Welcome to the Legal Documents Upload. To upload go to http://127.0.0.1:5001/upload"


# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'file' not in request.files:
#             return 'No file part in the request', 400

#         files = request.files.getlist('file')  # Get a list of uploaded files

#         if len(files) == 0:
#             return 'No file selected', 400

#         # Generate unique filenames for the uploaded files
#         filenames = [str(uuid.uuid4()) + '.jpg' for _ in range(len(files))]

#         # Save the files to the uploads folder
#         for i, file in enumerate(files):
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filenames[i]))

#         responses = []

#         for i, filename in enumerate(filenames):
#             # Process each uploaded file using the Classify class
#             classifier = LegalDocClassify(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#             result = classifier.process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#             if result['file_type'] == "Driving License":
#                 DL_OCR = OCRDrivingLicensescan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                 output1 = DL_OCR.process_file()
#                 response = {
#                     'filename': filename,
#                     'Extraction': output1['Extraction'],
#                     'Details': output1['Details']
#                 }
#                 responses.append(response)

#             elif result['file_type'] == "Passport":
#                 Passport_OCR = OCRPassportscan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                 output2 = Passport_OCR.process_file()
#                 response = {
#                     'filename': filename,
#                     'Extraction': output2['Extraction'],
#                     'Details': output2['Details']
#                 }
#                 responses.append(response)

#             elif result['file_type'] == "Old NIC":
#                 OldNIC_OCR = OCROldNICScan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                 output3 = OldNIC_OCR.process_file()
#                 response = {
#                     'filename': filename,
#                     'Extraction': output3['Extraction'],
#                     'Details': output3['Details']
#                 }
#                 responses.append(response)

#         return jsonify(responses)

#     # If it's a GET request, return the upload form
#     return '''
#     <form method="POST" enctype="multipart/form-data">
#         <input type="file" name="file" multiple>
#         <input type="submit" value="Upload">
#     </form>
#     '''


# if __name__ == '__main__':
#     app.run(debug=True, port=5001)



# 333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

# import cv2
# import pytesseract
# import re
# import json


# class OCRNewNICScan:
#   def __init__(self,imageF,imageB):
#     self.front = imageF
#     self.back = imageB

#   def preprocess(self):
#     self.grayF = cv2.cvtColor(self.front, cv2.COLOR_BGR2GRAY)
#     self.grayB = cv2.cvtColor(self.back, cv2.COLOR_BGR2GRAY)
#     thresh, self.im_bw = cv2.threshold(self.grayF, 135, 255, cv2.THRESH_BINARY)

#   def ocrExtract(self):
#     custom_config = r'--oem 3 --psm 6 '
#     self.ocrF = pytesseract.image_to_string(self.im_bw, config= custom_config)
#     self.ocrB = pytesseract.image_to_string(self.grayB, config= custom_config)

#   def remove_lowercase(self,lst):
#     result = []
#     for s in lst:
#         if s.islower():
#             continue
#         i = len(s) - 1
#         while i >= 0 and s[i].islower():
#             i -= 1
#         result.append(s[:i+1])
#     return result

#   def remove_lowercase_strings(self,lst):
#     return [elem for elem in lst if all(c.isupper() or not c.isalpha() for c in elem)]

#   def remove_replicating_substrings(self,lst):
#     new_lst = []

#     for i in range(len(lst)):
#         is_replicating = False
#         for j in range(len(lst)):
#             if i != j:
#                 if lst[i] in lst[j]:
#                     is_replicating = True
#                     break
#         if not is_replicating:
#             lst[i].strip()
#             new_lst.append(lst[i])

#     return new_lst

#   def textProcessing(self):
#     ocr_editedF = self.ocrF.split("\n")
#     ocr_editedB = self.ocrB.split("\n")

#     ocr_cleanedF = []
#     for item in ocr_editedF:
#       if item and not any(word in item for word in ['CEAW', 'NATIONAL', 'IDENTITY', 'DEMOCRATIC', 'Holder\'\s', 'Signature', '\\', '+','?',']','[','{','}','(',')','<','>']):
#         ocr_cleanedF.append(item)

#     ocr_cleanedF = self.remove_lowercase(ocr_cleanedF)
    
#     Back_regex_patterns = [
#       r'^\d+\/\d+(?:[-\w\s]*,[-\w\s]+)+[,.]', #Extract addresses
#       r'\d{4}\/\d{2}\/\d{2}',  # Matches date in format DD.MM. YYYY
#     ]


#     back_data = []
#     for item in ocr_editedB:
#       for pattern in Back_regex_patterns:
#         match = re.search(pattern, item)
#         if match:
#             back_data.append(match.group(0))
    
#     datas = self.remove_lowercase_strings(back_data)

#     N_back_data = []
#     for item in datas:
#       if re.search(Back_regex_patterns[0], item):
#         n_item = "Address: " + item
#         N_back_data.append(n_item)

#       if re.search(Back_regex_patterns[1], item):
#         n_item = "Issue Date: " + item
#         N_back_data.append(n_item)

#     Front_regex_patterns = [
#       r'\b[A-Z]{4,}\b', # Matches words with four or more uppercase letters.
#       r'\d{12}',  # Matches D followed by 7 digits
#       r'[A-Z]+\s[A-Z][A-Z\s]+\w',  # Matches two or more words in all caps followed by an alphanumeric character
#     ]

#     resultsF = []
#     for item in ocr_cleanedF:
#         for pattern in Front_regex_patterns:
#           match = re.search(pattern, item)
#           if match:
#             resultsF.append(match.group(0))

#     resultsF = [s for s in resultsF if not any(c.islower() for c in s)]
#     front_data = self.remove_replicating_substrings(resultsF)
#     front_data = self.remove_lowercase_strings(front_data)

#     N_front_data = []
#     for item in front_data:
#       if re.search(Front_regex_patterns[0], item):
#         n_item = "Name: " + item
#         N_front_data.append(n_item)

#       if re.search(Front_regex_patterns[1], item):
#         n_item = "NIC: " + item
#         N_front_data.append(n_item)

#     NIC_Data = N_front_data + N_back_data

#     name = []
#     for itm in NIC_Data:
#       if "Name: " in itm:
#         a, b = itm.split(":")
#         name.append(b)

#     Full_name = ''.join(name)
#     Full_name = "Full_name: " + Full_name
#     NIC_Data.append(Full_name)
#     self.Final_NIC_Data = [item for item in NIC_Data if "Name:" not in item]

#   def createDict(self):
#     NIC_Data_dict = {}

#     for item in self.Final_NIC_Data:
#       key_value_pair = item.split(": ")
#       NIC_Data_dict[key_value_pair[0]] = key_value_pair[1]
      
#     self.NIC_Data_dict = {key: value.strip() for key, value in NIC_Data_dict.items()}

#   def createJSON(self):
#     NIC = json.dumps(self.NIC_Data_dict)
#     return (NIC)
  
#   def getNewNIC_OCR(self):
#     self.preprocess()
#     self.ocrExtract()
#     self.textProcessing()
#     self.createDict()
#     output = self.createJSON()
#     return(output)
  
#   def process_file(self):
#     #img = cv2.imread(file_path)  # Read the uploaded image using OpenCV
#     result = self.getNewNIC_OCR()
#     return {
#             'Details': result,
#             'Extraction': 'Extracted Successfully'
#         }

##################################################################################################################################################3
# import os
# import uuid
# from flask import Flask, request, jsonify
# import cv2
# from documentClassify import LegalDocClassify
# from New_NIC_Classifier import NewNICClassify
# from license_OCR import OCRDrivingLicensescan
# from passport_OCR import OCRPassportscan
# from old_NIC_OCR import OCROldNICScan
# from new_NIC_OCR import OCRNewNICScan

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/')
# def index():
#     return "Welcome to the Legal Documents Upload! \nTo upload go to http://127.0.0.1:5001/upload"


# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return 'No file part in the request', 400

#         files = request.files.getlist('file')  # Get a list of uploaded files

#         if len(files) == 0:
#             return 'No file selected', 400

#         filenames = [str(uuid.uuid4()) + '.jpg' for _ in range(len(files))]

#         for i, file in enumerate(files):
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filenames[i]))

#         responses = []

#         if len(files) == 1:
#             for i, filename in enumerate(filenames):
#                 classifier = LegalDocClassify(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                 result = classifier.process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#                 if result['file_type'] == "Driving License":
#                     DL_OCR = OCRDrivingLicensescan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                     output1 = DL_OCR.process_file()
#                     response = {
#                         'filename': filename,
#                         'Extraction': output1['Extraction'],
#                         'Details': output1['Details']
#                     }
#                     responses.append(response)

#                 elif result['file_type'] == "Passport":
#                     Passport_OCR = OCRPassportscan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                     output2 = Passport_OCR.process_file()
#                     response = {
#                         'filename': filename,
#                         'Extraction': output2['Extraction'],
#                         'Details': output2['Details']
#                     }
#                     responses.append(response)

#                 elif result['file_type'] == "Old NIC":
#                     OldNIC_OCR = OCROldNICScan(cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
#                     output3 = OldNIC_OCR.process_file()
#                     response = {
#                         'filename': filename,
#                         'Extraction': output3['Extraction'],
#                         'Details': output3['Details']
#                     }
#                     responses.append(response)

#             return jsonify(responses)
        
#         elif len(files) == 2:
#             images1 = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filenames[0]))
#             images2 = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filenames[1]))
#             classifier = NewNICClassify(images1)
#             result = classifier.process_file()

#             if result == "New NIC Front":
#                 NewNIC_OCR = OCRNewNICScan(images1,images2)

#             else:
#                 NewNIC_OCR = OCRNewNICScan(images2,images1)

#             output4 = NewNIC_OCR.process_file()
#             response = {
#                         'Extraction': output4['Extraction'],
#                         'Details': output4['Details']
#                     }
#             responses.append(response)
#             return jsonify(responses)



#     return '''
#     <form method="POST" enctype="multipart/form-data">
#         <input type="file" name="file" multiple>
#         <input type="submit" value="Upload">
#     </form>
#         '''
    


# if __name__ == '__main__':
#     app.run(debug=True, port=5001)

########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################

# import os
# import uuid
# from flask import Flask, request, jsonify
# import cv2
# from documentClassify import LegalDocClassify
# from New_NIC_Classifier import NewNICClassify
# from license_OCR import OCRDrivingLicensescan
# from passport_OCR import OCRPassportscan
# from old_NIC_OCR import OCROldNICScan
# from new_NIC_OCR import OCRNewNICScan
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/')
# def index():
#     return "Welcome to the Legal Documents Upload! \nTo upload go to http://127.0.0.1:5001/upload"

# @app.route('/upload')
# def user():
#     return "Enter the user ID To upload the documents http://127.0.0.1:5001/upload/UserID"

# @app.route('/upload/<string:userID>', methods=['GET', 'POST'])
# def upload_file(userID):
#     if request.method == 'POST':
#         # Check if the post request has the file part
#         if 'file' not in request.files or len(request.files.getlist('file')) == 0:
#             return 'No file selected', 400

#         files = request.files.getlist('file')  # Get a list of uploaded files

#         # Create a folder specific to the user
#         user_folder = os.path.join(app.config['UPLOAD_FOLDER'], userID)
#         os.makedirs(user_folder, exist_ok=True)

#         # Generate unique filenames for the uploaded files
#         filenames = [str(uuid.uuid4()) + '.jpg' for _ in range(len(files))]

#         # Save the files to the user's folder
#         for i, file in enumerate(files):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(user_folder, filenames[i]))

#         responses = []

#         if len(files) == 0:
#             return 'No file selected', 400

#         elif len(files) == 1:
#             for i, filename in enumerate(filenames):
#                 try:
#                 # Process each uploaded file using the Classify class
#                     classifier = LegalDocClassify(cv2.imread(os.path.join(user_folder, filename)))
#                     result = classifier.process_file(os.path.join(user_folder, filename))
#                     new_filename = f"{userID}_{result['file_type']}.jpg"
#                     new_file_path = os.path.join(user_folder, new_filename)
#                     if os.path.exists(new_file_path):
#                         os.remove(new_file_path)
#                     os.rename(os.path.join(user_folder, filename), new_file_path)

#                     if result['file_type'] == "Driving_License":
#                         DL_OCR = OCRDrivingLicensescan(cv2.imread(os.path.join(user_folder, new_filename)))
#                         output1 = DL_OCR.process_file()
#                         response = {
#                         'userID': userID,
#                         'folder': user_folder,
#                         'filename': new_filename,
#                         'Extraction': output1['Extraction'],
#                         'Details': output1['Details']
#                         }
#                         responses.append(response)

#                     elif result['file_type'] == "Passport":
#                         Passport_OCR = OCRPassportscan(cv2.imread(os.path.join(user_folder, new_filename)))
#                         output2 = Passport_OCR.process_file()
#                         response = {
#                         'userID': userID,
#                         'folder': user_folder,
#                         'filename': new_filename,
#                         'Extraction': output2['Extraction'],
#                         'Details': output2['Details']
#                     }
#                         responses.append(response)

#                     elif result['file_type'] == "Old_NIC":
#                         OldNIC_OCR = OCROldNICScan(cv2.imread(os.path.join(user_folder, new_filename)))
#                         output3 = OldNIC_OCR.process_file()
#                         response = {
#                         'userID': userID,
#                         'folder': user_folder,
#                         'filename': new_filename,
#                         'Extraction': output3['Extraction'],
#                         'Details': output3['Details']
#                     }
#                         responses.append(response)

#                 except Exception as e:
#                 # Handle any other exceptions that may occur during processing
#                     response = {
#                         'error': f"Something went wrong when opening the file: {str(e)}"
#                     }

#                 return jsonify(responses)
            

    
#         elif len(files) == 2:
#             images1 = cv2.imread(os.path.join(user_folder, filenames[0]))
#             images2 = cv2.imread(os.path.join(user_folder, filenames[1]))
#             classifier = NewNICClassify(images1)
#             result = classifier.process_file()
#             for i,file in enumerate(filenames):
#                 new_filename1 = f"{userID}_New_NIC_{i}.jpg"
#                 new_file_path1 = os.path.join(user_folder, new_filename1)
#                 if os.path.exists(new_file_path1):
#                         os.remove(new_file_path1)
#                 os.rename(os.path.join(user_folder, file), new_file_path1)

#             if result == "New NIC Front":
#                 NewNIC_OCR = OCRNewNICScan(images1,images2)
                
#             else:
#                 NewNIC_OCR = OCRNewNICScan(images2,images1)
            
#             output4 = NewNIC_OCR.process_file()
#             response = {
#                 'userID': userID,
#                 'Extraction': output4['Extraction'],
#                 'Details': output4['Details']
#             }
#             responses.append(response)
#             return jsonify(responses)

#     # If it's a GET request, return the upload form
#     return '''
#     <form method="POST" enctype="multipart/form-data">
#         <input type="file" name="file" multiple>
#         <input type="submit" value="Upload">
#     </form>
#     '''

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)
