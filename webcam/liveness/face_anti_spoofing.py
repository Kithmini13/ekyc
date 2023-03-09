import random 
import cv2
import imutils
from . import f_liveness_detection
from . import questions
# import f_liveness_detection
# import questions

class Liveness(object):
    def __init__(self):
        print('################ init #################')
        # parameters 
        self.cam = None
        self.COUNTER, self.TOTAL = 0,0
        self.counter_ok_questions = 0
        self.counter_ok_consecutives = 0
        self.limit_consecutives = 3
        self.limit_questions = 6
        self.counter_try = 0
        self.limit_try = 50 


    def show_image(self,cam,text,color = (0,0,255)):
        # print('###### show_image ####:',cam.read())
        ret, im = cam.read()
        im = imutils.resize(im, width=720)
        #im = cv2.flip(im, 1)
        cv2.putText(im,text,(10,50),cv2.FONT_HERSHEY_COMPLEX,1,color,2)
        return im

    def process_video(self):
        print("####### Call process_video(self) 1")
        self.cam = cv2.VideoCapture(0)
        print("####### Call process_video(self) 2")
        # instanciar camara
        cv2.namedWindow('liveness_detection')

        for i_questions in range(0,self.limit_questions):
            # genero aleatoriamente pregunta
            index_question = random.randint(0,5)
            question = questions.question_bank(index_question)
            # print('###### 1 ####:',self.cam.read())
            im = self.show_image(self.cam,question)
            cv2.imshow('liveness_detection',im)
            if cv2.waitKey(1) &0xFF == ord('q'):
                break 

            for i_try in range(self.limit_try):
                # <----------------------- ingestar data 
                ret, im = self.cam.read()
                im = imutils.resize(im, width=720)
                im = cv2.flip(im, 1)
                # <----------------------- ingestar data 
                TOTAL_0 = self.TOTAL
                out_model = f_liveness_detection.detect_liveness(im,self.COUNTER,TOTAL_0)
                TOTAL = out_model['total_blinks']
                COUNTER = out_model['count_blinks_consecutives']
                dif_blink = TOTAL-TOTAL_0
                if dif_blink > 0:
                    blinks_up = 1
                else:
                    blinks_up = 0

                challenge_res = questions.challenge_result(question, out_model,blinks_up)
                # print('###### 2 ####:',self.cam.read())
                im = self.show_image(self.cam,question)
                cv2.imshow('liveness_detection',im)
                if cv2.waitKey(1) &0xFF == ord('q'):
                    break 

                if challenge_res == "pass":
                    # print('###### 3 ####:',self.cam.read())
                    im = self.show_image(self.cam,question+" : ok")
                    cv2.imshow('liveness_detection',im)
                    if cv2.waitKey(1) &0xFF == ord('q'):
                        break

                    self.counter_ok_consecutives += 1
                    if self.counter_ok_consecutives == self.limit_consecutives:
                        self.counter_ok_questions += 1
                        self.counter_try = 0
                        self.counter_ok_consecutives = 0
                        break
                    else:
                        continue

                elif challenge_res == "fail":
                    self.counter_try += 1
                    # print('###### 4 ####:',self.cam.read())
                    self.show_image(self.cam,question+" : fail")
                elif i_try == self.limit_try-1:
                    break
                    

            if self.counter_ok_questions ==  self.limit_questions:
                while True:
                    # print('###### 5 ####:',self.cam.read())
                    im = self.show_image(self.cam,"LIFENESS SUCCESSFUL",color = (0,255,0))
                    cv2.imshow('liveness_detection',im)
                    if cv2.waitKey(1) &0xFF == ord('q'):
                        break
            elif i_try == self.limit_try-1:
                while True:
                    # print('###### 6 ####:',self.cam.read())
                    im = self.show_image(self.cam,"LIFENESS FAIL")
                    cv2.imshow('liveness_detection',im)
                    if cv2.waitKey(1) &0xFF == ord('q'):
                        break
                break 

            else:
                continue


# if __name__=="__main__":
#     l = Liveness()
#     l.process_video()