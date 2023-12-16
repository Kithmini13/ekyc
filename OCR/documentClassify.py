import pytesseract
import cv2

class LegalDocClassify:
    def __init__(self, image):
        self.img = image
        self.output1 = "NIC"
        self.output2 = "Driving_License"
        self.output3 = "Passport"
        self.output4 = "NIC"
        self.output5 = "NIC"
        self.output6 = "Unknown_File"
        self.output7 = "Low_Qualityy"
        self.output8 = "Low_Brightness"

    def checkQuality(self):
        # Convert the image to grayscale
        # Set the blur detection threshold (adjust as needed)
        blur_threshold = 10
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        # Compute the Laplacian of the grayscale image
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)

        # Compute the variance of the Laplacian
        variance = laplacian.var()

        # Compare the variance with the threshold
        if variance < blur_threshold:
            return True  # Image is blurry
        else:
            return False  # Image is not blurry

    def grayScale(self):
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def OCR(self):
        self.text = pytesseract.image_to_string(self.gray)
        self.text2 = pytesseract.image_to_string(self.gray, config= r'--oem 3 --psm 6')



    def findClass(self):
        if "DRIVING" in self.text or "LICENSE" in self.text or "Blood" in self.text or "Group" in self.text:
            self.classified = True
            return self.output2

        elif "PASSPORT" in self.text or "Profession" in self.text or "PBLK" in self.text or "PB" in self.text or "AUTHORITY COLOMBO" in self.text:
            self.classified = True
            return self.output3

        elif "Address" in self.text or "Registration of Persons" in self.text or "Act" in self.text or "32 of 1968" in self.text or "Commissioner General" in self.text:
            self.classified = True
            return self.output5
        
        elif "IDENTITY" in self.text or "CARD" in self.text:
            self.classified = True
            return self.output4
        
        elif "1968" in self.text or "32" in self.text or "V" in self.text or "v" in self.text or "1968" in self.text2 or "32" in self.text2 or "V" in self.text2 or "v" in self.text2:
            self.classified = True
            return self.output1

        else:
            self.classified = False
            return self.output6

    def classify(self):
        self.grayScale()
        self.OCR()
        output = self.findClass()
        return output

    def process_file(self, file_path):
        self.img = cv2.imread(file_path)  # Read the uploaded image using OpenCV
        pre_result = self.classify()
        hsv_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        self.average_brightness = cv2.mean(v)[0]

        if self.average_brightness < 25:
            self.classified = pre_result
            result = self.output8

        else:
            if pre_result == "Passport" or "NIC" in pre_result:
                result = self.classify()
            
            else:
                is_blurry_image = self.checkQuality()
                if is_blurry_image:
                    self.classified = pre_result
                    result = self.output7
                else:
                    result = self.classify()

        return {
            'file_path': file_path,
            'file_type': result,
            'classification': self.classified
        }