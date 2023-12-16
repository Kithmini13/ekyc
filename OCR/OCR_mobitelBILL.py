from collections import namedtuple
import pytesseract
import cv2
import re
import numpy as np
import json

class OCRmobitel:
  def __init__(self,img):
    self.image1 = img
    self.image = cv2.resize(self.image1, (1240, 1755))
    # self.BILL_Data_dict = {}

  def remove_duplicates(self,lst):
    result = []
    for item in lst:
        if item not in result:
            result.append(item)
    return result

  def extract_text(self):
    OCRLocation = namedtuple("OCRLocation", ["bbox","filter_keywords"])

    self.OCR_LOCATIONS = [
	    OCRLocation((270, 259, 260, 241),
		    ["BILL", "ACCOUNT", "NUMBER."]),
      OCRLocation((571, 240, 429, 189),
		    [" "]),
    ]

    self.parsingResults = []
    self.cropped_images = []
    
    for i, loc in enumerate(self.OCR_LOCATIONS):
        x, y, w, h = loc.bbox
        roi = self.image[y:y+h, x:x+w]
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2, 2), np.uint8)
        blacked = np.where(gray < 120, 0, gray)
        
        text = pytesseract.image_to_string(blacked)
        
        self.parsingResults.append(text)
        self.cropped_images.append(blacked)

  def clean_text(self):
    list_of_strings = [str(t) for t in self.parsingResults]
    new_list = [s.split("\n") for s in list_of_strings]
    new_list = [[word for word in sublist if word != ' '] for sublist in new_list]
    list_without_blanks = sum(new_list, [])
    ocr_cleaned = []
    for item in list_without_blanks:
        if item and not any(word in item for word in ['\x0c']):
          ocr_cleaned.append(item)

    new_lst1 = self.remove_duplicates(ocr_cleaned)
    for i in range(len(new_lst1)):
        new_lst1[i] = new_lst1[i].replace('!', '')
        new_lst1[i] = new_lst1[i].replace('@', '')
        new_lst1[i] = new_lst1[i].replace('#', '')
        new_lst1[i] = new_lst1[i].replace('$', '')
        new_lst1[i] = new_lst1[i].replace('%', '')
        new_lst1[i] = new_lst1[i].replace('^', '')
        new_lst1[i] = new_lst1[i].replace('&', '')
        new_lst1[i] = new_lst1[i].replace('*', '')
        new_lst1[i] = new_lst1[i].replace('~', '')


    new_lst1 = [item.strip() for item in new_lst1]
    patterns = [
            r"^\d{3}\s\d{3}\s\d{4}$",
            r"^\d{3}\s\d{3}\s\d{3}[A-Za-z]$",
            r"\b(Mr|Mrs|Ms|Mr |Mrs |Ms )\.?([A-Za-z]+)",
            # r"^(?:Mr|Miss|Ms)\s(?:[A-Z]\.?)+\s[A-Z][a-z]+\s(?:[A-Z]\.?)+[A-Z][a-z]+$",
            # r'\b(MR|MS|MRS|REV|Mr|Mr.)\s*\.\s*[A-Z]\s*[A-Z]\b',
            # r"\b(MR|MS|MRS|REV|Mr|Mr.)\s[A-Z]\s*[A-Z]\s*[A-Z]+\b",
            r"\d{2}/\d{2}/\d{4}\s*-\s*\d{2}/\d{2}/\d{4}",
            r'\d{2}/\d{2}/\d{4}',

            ]
    
    # for i, ele in enumerate(new_lst1): 
    #   new_lst1[i] = ele.replace(",", "").replace("."," ")

    N_front_data = []
    for item in new_lst1:
      if re.search(patterns[3], item):
        n_item = "Bill Period: " + item
        N_front_data.append(n_item)
      
      elif re.search(patterns[4], item):
          match = re.search(patterns[4], item)
          if match:
              number_part = re.search(r'\d{2}/\d{2}/\d{4}', match.group()).group()
              day,month,year = number_part.split("/")
              new_date = f"{year}/{month}/{day}"
              n_item = "Bill Date: " + new_date
              N_front_data.append(n_item)

      elif re.search(patterns[2], item):
        n_item = "Name: " + item
        N_front_data.append(n_item)

      elif re.search(patterns[0], item) or re.search(patterns[1], item):
        n_item = "Acc No: " + item
        N_front_data.append(n_item)

      # elif re.search(patterns[1], item):
      #   n_item = "Name: " + item
      #   N_front_data.append(n_item)

      else:
        n_item = "Address: " + item
        N_front_data.append(n_item)
    

    Address = []
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

    for item in N_front_data:
      key_value_pair = item.split(": ")
      BILL_Data_dict[key_value_pair[0]] = key_value_pair[1]

      self.BILL_Data_dict = {key: value.strip() for key, value in BILL_Data_dict.items()}
    
    if "Name" in self.BILL_Data_dict:
      name_to_edit = self.BILL_Data_dict['Name']
      name_edited = name_to_edit.replace("Mr", "").replace("Mrs", "").replace("Rev", "").replace("_Mr", "").replace("_Mrs", "").replace("(_Rev", "").replace("_Ms", "").replace("Ms", "").replace("|", "I")
      name_edited_final = name_edited.strip()
      self.BILL_Data_dict['Name'] = name_edited_final


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