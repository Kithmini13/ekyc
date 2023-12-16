from collections import namedtuple
import pytesseract
import cv2
import re
import numpy as np
import json

class OCRdialog:
    def __init__(self,img):
        self.image = cv2.resize(img, (1240,1750))


    def remove_duplicates(self,lst):
        result = []
        for item in lst:
            if item not in result:
                result.append(item)
        return result

    def extract_text(self):
        self.parsingResults = []
        height, width =  self.image.shape[:2]

        # Calculate the coordinates for cropping
        crop_start_y = int(height * 1/15)
        crop_end_y = int(height * 2/12)
        crop_start_x = int(width * 1/2)
        crop_end_x = int(width)

        # Calculate the coordinates for cropping
        crop_start_y2 = int(height * 1/17)
        crop_end_y2 = int(height * 3/17)
        crop_start_x2 = 0
        crop_end_x2 = int(width * 1/2)

        cropped_image = self.image[crop_start_y:crop_end_y, crop_start_x:crop_end_x]

        cropped_image2 = self.image[crop_start_y2:crop_end_y2, crop_start_x2:crop_end_x2]

        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        blacked = np.where(gray < 150, 0, gray)

        text = pytesseract.image_to_string(blacked)

        gray2 = cv2.cvtColor(cropped_image2, cv2.COLOR_BGR2GRAY)
        blacked2 = np.where(gray2 < 150, 0, gray2)

        text2 = pytesseract.image_to_string(blacked2)

        self.parsingResults.append(text)
        self.parsingResults.append(text2)

    def clean_text(self):
        list_of_strings = [str(t) for t in self.parsingResults]

        new_list = [s.split("\n") for s in list_of_strings]
        new_list = [[word for word in sublist if word != ' '] for sublist in new_list]
        list_without_blanks = sum(new_list, [])
        list_without_blanks
        ocr_cleaned = []

        for item in list_without_blanks:
                if item and not any(word in item for word in ['\x0c']):
                    ocr_cleaned.append(item)

        new_lst1 = self.remove_duplicates(ocr_cleaned)

        for i in range(len(ocr_cleaned)):
            ocr_cleaned[i] = ocr_cleaned[i].replace('BiLL PERIOD ', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('CONTRACT NUMBER ', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('BILL PERIOD ', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace(' BiLL PERIOD', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('MOBILE NUMBER ', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('SUBSCRIPTION NUMBER ', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('INVOICE DATE :', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('INVOICE', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('SUBSCRIPTION', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('CONTRACT', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('BILL', '')
            ocr_cleaned[i] = ocr_cleaned[i].replace('PERIOD', '')

        for i, item in enumerate(ocr_cleaned):
          ocr_cleaned[i] = item.strip()

        special_words = ["Mr", "Mrs", "Ms", "Rev"]
        ocr_cleaned = [item for item in ocr_cleaned if not any(c.islower() for c in item) or any(word in item for word in special_words)]



        patterns = [
                r"\d{9}",
                # r"\b[A-Za-z]*?(\d{8,10})\b",
                # r"\b[^A-Za-z\s]*(\d{9})\b",
                # r'\b(?:MR|MS|REV|HR|HS|MS,|Mr)\s[A-Z]+\s[A-Z]+\b',
                r'\b(MR|MS|MRS|REV|Mr|Mr.)\s*\.\s*[A-Z]\s*[A-Z]*\b',
                r"\b(MR|MS|MRS|REV|Mr|Mr.)\s*[A-Z]\s*[A-Z]\s*[A-Z]+\b",
                r'\d{2}/\d{2}/\d{4}\s*-\s*\d{2}/\d{2}/\d{4}',
                r'\d{2}/\d{2}/\d{4}',
                ]

        N_front_data = []
        for item in ocr_cleaned:

            if re.search(patterns[1], item) or re.search(patterns[2], item):
                n_item = "Name: " + item
                N_front_data.append(n_item)

            elif re.search(patterns[0], item):
              match = re.search(patterns[0], item)
              if match:
                  number_part = re.search(r'\d{9}', match.group()).group()
                  n_item = "Acc No: " + number_part
                  N_front_data.append(n_item)

            elif re.search(patterns[4], item):
              match = re.search(patterns[4], item)
              if match:
                  number_part = re.search(r'\d{2}/\d{2}/\d{4}', match.group()).group()
                  day,month,year = number_part.split("/")
                  new_date = f"{year}/{month}/{day}"
                  n_item = "Bill Date: " + new_date
                  N_front_data.append(n_item)


            elif re.search(patterns[3], item):
                n_item = "Bill Period: " + item
                N_front_data.append(n_item)
                date1, date2 = item.split("-")
                date1 = date1.strip()
                day,month,year = date1.split("/")
                new_date = f"{year}/{month}/{day}"
                n_item = "Bill Date: " + new_date
                N_front_data.append(n_item)

            else:
                n_item = "Address: " + item
                N_front_data.append(n_item)


        Address = []
        # if "Address" in N_front_data:
        for itm in N_front_data:
            if "Address: " in itm:
                a, b = itm.split(": ")
                Address.append(b.strip())

        Address = [item for item in Address if not re.search(r'\d{4,}', item)]
     
        Full_Address = ' '.join(Address)
        Full_Address = "Full_address: " + Full_Address
        N_front_data.append(Full_Address)
        Final_BILL_Data = [item for item in N_front_data if "Address: " not in item]


        BILL_Data_dict = {}

        for item in Final_BILL_Data:
            key_value_pair = item.split(": ")
            BILL_Data_dict[key_value_pair[0]] = key_value_pair[1]

        self.BILL_Data_dict = {key: value.strip() for key, value in BILL_Data_dict.items()}
  
        if "Name" in self.BILL_Data_dict:
          name_to_edit = self.BILL_Data_dict['Name']
          name_edited = name_to_edit.replace("Mr","").replace("MRS","").replace("MS","").replace("MR.","").replace("MRS.","").replace("MS.","").replace("MR ","")
          self.BILL_Data_dict['Name'] = name_edited

    def jsonify_test(self):
        Dialog_BILL = json.dumps(self.BILL_Data_dict)
        return Dialog_BILL

    def classify_dialog_bill(self):
        self.extract_text()
        self.clean_text()
        output = self.jsonify_test()
        return(output)

    def process_file(self):
        result = self.classify_dialog_bill()
        return {
                'Details': result,
                'Extraction': True
            }