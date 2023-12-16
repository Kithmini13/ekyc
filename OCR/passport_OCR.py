import cv2
import pytesseract
import re
from datetime import datetime, timedelta
import json

class OCRPassportscan:
  def __init__(self,image):
    self.img = image

  def getROI(self):
    # Get the dimensions of the image
    height, width = self.img.shape[:2]

    # Calculate the coordinates for the ROI
    roi_start_y = int(height * 3 / 4)
    roi_end_y = height

    # Crop the image to the ROI
    self.roiB = self.img[roi_start_y:roi_end_y, :]


  def preprocess(self):
    self.grayB = cv2.cvtColor(self.roiB, cv2.COLOR_BGR2GRAY)
    hsv_image = cv2.cvtColor(self.roiB, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    average_brightness = cv2.mean(v)[0]
    self.grayB[self.grayB < average_brightness - 44] = 0

  def ocrExtract(self):
    custom_config = r'--oem 3 --psm 6 '
    self.ocr = pytesseract.image_to_string(self.grayB)
    self.ocr = self.ocr.replace(" ", "")
    self.extractIssueDate()

  def extractIssueDate(self):
    img = cv2.resize(self.img, (3000, 2024))
    # Get the dimensions of the image
    height, width =  img.shape[:2]

    # Calculate the coordinates for cropping
    crop_start_y = int(height * 5/9)
    crop_end_y = int(height * 6/9)
    crop_start_x = int(width * 1/4)
    crop_end_x = int(width * 2/4)

    # Crop the image
    cropped_image = img[crop_start_y:crop_end_y, crop_start_x:crop_end_x]
    roi = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    roi[roi < 110] = 0
    Issue_Date = pytesseract.image_to_string(roi, config='-c tessedit_char_whitelist=0123456789/\-')
    return Issue_Date

  def extractInfo(self):
    init_patterns = [
      r'[A-Z]\d{7,8}',  # Matches D followed by 7 digits
      r'\d{9}\s*[vV]',   # Matches 9 digits followed by V
      r'(19\d{10}|2\d{11})+(?=<)'
    ]

    init_results = []
    for i in range(len(init_patterns)):
      match = re.search(init_patterns[i], self.ocr)
      if match:
        init_results.append(match.group(0))

    matching_elements = [elem for elem in init_results if re.match(r'\d{9}\s*[vV]', elem)]

    # Remove matching elements if they exist
    if matching_elements:
        init_results = [elem for elem in init_results if not re.match(r'(19\d{10}|2\d{11})+(?=<)', elem)]

    match = re.search(r'(M|F)([0-9]\d{5})', self.ocr)
    if match:
        extracted_pattern = match.group(2)
    else:
        extracted_pattern = ""

    # Convert to date format "33/04/26"
    date = extracted_pattern[:2] + "/" + extracted_pattern[2:4] + "/" + extracted_pattern[4:]
    init_results.append(date)


    # Extract words using regular expression
    words = re.findall(r'[A-Z]{2,}', self.ocr)

    # Join the words into a single string
    word_string = ' '.join(words)
    name = word_string.replace("PELKA", "").replace("PBLKA", "").replace("LKA", "").replace("TEIC", "").replace("DISTR", "").replace("ORDTSONOROECDOEASCTE", "").replace("NONIC", "")
    name = name.strip()
    init_results.append(name)
    if '//' in init_results:
      init_results.remove('//')
    self.extracted = init_results

  def createJson(self):
    labeling_patterns = [
      r'[A-Z]\d{7,8}',  # Matches D followed by 7 digits
      r'\d{9}\s*[vV]',   # Matches 9 digits followed by V
      r'(19\d{10}|2\d{11})',
      r'\d{2}\/\d{2}\/\d{2}',  # Matches date in format DD.MM. YYYY

    ]

    labeled_data = []
    for item in self.extracted:

      if re.search(labeling_patterns[0], item):
        n_item = "PassportNo: " + item
        labeled_data.append(n_item)

      elif re.search(labeling_patterns[1], item):
        n_item = "NIC: " + item
        labeled_data.append(n_item)

      elif re.search(labeling_patterns[2], item):
        n_item = "NIC: " + item
        labeled_data.append(n_item)

      elif re.search(labeling_patterns[3], item):
        n_item = "ExpiryDate: " + item
        labeled_data.append(n_item)

      else:
        n_item = "Name: " + item
        labeled_data.append(n_item)


    for i in range(len(labeled_data)):
      if labeled_data[i].startswith('Name:'):
          labeled_data[i] = labeled_data[i].replace('KA', '')
      Passport_Data_dict = {}

    for item in labeled_data:
        key_value_pair = item.split(": ")
        Passport_Data_dict[key_value_pair[0]] = key_value_pair[1]


    img = cv2.resize(self.img, (3000, 2024))
    # Get the dimensions of the image
    height, width =  img.shape[:2]

    # Calculate the coordinates for cropping
    crop_start_y = int(height * 1/9)
    crop_end_y = int(height * 3/13)
    crop_start_x = int(width * 1/4)
    crop_end_x = int(width * 3/4)

    # Crop the image
    cropped_image = img[crop_start_y:crop_end_y, crop_start_x:crop_end_x]
    # cv2.imshow('Image', cropped_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    cleaned = []
    roi = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('Image', roi)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    Name_counts = pytesseract.image_to_string(roi, config='--oem 3 --psm 6')
    name_c = Name_counts.split("\n")
    cleaned = []  # Initialize the cleaned list
    for element in name_c:
        if "PB" in element or "LKA" in element or "PB LKA" in element or "AND" in element or "TARA" in element or "RVA" in element:
            continue  # Skip elements containing any of the specified keywords
        cleaned.append(element)
          
    pattern = re.compile(r'\b[A-Z\s]{4,}\b')

    # List to store the selected block letter parts
    selected_parts = []

    for element in cleaned:
        # Find all matches in the current element
        matches = pattern.findall(element)
        
        # Extend the selected_parts list with the matches
        selected_parts.extend(matches)

    # Print the selected block letter parts
    filtered_words = [word for word in selected_parts if len(word.strip()) > 3]
    if len(filtered_words) > 0:
      selected_parts_1 = filtered_words[0].split(" ")
      filtered_list_22 = [item for item in selected_parts_1 if item.strip() != '']
      surname_count = len(filtered_list_22)

    else:
       surname_count = 0

    if 'Name' in Passport_Data_dict and surname_count > 0:
      # Extract the original name
      name_str = Passport_Data_dict['Name']

      # Split the name into individual parts
      name_parts = name_str.split()

      # Move the first name to the end
      rearranged_name_parts = name_parts[surname_count:] + name_parts[:surname_count]

      # Join the rearranged name parts back together
      rearranged_name = ' '.join(rearranged_name_parts)

      # Update the dictionary with the rearranged name
      Passport_Data_dict['Name'] = rearranged_name

    else:
      # Extract the original name
      name_str = Passport_Data_dict['Name']

      # Split the name into individual parts
      name_parts = name_str.split()

      # Move the first name to the end
      rearranged_name_parts = name_parts[1:] + [name_parts[0]]

      # Join the rearranged name parts back together
      rearranged_name = ' '.join(rearranged_name_parts)

      # Update the dictionary with the rearranged name
      Passport_Data_dict['Name'] = rearranged_name
       



    if 'ExpiryDate' in Passport_Data_dict:
      # Extract the original expiry date
      expiry_date_str = Passport_Data_dict['ExpiryDate']

      # Split the expiry date into day, month, and year components
      year, month, day = expiry_date_str.split('/')

      # Determine the full year by assuming it belongs to the 21st century
      full_year = '20' + year

      # Format the expiry date in the desired format
      formatted_expiry_date = f"{full_year}/{month}/{day}"

      # Update the dictionary with the formatted expiry date
      Passport_Data_dict['ExpiryDate'] = formatted_expiry_date

      issued = self.extractIssueDate()
      match = re.search(r'\d{2}\/\d{2}\/\d{4}', issued)
      if match:
          date_part = match.group(0)
          day, month, year = date_part.split('/')
          formatted_date = f"{year}/{month}/{day}"
          Passport_Data_dict['IssueDate'] = formatted_date
      else:
          Passport_Data_dict['IssueDate'] = None


      if 'IssueDate' not in Passport_Data_dict or Passport_Data_dict['IssueDate'] is None:
          # Split the expiry date by '/'
          expiry_parts = formatted_expiry_date.split('/')

          # Extract the year from the expiry date
          expiry_year = int(expiry_parts[0])

          # Calculate the issue year as 10 years before the expiry year
          issue_year = expiry_year - 10

          # Reconstruct the issue date with the same day and month as the expiry date
          issue_date_str = f"{issue_year}/{expiry_parts[1]}/{expiry_parts[2]}"

          # Add the 'IssueDate' key with the formatted issue date to the dictionary
          Passport_Data_dict['IssueDate'] = issue_date_str

    name = Passport_Data_dict["Name"]
    modified_name = ' '.join([word for word in name.split() if not word.islower()])
    modified_name = ' '.join([word for word in name.split() if len(word) > 2])
    Passport_Data_dict["Name"] = modified_name

    if "NIC" in Passport_Data_dict:
      nic = Passport_Data_dict["NIC"]
    #  License_Data_dict["NIC"] = nic.replace(" ", "")
      Passport_Data_dict["NIC"] = nic.replace("v", "V").replace(" ", "")

    if "Name" in Passport_Data_dict:
      array = []
      name = Passport_Data_dict["Name"]
      word_array = name.split()

      for word in word_array:
          if "A" in  word or "E" in word or "I" in word or "O" in word or "U" in word:
             array.append(word)
      concatenated_string = ' '.join(array)
      Passport_Data_dict["Name"] = concatenated_string

    if "Name" in Passport_Data_dict:
            name = Passport_Data_dict["Name"]
            name_parts = name.split(" ")
            print("Names Length: ", len(name_parts))
            if len(name_parts) == 1:
                Passport_Data_dict["familyName"] = name_parts[0]
                Passport_Data_dict["firstName"] = name_parts[0]
                Passport_Data_dict["middleName"] = None
                Passport_Data_dict["lastName"] = name_parts[0]        

            if len(name_parts) == 2:
                Passport_Data_dict["familyName"] = name_parts[1]
                Passport_Data_dict["firstName"] = name_parts[0]
                Passport_Data_dict["middleName"] = None
                Passport_Data_dict["lastName"] = name_parts[1]

            if len(name_parts) == 3:
                Passport_Data_dict["familyName"] = name_parts[2]
                Passport_Data_dict["firstName"] = name_parts[0]
                Passport_Data_dict["middleName"] = name_parts[1]
                Passport_Data_dict["lastName"] = name_parts[2]

            if len(name_parts) > 3:
                Passport_Data_dict["familyName"] = ' '.join(name_parts[-2:])
                Passport_Data_dict["firstName"] = name_parts[0]
                Passport_Data_dict["middleName"] = ' '.join(name_parts[1:-2])
                Passport_Data_dict["lastName"] = ' '.join(name_parts[-2:])

    if "Name" in Passport_Data_dict:
        initials = []
        name = Passport_Data_dict["Name"]
        name_parts = name.split(" ")
        initials_name_part = name_parts[:-1]

        for name_part in initials_name_part:
          if name_part:
              initials.append(name_part[0])
       
        last_name = name_parts[-1] 
        nameInitials = '.'.join(initials) + '.' + last_name
        Passport_Data_dict["nameInitials"] = nameInitials
       

    Passport = json.dumps(Passport_Data_dict)
    return (Passport)

  def getPassport_OCR(self):
    self.getROI()
    self.preprocess()
    self.ocrExtract()
    self.extractInfo()
    output = self.createJson()
    return(output)

  def process_file(self):
    result = self.getPassport_OCR()
    return {
            'Details': result,
            'Extraction': True
        }





