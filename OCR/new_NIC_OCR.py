import cv2
import pytesseract
import re
import json
import numpy as np
from datetime import datetime as dt
import logging
import datetime

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


class OCRNewNICScan:
    def __init__(self, imageF, imageB):
        self.front = imageF
        self.back = imageB

    def preprocess(self):
        self.grayB = cv2.cvtColor(self.back, cv2.COLOR_BGR2GRAY)

    def highlight_letters_numbers(self):
        gray = cv2.cvtColor(self.front, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=10)
        eroded = cv2.erode(dilated, kernel, iterations=10)

        self.result = cv2.bitwise_and(self.front, self.front, mask=eroded)
        self.result[eroded == 0] = 255

    def extract_dates(self, text):
        date_regex = r"\d{4}\d{2}\d{2}"  # Regular expression to match the date format (e.g., 20200821)
        dates = re.findall(date_regex, text)  # Find all occurrences of dates in the text

        formatted_dates = []
        for date in dates:
            try:
                datetime_obj = dt.strptime(date, "%Y%m%d")  # Convert the date string to a datetime object
                formatted_date = datetime_obj.strftime("%Y/%m/%d")  # Convert the datetime object to the desired date format
                formatted_dates.append(formatted_date)
            except ValueError:
                pass

        return formatted_dates

    def ocrExtract(self):
        custom_config = r'--oem 3 --psm 6 '

        self.ocrF = pytesseract.image_to_string(self.result, config=custom_config)
        self.ocrB = pytesseract.image_to_string(self.grayB, config=custom_config)


    def remove_lowercase(self, lst):
        result = []
        for s in lst:
            if s.islower():
                continue
            i = len(s) - 1
            while i >= 0 and s[i].islower():
                i -= 1
            result.append(s[:i + 1])
        return result

    def remove_lowercase_strings(self, lst):
        return [elem for elem in lst if all(c.isupper() or not c.isalpha() for c in elem)]

    def remove_replicating_substrings(self, lst):
        new_lst = []

        for i in range(len(lst)):
            is_replicating = False
            for j in range(len(lst)):
                if i != j:
                    if lst[i] in lst[j]:
                        is_replicating = True
                        break
            if not is_replicating:
                lst[i].strip()
                new_lst.append(lst[i])

        return new_lst

    def textProcessing(self):
        ocr_editedF = self.ocrF.split("\n")
        ocr_editedB = self.ocrB.split("\n")

        ocr_cleanedF = []
        for item in ocr_editedF:
            if item and not any(word in item for word in
                                ['CEAW','CSAW', 'DEQH', 'HOES', 'NATIONAL', 'IDENTITY', 'DEMOCRATIC', "Holder's", 'Signature',
                                 '\\', '+', '?', ']', '[', '{', '}', '<', '>']):
                ocr_cleanedF.append(item)

        ocr_cleanedF = self.remove_lowercase(ocr_cleanedF)

        Back_regex_patterns = [
            r'^\d+\/\d+(?:[-\w\s]*,[-\w\s]+)+[,.]',  # Extract addresses
            r"\b\d{1,4},\s[\w\s]+,\s[\w\s]+,\s[\w\s]+\b",  # address
            r'\d{4}\/\d{2}\/\d{2}',  # Matches date in format DD.MM. YYYY
            
        ]

        Date_patterns = [
            r'(\d{4})(\d{2})/(\d{2})',
            r'(\d{4})/(\d{2})(\d{2})',
        ]
        

        match = re.search(Date_patterns[0], self.ocrB) 
        match2 = re.search(Date_patterns[1], self.ocrB)

        if match:
            # Extract the captured parts
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)

            # Rearrange the parts into the desired format
            formatted_date = f"{year}/{month}/{day}"
            ocr_editedB.append(formatted_date)

        if match2:
            # Extract the captured parts
            year = match2.group(1)
            month = match2.group(2)
            day = match2.group(3)

            # Rearrange the parts into the desired format
            formatted_date = f"{year}/{month}/{day}"
            ocr_editedB.append(formatted_date)
   

        back_data_1 = []
        for item in ocr_editedB:
            for pattern in Back_regex_patterns:
                match = re.search(pattern, item)
                if match:
                    back_data_1.append(match.group(0))

        back_data = []
        for i in range(len(back_data_1)):
            is_replicating = False
            for j in range(len(back_data_1)):
                if i != j:
                    if back_data_1[i] in back_data_1[j]:
                        is_replicating = True
                        break
            if not is_replicating:
                back_data.append(back_data_1[i])

        dates = self.extract_dates(self.ocrB)
        back_data.extend(dates)

        datas = self.remove_lowercase_strings(back_data)

        N_back_data = []
        for item in datas:
            if re.search(Back_regex_patterns[2], item):
                n_item = "Issue Date: " + item
                N_back_data.append(n_item)

            else:
                n_item = "Address: " + item
                N_back_data.append(n_item)

        Front_regex_patterns = [
            r'\b[A-Z]{4,}\b',  # Matches words with four or more uppercase letters.
            r'\d{12}',  # Matches D followed by 7 digits
            r'[A-Z]+\s[A-Z][A-Z\s]+\w',  # Matches two or more words in all caps followed by an alphanumeric character
        ]

        resultsF = []
        for item in ocr_cleanedF:
            for pattern in Front_regex_patterns:
                match = re.search(pattern, item)
                if match:
                    resultsF.append(match.group(0))

        resultsF = [s for s in resultsF if not any(c.islower() for c in s)]
        front_data = self.remove_replicating_substrings(resultsF)
        front_data = self.remove_lowercase_strings(front_data)

        N_front_data = []
        for item in front_data:
            if re.search(Front_regex_patterns[0], item):
                n_item = "Name: " + item
                N_front_data.append(n_item)

            if re.search(Front_regex_patterns[1], item):
                n_item = "NIC: " + item
                N_front_data.append(n_item)

        NIC_Data = N_front_data + N_back_data

        name = []
        for itm in NIC_Data:
            if "Name: " in itm:
                a, b = itm.split(":")
                name.append(b)

        Full_name = ''.join(name)
        Full_name = "Full_name: " + Full_name
        NIC_Data.append(Full_name)
        self.Final_NIC_Data = [item for item in NIC_Data if "Name:" not in item]

    def createDict(self):
        NIC_Data_dict = {}

        for item in self.Final_NIC_Data:
            key_value_pair = item.split(": ")
            NIC_Data_dict[key_value_pair[0]] = key_value_pair[1]

        self.NIC_Data_dict = {key: value.strip() for key, value in NIC_Data_dict.items()}

        # if "NIC" in self.NIC_Data_dict:
        #     nic = self.NIC_Data_dict["NIC"]
        #     self.NIC_Data_dict["NIC"] = nic.replace("v", "V").replace(" ", "")
        if "NIC" in self.NIC_Data_dict:
            nic = self.NIC_Data_dict["NIC"]
            if not (nic.startswith("1") or nic.startswith("2")):
                # Replace the first character with '1' or '2' depending on the trailing number
                if nic[1] == "0":
                    nic = "2" + nic[1:]
                else:
                    nic = "1" + nic[1:]

                self.NIC_Data_dict["NIC"] = nic

        if "Full_name" in self.NIC_Data_dict:
            name = self.NIC_Data_dict["Full_name"]
            name_parts = name.split(" ")
            print("Names Length: ", len(name_parts))
            if len(name_parts) == 1:
                self.NIC_Data_dict["familyName"] = name_parts[0]
                self.NIC_Data_dict["firstName"] = name_parts[0]
                self.NIC_Data_dict["middleName"] = None
                self.NIC_Data_dict["lastName"] = name_parts[0]        

            if len(name_parts) == 2:
                self.NIC_Data_dict["familyName"] = name_parts[1]
                self.NIC_Data_dict["firstName"] = name_parts[0]
                self.NIC_Data_dict["middleName"] = None
                self.NIC_Data_dict["lastName"] = name_parts[1]

            if len(name_parts) == 3:
                self.NIC_Data_dict["familyName"] = name_parts[2]
                self.NIC_Data_dict["firstName"] = name_parts[0]
                self.NIC_Data_dict["middleName"] = name_parts[1]
                self.NIC_Data_dict["lastName"] = name_parts[2]

            if len(name_parts) > 3:
                self.NIC_Data_dict["familyName"] = name_parts[0]
                self.NIC_Data_dict["firstName"] = name_parts[1]
                self.NIC_Data_dict["middleName"] = name_parts[2]
                self.NIC_Data_dict["lastName"] = ' '.join(name_parts[2:])

        if "Full_name" in self.NIC_Data_dict:
            initials = []
            name = self.NIC_Data_dict["Full_name"]
            name_parts = name.split(" ")
            initials_name_part = name_parts[:-1]

            for name_part in initials_name_part:
                if name_part:
                    initials.append(name_part[0])
        
            last_name = name_parts[-1] 
            nameInitials = '.'.join(initials) + '.' + last_name
            self.NIC_Data_dict["nameInitials"] = nameInitials

    def createJSON(self):
        NIC = json.dumps(self.NIC_Data_dict)
        return NIC

    def getNewNIC_OCR(self):
        self.preprocess()
        self.highlight_letters_numbers()
        self.ocrExtract()
        self.textProcessing()
        self.createDict()
        output = self.createJSON()
        return output

    def process_file(self):
        result = self.getNewNIC_OCR()
        result = json.loads(result)
        logger.info('API PROCESSES COMPLETED: output: %s', json.dumps(result))
        logger.info('Timestamp: %s', datetime.datetime.now())

        return {
            'Details': result,
            'Extraction': True,
            'file_type': 'New NIC'
        }