import cv2
import pytesseract
import re
from datetime import datetime
import json
from collections import namedtuple

class OCRDrivingLicensescan:
  def __init__(self,image2):
    self.img1 = image2  
    self.img2 = cv2.resize(self.img1, (1061, 665))
    self.ocr_cleaned = []


  def grayScale(self):
    self.gray = cv2.cvtColor(self.img2, cv2.COLOR_BGR2GRAY)

  def ocrText(self):
    self.parsingResults = []
    OCRLocation = namedtuple("OCRLocation", ["id", "bbox","filter_keywords"])
    OCR_LOCATIONS = [
	      OCRLocation("ID", (250, 115, 770, 135),["ID: "]),
        OCRLocation("NAme", (280, 240, 490, 260),["Name: "]),
    ]
    
    for loc in OCR_LOCATIONS:
        # extract the region of interest using the bounding box
        x, y, w, h = loc.bbox
        roi = self.img2[y:y+h, x:x+w]

        # cv2.imshow("ROI", roi)
        # cv2.waitKey(0)  # Wait for a key press before moving to the next ROI
        # cv2.destroyAllWindows()

        self.gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        self.ocr = pytesseract.image_to_string(self.gray)
        self.parsingResults.append(self.ocr)

  def is_date(self,item):
    # Check if the given item is a valid date string
    date_format = '%d.%m.%Y'
    try:
        datetime.strptime(item, date_format)
        return True
    except ValueError:
        return False
    
  def remove_oldest_and_futurest_dates(self,lst):
    # Convert date strings to datetime objects
    date_format = '%d.%m.%Y'
    dates = [datetime.strptime(item, date_format) for item in lst if self.is_date(item)]
    print("NO OF DATES: ", len(dates))

    # Remove the oldest and most future dates
    if dates:
        oldest_date = min(dates)
        futurest_date = max(dates)
        lst = [item for item in lst if not (self.is_date(item) and (datetime.strptime(item, date_format) == oldest_date or datetime.strptime(item, date_format) == futurest_date))]

    if futurest_date and len(dates) > 2:
       ExpDate = futurest_date
    else:
       ExpDate = None
       futurest_date = futurest_date.strftime('%d.%m.%Y')
       lst.append(str(futurest_date))

    print("LST DATE PASSED: ", lst)

    return lst, ExpDate
  
  def merge_address_values(self,lst):
    merged_list = []
    address_values = []
    
    for item in lst:
        if item.startswith('Address:'):
            address_values.append(item.replace('Address: ', ''))
        else:
            merged_list.append(item)
    
    if len(address_values) > 0:
        merged_list.append('Address: ' + ' '.join(address_values))
    
    return merged_list
  
  def merge_block_letter_words(self,lst):
    merged_list = []
    block_words = []

    for item in lst:
        if re.match(r'\b[A-Z]+\b', item):
            block_words.append(item)
        else:
            merged_list.append(item)

    if len(block_words) > 0:
        merged_list.append(' '.join(block_words))

    return merged_list

    
  def cleaningText(self):
    self.ocr = self.parsingResults
    ocr1_b = self.ocr[0].split("\n")
    ocr2_b = self.ocr[1].split("\n")

    ocr1 = []
    for item in ocr1_b:
        if item and not any(word in item for word in ['DRIVING LICENCE NO', 'NATIONAL IDENTITY CARD NO', 'REPUBLIC', 'DEMOCRATIC', 'SOCIALIST', 'Signature']):
            ocr1.append(item)

    ocr2 = []
    for item in ocr2_b:
        if item and not any(word in item for word in ['DRIVING LICENCE NO', 'NATIONAL IDENTITY CARD NO', 'REPUBLIC', 'DEMOCRATIC', 'SOCIALIST', 'Signature']):
            ocr2.append(item)

    # print("ocr1", ocr1)
    # print("ocr2", ocr2)

    patterns = [r"\d{2}\.\d{2}\. \d{4}",
                r"\d{2}\. \d{2}\.\d{4}",
                r"\d{2}\. \d{2}\. \d{4}",
                ]  # Pattern to match the date format "dd.mm.yyyy"

    for i in range(len(ocr2)):
      for pattern in patterns:
          date_matches = re.findall(pattern, ocr2[i])
          for date in date_matches:
              date_no_space = date.replace(" ", "")  # Remove whitespace from the date
              ocr2[i] = ocr2[i].replace(date, date_no_space)

  
    # print("Stage 2: OCR2: ", ocr2)

    regex_patterns = [
      r'B\d{6,7}',  # Matches B followed by 7 digits
      r'\d{9}',  # Matches 9 digits followed by V
      r'\d{12}',
      r'\d+/\d+\s+(?:(?![a-z])[^\s])+\s*(?:(?:(?![a-z])[^\s])+\s*)*',  # Matches digits/digits followed by two or more words
      r'[A-Z]\s\d+/\d+\s+(?:(?![a-z])[^\s])+\s*(?:(?:(?![a-z])[^\s])+\s*)*',
      r'[A-Z]{2}\s\d+/\d+\s+(?:(?![a-z])[^\s])+\s*(?:(?:(?![a-z])[^\s])+\s*)*',
      r'^\d+\/\d+(?:[-\w\s]*,[-\w\s]+)+[,.]',
      r'\d+/\d+[A-Za-z]+\s[A-Za-z\s]+',
      r'\b[A-Z]{4,}\b', # Matches words with four or more uppercase letters.
      r'[A-Z]+\s[A-Z][A-Z\s]+\w',  # Matches two or more words in all caps followed by an alphanumeric character
      r'\d{2}\.\d{2}\.\d{4}',  # Matches date in format DD.MM.YYYY
      r'\d{2}\.\s\d{2}\.\s\d{4}',  # Matches date in format DD.MM. YYYY
      r'B\d{6,7}D',  # Matches B followed by 7 digits
      r"\d+\s+[A-Za-z\s]+"
    ]

    results1 = []
    for item in ocr1:
      for pattern in regex_patterns:
        match = re.search(pattern, item)
        if match:
          results1.append(match.group(0))

    results2 = []
    for item in ocr2:
      for pattern in regex_patterns:
        match = re.search(pattern, item)
        if match:
          results2.append(match.group(0))

    # print("Stage 3: OCR2: ", results2)

    #Removes duplicate elements which are substring of longer strings
    new_lst1 = []
    for i in range(len(results1)):
        is_replicating = False
        for j in range(len(results1)):
            if i != j:
                if results1[i] in results1[j]:
                    is_replicating = True
                    break
        if not is_replicating:
            new_lst1.append(results1[i])

    new_lst1 = self.merge_block_letter_words(new_lst1)

    new_lst2 = []
    for i in range(len(results2)):
        is_replicating = False
        for j in range(len(results2)):
            if i != j:
                if results2[i] in results2[j]:
                    is_replicating = True
                    break
        if not is_replicating:
            new_lst2.append(results2[i])

    # print("Stage 4: OCR2: ", new_lst2)

    lst, expDate = self.remove_oldest_and_futurest_dates(new_lst2)

    regex_patterns_final = [
        r'B\d{6,7}',  # Matches B followed by 7 digits
        r'\d{9}',  # Matches 9 digits followed by V
        r'\d{12}',
        r'\b[A-Z]+\b',
        r'B\d{6,7}D',  # Matches B followed by 7 digits

    ]

    regex_patterns_final2 = [
        r'\b[A-Z]+\b',
        r'\d{2}\.\d{2}\.\d{4}',  # Matches date in format DD.MM.YYYY
    ]

    labeled_data = []

    for item in new_lst1:
      if re.search(regex_patterns_final[0], item):
        n_item = "License No: " + item
        labeled_data.append(n_item)

      elif re.search(regex_patterns_final[4], item):
        n_item = "License No: " + item
        labeled_data.append(n_item)  

      elif re.search(regex_patterns_final[2], item):
        n_item = "NIC: " + item 
        labeled_data.append(n_item)

      elif re.search(regex_patterns_final[1], item):
        n_item = "NIC: " + item
        labeled_data.append(n_item)

      elif re.search(regex_patterns_final[3], item):
        n_item = "Name: " + item
        labeled_data.append(n_item)


    # print("Stage05: OCR2: ", lst)

    for item in lst:
      if re.search(regex_patterns_final2[0], item):
        n_item = "Address: " + item
        labeled_data.append(n_item)

      elif re.search(regex_patterns_final2[1], item):
        n_item = "Issue Date: " + item
        labeled_data.append(n_item)

    final = self.merge_address_values(labeled_data)

    License_Data_dict = {}
    for item in final:
      key_value_pair = item.split(": ")
      License_Data_dict[key_value_pair[0]] = key_value_pair[1]
      License_Data_dict = {key: value.strip() for key, value in License_Data_dict.items()}


    if 'Issue Date' in License_Data_dict:
      issue_date_str = License_Data_dict['Issue Date']
      issue_date = datetime.strptime(issue_date_str, '%d.%m.%Y')
      formatted_issue_date = issue_date.strftime('%Y/%m/%d')
      License_Data_dict['Issue Date'] = formatted_issue_date

    if expDate:
      if not isinstance(expDate, str):
          exp_date_str = expDate.strftime('%d.%m.%Y')
      else:
          exp_date_str = expDate

      exp_date = datetime.strptime(exp_date_str, '%d.%m.%Y')
      formatted_exp_date = exp_date.strftime('%Y/%m/%d')
      License_Data_dict['Expiry_Date'] = formatted_exp_date

      if "Name" in License_Data_dict:
        name = License_Data_dict["Name"]
        modified_name = ' '.join([word for word in name.split() if not word.islower()])
        modified_name = ' '.join([word for word in name.split() if len(word) > 3])
        License_Data_dict["Name"] = modified_name

      if "NIC" in License_Data_dict:
        nic = License_Data_dict["NIC"]
        License_Data_dict["NIC"] = nic.replace("v", "V").replace(" ", "")


      if "Name" in License_Data_dict:
            name = License_Data_dict["Name"]
            name_parts = name.split(" ")
            # print("Names Length: ", len(name_parts))
            if len(name_parts) == 1:
                License_Data_dict["familyName"] = name_parts[0]
                License_Data_dict["firstName"] = name_parts[0]
                License_Data_dict["middleName"] = None
                License_Data_dict["lastName"] = name_parts[0]        

            if len(name_parts) == 2:
                License_Data_dict["familyName"] = name_parts[1]
                License_Data_dict["firstName"] = name_parts[0]
                License_Data_dict["middleName"] = None
                License_Data_dict["lastName"] = name_parts[1]

            if len(name_parts) == 3:
                License_Data_dict["familyName"] = name_parts[2]
                License_Data_dict["firstName"] = name_parts[0]
                License_Data_dict["middleName"] = name_parts[1]
                License_Data_dict["lastName"] = name_parts[2]

            if len(name_parts) > 3:
                License_Data_dict["familyName"] = name_parts[0]
                License_Data_dict["firstName"] = name_parts[1]
                License_Data_dict["middleName"] = name_parts[2]
                License_Data_dict["lastName"] = ' '.join(name_parts[3:])

      if "Name" in License_Data_dict:
        initials = []
        name = License_Data_dict["Name"]
        name_parts = name.split(" ")
        initials_name_part = name_parts[:-1]

        for name_part in initials_name_part:
          if name_part:
              initials.append(name_part[0])
        
        last_name = name_parts[-1]  
        nameInitials = '.'.join(initials) + '.'+ last_name
        License_Data_dict["nameInitials"] = nameInitials
       
    # print("License_Data_dict", License_Data_dict)
    License = json.dumps(License_Data_dict, indent= 4)

    
    return (License)

  def getDL_OCR(self):
    self.ocrText()
    output = self.cleaningText()
    return(output)
  
  def process_file(self):
    #img = cv2.imread(file_path)  # Read the uploaded image using OpenCV
    result = self.getDL_OCR()
    return {
            'Details': result,
            'Extraction': True
        }