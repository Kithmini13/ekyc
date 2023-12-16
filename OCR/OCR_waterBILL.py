from collections import namedtuple
import pytesseract
import cv2
import re
import numpy as np
import json

class OCRwaterBill:
  def __init__(self,img):
    self.image = img
    height, width, c = self.image.shape
    if height > width:
        self.bill_type = "Half"
    else:
        self.bill_type = "Full"

    hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    self.average_brightness = cv2.mean(v)[0]

  def remove_duplicates(self,lst):
    result = []
    for item in lst:
        if item not in result:
            result.append(item)
    return result
  
  def forceDateExtraction(self):
      img = self.image.copy()
      height, width =  img.shape[:2]

      # Calculate the coordinates for cropping
      crop_start_y = int(height * 2/6)
      crop_end_y = int(height * 3/8)
      crop_start_x = int(width *1/17)
      crop_end_x = int(width *1/5)

      cropped_image = img[crop_start_y:crop_end_y, crop_start_x:crop_end_x]
      blacked2 = np.where(cropped_image < self.average_brightness - 6 , 0, cropped_image)

      text = pytesseract.image_to_string(blacked2, config = r'--oem 3 --psm 6')

      match = re.search(r'\d{2}\-\d{2}\-\d{4}', text)
      extracted_variable = match.group() if match else None
      if extracted_variable is not None:
        day, month, year = extracted_variable.split("-")
        modified_date = f"{year}/{month}/{day}"
        return (modified_date)

      else:
        return (extracted_variable)

  def extract_text(self):
    if self.bill_type == "Half":
        OCRLocation = namedtuple("OCRLocation", ["id", "bbox",
            "filter_keywords"])

        self.OCR_LOCATIONS = [
        OCRLocation("No&Date", (221, 80, 323, 75),
            ["INVOICE", "ACCT", "No."]),
        OCRLocation("Name&Address", (17, 63, 194, 30),
            ["/"]),
        OCRLocation("Name&Address", (25, 272, 138, 36),
            ["/"]),
        ]

        resized_image = cv2.resize(self.image, (553,746))

        self.parsingResults = []

        for loc in self.OCR_LOCATIONS:
            x, y, w, h = loc.bbox
            roi = resized_image[y:y+h, x:x+w]

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((2,2), np.uint8)
            eroded_img = cv2.erode(gray, kernel, iterations=1)
            text = pytesseract.image_to_string(eroded_img)

            self.parsingResults.append((loc.id, text))

    else:
        OCRLocation = namedtuple("OCRLocation", ["id", "bbox",
            "filter_keywords"])

        self.OCR_LOCATIONS = [
        OCRLocation("No&Date", (2059, 643, 885, 282),
            ["INVOICE", "ACCT", "No."]),
        OCRLocation("Name&Address", (719, 233, 1028, 262),
            ["/"]),
        OCRLocation("Name&Address", (83, 823, 464, 164),
            ["/"]),
        ]

        resized_image = cv2.resize(self.image, (3088,2400))

        self.parsingResults = []

        for loc in self.OCR_LOCATIONS:
            x, y, w, h = loc.bbox
            roi = resized_image[y:y+h, x:x+w]

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((2,2), np.uint8)
            eroded_img = cv2.erode(gray, kernel, iterations=3)
            text = pytesseract.image_to_string(eroded_img)

            self.parsingResults.append((loc.id, text))

  def clean_text(self):
        list_of_strings = [str(t) for t in self.parsingResults]

        new_list = [s.split("\\n") for s in list_of_strings]
        new_list = [[word for word in sublist if word != ' '] for sublist in new_list]

        new_list = [[s for s in sub_list if s != ''] for sub_list in new_list]

        list_without_blanks = sum(new_list, [])

        patterns = [r"\d+[-/]?\d*(?:[-/]?\d*)?[A-Z]?",
                #r"\b\d+/\d+\s+\w+\s+\w+\b",
                r'[A-Z\s/]+',
                #r'\b[A-Z]{4,}\b',
                # r'\b(?:MR|MS|REV|HR|HS|MS,|Mrs.|Mrs)\s[A-Z]+\s[A-Z]+\b',
                r'\b(?:MR|MS|REV|HR|HS|MS,|Mrs\.?)(?:\s[A-Z]+\b)+',
                r'\b\d{2}\/\d{2}\/\d{3}\/\d{3}\/\d{2}\b',
                r'\d{2}\-\d{2}\-\d{4}',
                r'\b\d{1}\/\d{2}\/\d{3}\/\d{3}\/\d{2}\b',
                r'.*\/\/.*\/\/.*',
                #r'\b[A-Z]\s[A-Z\s]+(?<!\b[A-Z]{2}\b)',
                ]

        results = []
        for item in list_without_blanks:
            for pattern in patterns:
                match = re.search(pattern, item)
                if match:
                    results.append(match.group(0))


        ocr_cleaned = []
        for item in results:
            if item and not any(word in item for word in ['x0c', 'INVOICE ', 'ACCT']):
                ocr_cleaned.append(item)


        for item in ocr_cleaned:
            if len(item) < 3:
                ocr_cleaned.remove(item)

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

        for i,  ele in enumerate(new_lst):
          new_lst[i] = ele.replace(",", "")


        N_front_data = []
        for item in new_lst:
            if re.search(patterns[2], item):
                n_item = "Name: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[3], item):
                n_item = "Acc No: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[5], item):
                n_item = "Acc No: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[6], item):
                n_item = "Acc No: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[4], item):
                n_item = "Bill Date: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[0], item):
                n_item = "Address: " + item
                N_front_data.append(n_item)
            elif re.search(patterns[1], item):
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


        if "Bill Date" in self.BILL_Data_dict:
          date = self.BILL_Data_dict["Bill Date"]
          day, month, year = date.split("-")
          modified_date = f"{year}/{month}/{day}"
          self.BILL_Data_dict["Bill Date"] = modified_date

        if "Name" in self.BILL_Data_dict:
          name = self.BILL_Data_dict["Name"]
          modified_name = name.replace("HR", "").replace("MR", "").replace("MS", "").replace("HS", "").replace("REV", "").replace("Mrs.", "").strip()
          self.BILL_Data_dict["Name"] = modified_name

        if "Bill Date" not in self.BILL_Data_dict:
          date_extracted = self.forceDateExtraction()
          if date_extracted is not None:
            self.BILL_Data_dict["Bill Date"] = date_extracted

  def jsonify_text(self):
    Mobitel_BILL = json.dumps(self.BILL_Data_dict)
    return Mobitel_BILL

  def classify_mobitel_bill(self):
        self.extract_text()
        self.clean_text()
        output = self.jsonify_text()
        return(output)

  def process_file(self):
        result = self.classify_mobitel_bill()
        return {
                'Details': result,
                'Extraction': True
            }