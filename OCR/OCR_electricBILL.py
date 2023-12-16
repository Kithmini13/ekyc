from collections import namedtuple
import pytesseract
import cv2
import re
import numpy as np
import json

class ElectricBillOCR:
    def __init__(self,img):
        self.image = img
        self.original_height, self.original_width =  img.shape[:2]
        if self.original_height > self.original_width:
            self.TYPE = "NEW"
        else:
            self.TYPE = "OLD"

    def remove_duplicates(self,lst):
        result = []
        for item in lst:
            if item not in result:
                result.append(item)
        return result

    def extraction(self):
        self.parsingResults = []
        img = self.image.copy()
        height, width =  img.shape[:2]

        # Calculate the coordinates for cropping
        crop_start_y = 0
        crop_end_y = int(height * 1/3)
        crop_start_x = 0
        crop_end_x = int(width)

        # Calculate the coordinates for cropping
        crop_start_y2 = int(height * 15/16)
        crop_end_y2 = int(height)
        crop_start_x2 = 0
        crop_end_x2 = int(width)

        cropped_image = img[crop_start_y:crop_end_y, crop_start_x:crop_end_x]

        cropped_image2 = img[crop_start_y2:crop_end_y2, crop_start_x2:crop_end_x2]

        # self.image = cv2.resize(self.image,(2880,2256))
        resized_image = cv2.resize(self.image, (2880,2256))

        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        eroded_img = cv2.erode(gray, kernel, iterations=1)
        blacked2 = np.where(eroded_img < 192, 0, eroded_img)


            # perform OCR on the binarized image
        text2 = pytesseract.image_to_string(blacked2,config='-c tessedit_char_whitelist= ()ABCDEFTGHIJKLMNOPQRSTUVWXTZ/,-0123456789/\-')
        self.parsingResults.append(text2)


        # apply thresholding to binarize the image
        gray = cv2.cvtColor(cropped_image2, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        eroded_img = cv2.erode(gray, kernel, iterations=1)
        blacked = np.where(eroded_img < 195, 0, eroded_img)


        # perform OCR on the binarized image
        text = pytesseract.image_to_string(blacked,config='-c tessedit_char_whitelist= ()ABCDEFTGHIJKLMNOPQRSTUVWXTZ/,-0123456789/\-')

        # add the result to the parsing results list
        self.parsingResults.append(text)

    def extraction_NEW(self):
        self.parsingResults = []
        img = self.image.copy()
        height, width =  img.shape[:2]

        crop_start_y = int(height * 1/12)
        crop_end_y = int(height * 1/5)
        crop_start_x = 0
        crop_end_x = int(width *1/3)

        # Calculate the coordinates for cropping
        crop_start_y2 = int(height * 2/6)
        crop_end_y2 = int(height * 3/5)
        crop_start_x2 = 0
        crop_end_x2 = int(width *1/3)

        # Calculate the coordinates for cropping
        crop_start_y3 = int(height * 1/12)
        crop_end_y3 = int(height * 1/5)
        crop_start_x3 = int(width *3/4)
        crop_end_x3 = int(width)

        cropped_image = img[crop_start_y:crop_end_y, crop_start_x:crop_end_x]

        cropped_image2 = img[crop_start_y2:crop_end_y2, crop_start_x2:crop_end_x2]

        cropped_image3 = img[crop_start_y3:crop_end_y3, crop_start_x3:crop_end_x3]

        # self.image = cv2.resize(self.image,(2880,2256))
        resized_image = cv2.resize(self.image, (2880,2256))

        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        eroded_img = cv2.erode(gray, kernel, iterations=1)
        blacked2 = np.where(gray < 192, 0, eroded_img)



            # perform OCR on the binarized image
        self.text2 = pytesseract.image_to_string(gray,config='--oem 3 --psm 6')
        self.parsingResults.append(self.text2)


        gray = cv2.cvtColor(cropped_image3, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        eroded_img = cv2.erode(gray, kernel, iterations=1)
        blacked2 = np.where(gray < 192, 0, eroded_img)


            # perform OCR on the binarized image
        self.text3 = pytesseract.image_to_string(gray,config='-c tessedit_char_whitelist= ()ABCDEFTGHIJKLMNOPQRSTUVWXTZ/,-0123456789/\-')
        self.parsingResults.append(self.text3)


        # apply thresholding to binarize the image
        gray2 = cv2.cvtColor(cropped_image2, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2,2), np.uint8)
        eroded_img = cv2.erode(gray2, kernel, iterations=1)
        blacked = np.where(eroded_img < 195, 0, eroded_img)


        # perform OCR on the binarized image
        self.text = pytesseract.image_to_string(gray2,config='-c tessedit_char_whitelist= ()ABCDEFTGHIJKLMNOPQRSTUVWXTZ/,-0123456789/\-')

        # add the result to the parsing results list
        self.parsingResults.append(self.text)

    def cleanText(self):
        if self.TYPE == "OLD":
            list_of_strings = [str(t) for t in self.parsingResults]
            new_list = [s.split("\\n") for s in list_of_strings]
            new_list = [[word for word in sublist if word != ' '] for sublist in new_list]
            list_without_blanks = sum(new_list, [])
            patterns = [r"\b\d{10}\b",
                    r"\b\d+/\d+\s+\w+\s+\w+\b",
                    r'\b[A-Z]+\b',
                    r'\b[A-Z]{4,}\b',
                    r'\d{2}\/\d{2}\/\d{2}',
                    r'\b[A-Z]\s[A-Z\s]+(?<!\b[A-Z]{2}\b)',
                    r"^[A-Z](?: [A-Z]){1,} [A-Z]+$",
                    ]

            results = []
            for item in list_without_blanks:
                for pattern in patterns:
                    match = re.search(pattern, item)
                    if match:
                        results.append(match.group(0))

            ocr_cleaned = []
            for item in results:
                if item and not any(word in item for word in ['x0c', 'PRINT', 'SMS', 'ACC', 'Req', 'BANA']):
                    ocr_cleaned.append(item)



            ocr_cleaned = [x for x in ocr_cleaned if len(x) > 3]
            new_lst1 = self.remove_duplicates(ocr_cleaned)

            new_lst = []

            for i in range(len(new_lst1)):
                is_replicating = False
                for j in range(len(new_lst1)):
                    if i != j:
                        if new_lst1[i] in new_lst1[j]:
                            is_replicating = True
                            break
                if not is_replicating:
                    new_lst1[i].strip()
                    new_lst.append(new_lst1[i])

            N_front_data = []
            for item in new_lst:

                if re.search(patterns[6], item): 
                    n_item = "Name: " + item
                    N_front_data.append(n_item)

                elif re.search(patterns[0], item):
                    n_item = "Account No: " + item
                    N_front_data.append(n_item)

                elif re.search(patterns[4], item):
                    n_item = "Date: " + item
                    N_front_data.append(n_item)

                # elif re.search(patterns[1], item):
                #     n_item = "Address: " + item
                #     N_front_data.append(n_item)

                # elif re.search(patterns[3], item):
                #     n_item = "Address: " + item
                #     N_front_data.append(n_item)

                else:
                    n_item = "Address: " + item
                    N_front_data.append(n_item)


            Address = []
            for itm in N_front_data:
                if "Address: " in itm:
                    a, b = itm.split(":")
                    Address.append(b)

            Full_Address = ''.join(Address)
            Full_Address = "Full_address: " + Full_Address
            N_front_data.append(Full_Address)
            Final_BILL_Data = [item for item in N_front_data if "Address:" not in item]

            BILL_Data_dict = {}

            for item in Final_BILL_Data:
                key_value_pair = item.split(": ")
                BILL_Data_dict[key_value_pair[0]] = key_value_pair[1]

                self.BILL_Data_dict = {key: value.strip() for key, value in BILL_Data_dict.items()}

            if "Date" in self.BILL_Data_dict:
                date = self.BILL_Data_dict["Date"] 
                if re.match(r"\d{2}/\d{2}/\d{2}$", date):
                    year, month, day = date.split("/")
                    self.BILL_Data_dict["Date"] = f"20{year}/{month}/{day}"
                elif re.match(r"\d{2}/\d{2}/\d{4}$", date):
                    year, month, day = date.split("/")
                    self.BILL_Data_dict["Date"] = f"{year}/{month}/{day}"
        
        if self.TYPE == "NEW":
            new_list1 = self.text.split("\n")
            new_list2 = self.text2.split("\n")
            new_list3 = self.text3.split("\n")
   


            patterns1 = [r"\b\d{10}\b",
                    ]

            patterns2 = [
                    r"\b\d+/\d+\s+\w+\s+\w+\b",
                    r'\b[A-Z]\s[A-Z\s]+(?<!\b[A-Z]{2}\b)',
                    r'\b[A-Z]+\s(?:[A-Z](?!\b)\s)*[A-Z]{4,}\b',
                    r'\b[A-Z]+\b',
                    ]

            patterns3 = [
                    r'\d{2}\/\d{2}\/\d{2}',
                    r'\d{4}\-\d{2}\-\d{2}',
                    ]


            results1 = []
            results2 = []
            results3 = []
            for item in new_list1:
                for pattern in patterns3:
                    match = re.search(pattern, item)
                    if match:
                        results1.append(match.group(0))

            for item in new_list3:
                for pattern in patterns1:
                    match = re.search(pattern, item)
                    if match:
                        results3.append(match.group(0))

            substrings_to_remove = ['Rev', 'Mr', 'Mrs', 'Reg.', 'Mobile No', '\x0c']
            results2 = [element for element in new_list2 if not any(substring in element for substring in substrings_to_remove)]
            results2_new = [element for element in results2 if element]

            results1_new = []
            if results1:
                element = results1[0]
                results1_new.append( "Date: " + element)

            if results3:
                element = results3[0]
                results3[0] = "Account No: " + element

            if results2_new:
                for i, element in  enumerate(results2_new):
                    if i == 0:
                        results2_new[0] = "Name: " + element
                    else:
                        results2_new[i] = "Address: " + element


            N_front_data = results1_new + results2_new + results3

            Address = []
            for itm in N_front_data:
                if "Address: " in itm:
                    a, b = itm.split(":")
                    Address.append(b)

            Full_Address = ''.join(Address)
            Full_Address = "Full_address: " + Full_Address
            N_front_data.append(Full_Address)
            Final_BILL_Data = [item for item in N_front_data if "Address:" not in item]

            BILL_Data_dict = {}

            for item in Final_BILL_Data:
                key_value_pair = item.split(": ")
                BILL_Data_dict[key_value_pair[0]] = key_value_pair[1]

                self.BILL_Data_dict = {key: value.strip() for key, value in BILL_Data_dict.items()}

            if "Date" in self.BILL_Data_dict:
                date = self.BILL_Data_dict["Date"]
                if re.match(r"\d{2}/\d{2}/\d{2}$", date):
                    year, month, day = date.split("/")
                    self.BILL_Data_dict["Date"] = f"20{year}/{month}/{day}"
                    # print(self.BILL_Data_dict["Date"])
                elif re.match(r"\d{2}/\d{2}/\d{4}$", date):
                    day, month, year = date.split("/")
                    self.BILL_Data_dict["Date"] = f"{year}/{month}/{day}"
                    # print(self.BILL_Data_dict["Date"])
                elif re.match(r"\d{4}-\d{2}-\d{2}$", date):
                    year, month, day = date.split("-")
                    self.BILL_Data_dict["Date"] = f"{year}/{month}/{day}"
                    # print(self.BILL_Data_dict["Date"])


    def jsonifyOut(self):
        BILL = json.dumps(self.BILL_Data_dict)
        return BILL

    def classify_electric_bill(self):
        
        if self.TYPE == "OLD":
            self.extraction()
        if self.TYPE == "NEW":
            self.extraction_NEW()
        self.cleanText()
        output = self.jsonifyOut()
        return(output)

    def process_file(self):
        result = self.classify_electric_bill()
        return {
                'Details': result,
                'Extraction': True
            }