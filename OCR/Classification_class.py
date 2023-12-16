import cv2
import numpy as np
from keras.models import load_model

class NICSideClassification:
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        self.img = cv2.resize(self.img, (400, 400))
        self.img = np.expand_dims(self.img, axis=0)
        self.model = load_model('NIC_side_classifier_model.h5')

    def predict(self):
        predictions = self.model.predict(self.img)
        predicted_class = np.argmax(predictions[0])
        predicted_probability = np.max(predictions[0])

        label_mapping = {
            0: 'Front',
            1: 'Back',
        }

        print("predicted_probability", predicted_probability)
        if predicted_probability > 0.10:
            predicted_label = label_mapping[predicted_class]
        else:
            predicted_label = "File not recognized"

        return predicted_label
