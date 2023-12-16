import pytesseract
import cv2

class BillClassify:
    def __init__(self, image,TYPE):
        self.img = image
        self.Type = TYPE
        self.output1 = "Electricity"
        self.output2 = "Water"
        self.output3 = "Dialog"
        self.output4 = "Mobitel"
        self.output5 = "Unknown"
        self.output6 = "Low_Quality"

    def checkQuality(self):
        # Convert the image to grayscale
        # Set the blur detection threshold (adjust as needed)
        if self.Type == "IMG":
            blur_threshold = 30
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
            
        else:
            blur_threshold = 0
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

    def findClass(self):
        if "Electricity" in self.text or "Enrich" in self.text or "WPS" in self.text or "CEB" in self.text or "electricity" in self.text or "ELECTRICITY" in self.text:
            self.classified = True
            return self.output1

        elif "WATER" in self.text or "SUPPLY" in self.text or "DRAINAGE" in self.text or "N.W.S" in self.text or "D.B" in self.text or "water" in self.text or "Supply" in self.text:
            self.classified = True
            return self.output2

        elif "Dialog" in self.text or "DIalog" in self.text or "PLAN" in self.text or "Loyalty" in self.text:
            self.classified = True
            return self.output3

        elif "SLT" in self.text or "Telecom" in self.text or "PLC" in self.text or "Lotus" in self.text or "Mega" in self.text or "Lines" in self.text:
            self.classified =True
            return self.output4

        else:
            self.classified = False
            return self.output5
        


    def classify(self):
        self.grayScale()
        self.OCR()
        output = self.findClass()
        return output

    def process_file(self, file_path):
        self.img = cv2.imread(file_path)  # Read the uploaded image using OpenCV
        is_blurry_image = self.checkQuality()
        if is_blurry_image:
            self.classified = False
            result = self.output6
        else:
            result = self.classify()
        
        return {
            'file_path': file_path,
            'file_type': result,
            'classification': self.classified
        }