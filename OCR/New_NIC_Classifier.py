import pytesseract
import cv2

class NewNICClassify:
    def __init__(self, image1):
        self.img1 = image1
        self.output4 = "New_NIC_Front"
        self.output5 = "New_NIC_Back"

    def grayScale(self):
        self.gray1 = cv2.cvtColor(self.img1, cv2.COLOR_BGR2GRAY)

    def OCR(self):
        self.text = pytesseract.image_to_string(self.gray1)

    def findClass(self):
        if "IDENTITY" in self.text or "CARD" in self.text or "NATIONAL" in self.text or "SRI LANKA" in self.text or "Name" in self.text or "Date of Birth" in self.text or "Holder" in self.text or "Signature" in self.text:
            return self.output4

        elif "Address" in self.text or "Registration of Persons" in self.text or "Act" in self.text or "32 of 1968" in self.text or "Date of Issue" in self.text or "Registration" in self.text or "Commissioner" in self.text:
            return self.output5

    def classify(self):
        self.grayScale()
        self.OCR()
        output = self.findClass()
        return output

    def process_file(self):
        #img = cv2.imread(file_path)  # Read the uploaded image using OpenCV
        result = self.classify()

        return {
            'file_type': result,
            'classification': True
        }