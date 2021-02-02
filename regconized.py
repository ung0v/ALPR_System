import cv2
import pyodbc 
from PyQt5 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from design import Ui_MainWindow
import queue
import sys
import time
import threading
import csv
import os
import datetime
from class_CNN import NeuralNetwork
from class_PlateDetection import PlateDetector
from utils.average_plate import *
from utils.find_best_quality_images import get_best_images
from test2 import ApplicationWindow
from PIL import Image

########### INIT ###########
# Initialize the plate detector
plateDetector = PlateDetector(type_of_plate='RECT_PLATE',
                                        minPlateArea=4100,
                                        maxPlateArea=15000)

# Initialize the Neural Network
myNetwork = NeuralNetwork(modelFile="model/binary_128_0.50_ver3.pb",
                            labelFile="model/binary_128_0.50_labels_ver2.txt")

list_char_on_plate = [] # contains an array of the segmented characters in each frame
countPlates = 0 # count the number of same plates
recog_plate = ''
coordinates = (0, 0)
num_frame_without_plates = 0
countPlates_threshold = 11 # the maximum number of images of the same plate to get
###########################
server = 'DESKTOP-RM7E647\SQLEXPRESS' 
database = 'nhandien' 
username = 'sa' 
password = '1' 
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

app = QtWidgets.QApplication(sys.argv)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self,text, img, img2):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.text = text
        self.img = img
        self.img2 = img2
        self.ui.label_28.setText(QCoreApplication.translate("MainWindow", text, None))
        self.ui.label_3.setPixmap(QtGui.QPixmap(img))
        self.ui.label_6.setPixmap(QtGui.QPixmap(img2))
def insertDB(img1, img2, plate):
    # Some other example server values are
    # server = 'localhost\sqlexpress' # for a named instance
    # server = 'myserver,port' # to specify an alternate port
    date = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    cursor = cnxn.cursor()
    m3 = """
    INSERT INTO bienso (Image, Image2, LicensePlate, CreatedDate) 
    VALUES ('%s', '%s', '%s', '%s')""" %(img1, img2, plate, date)
    print(m3)
    cursor.execute("""
    INSERT INTO bienso (Image, Image2, LicensePlate, CreatedDate) 
    VALUES ('%s', '%s', '%s', '%s')""" %(img1, img2, plate, date))  
    cnxn.commit()
    

def recognized_plate(list_char_on_plate, size,res=[]):
    """
    input is a list that contains a images of the same plate
    get the best images in the list
    calculates the average plate
    """
    global recog_plate

    t0 = time.time()
    plates_value = []
    plates_length = []

    list_char_on_plate = get_best_images(list_char_on_plate, num_img_return=7) # get the best images

    for segmented_characters in list_char_on_plate:
        plate, len_plate = myNetwork.label_image_list(segmented_characters[1], size)
        plates_value.append(plate)
        plates_length.append(len_plate)
        
    final_plate = get_average_plate_value(plates_value, plates_length) # calculates the average plate
    if len(final_plate) > 7:
        if (final_plate[2] == '8'):
            final_plate = final_plate[:2] + 'B' + final_plate[3:]
        elif (final_plate[2] == '0'):
            final_plate = final_plate[:2] + 'D' + final_plate[3:]
    recog_plate = final_plate
    # current_time = datetime.datetime.now()
    # myplate = [{'Plate': final_plate, 'Event Time': current_time}]
    # filename = "recognized_plate.csv"
    # fields = ['Plate', 'Event Time']
    # # writing to csv file  
    # with open(filename, 'w') as csvfile:  
    #     # creating a csv dict writer object  
    #     writer = csv.writer(csvfile, fieldnames = fields)  
            
    #     # # writing headers (field names)  
    #     # writer.writeheader()

    #     # writing the fields  
    #     csvwriter.writerow(fields)     
    #     # writing data rows  
    # writer.writerows(myplate)
    print("recognized plate: " + final_plate)
    print("threading time: " + str(time.time() - t0))
    res.append(final_plate)
    # For IP CAMERA: rtsp://admin:Admin@123456@100.0.0.40/Streaming/Channels/101
    # For Laptop Camera: 0
cap = cv2.VideoCapture(0) # video path
img1_link = []
img2_link = [] 
if __name__=="__main__":
    while(cap.isOpened):
        ret, frame = cap.read()
        if (frame is None):
            print("[INFO] End of Video")
            break

        _frame = cv2.resize(frame, (960, 540)) # resize the frame to fit the screen
        frame_height, frame_width = frame.shape[:2]
        _frame_height, _frame_width = _frame.shape[:2]
        cropped_frame = frame[int(frame_height*0.3):frame_height, 0:int(frame_width*0.8)] # crop the ROI
        cv2.rectangle(_frame, (0, int(_frame_height*0.01)), (int(_frame_width*1), _frame_height), (255, 0, 0), 2) # draw a
        # rectangle to locate the ROI

        # print the result
        cv2.rectangle(_frame, (0, 0), (190, 40), (0, 0, 0), -1)
        cv2.putText(_frame, recog_plate, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        # out.write(_frame)
        # window=Tk()
        # window.title('Nhận diện biển số')
        # window.geometry("960x540+10+10")
        # window.mainloop()
        
        cv2.imshow('video', _frame)

        possible_plates = plateDetector.find_possible_plates(cropped_frame)
        # cv2.imshow('morphed', plateDetector.after_preprocess)
        if possible_plates is not None:
            num_frame_without_plates = 0
            distance = tracking(coordinates, plateDetector.corresponding_area[0]) # calculates the distance between two plates
            coordinates = plateDetector.corresponding_area[0] # get the coordinate of the detected plate
            if (distance < 100):
                if(countPlates < countPlates_threshold):
                    cv2.imshow('Plate', possible_plates[0])
                    im = Image.fromarray(possible_plates[0])
                    image = cap.read()
                    
                    # img.save('image.png')
                    im.save("regconized%d.png" % countPlates)  
                    cv2.imwrite("frame%d.jpg" % countPlates, image[1])
                    img1_link.append(os.getcwd() + '\\' +  "regconized%d.png" % countPlates)
                    img2_link.append(os.getcwd() + '\\' +  "frame%d.jpg" % countPlates)
                    temp = []
                    temp.append(possible_plates[0])
                    temp.append(plateDetector.char_on_plate[0]) # temp = [image of plate, segmented characters on plate]
                    
                    list_char_on_plate.append(temp)
                    countPlates += 1
                elif(countPlates == countPlates_threshold):
                    # create a new thread for image recognition
                    q = queue.Queue()
                    res = []
                    t = threading.Thread(target=recognized_plate, args=(list_char_on_plate, 128,res))
                    t.start()
                    t.join()
                    link1 = ('|').join(img1_link)
                    link2 = ('|').join(img2_link)
                    insertDB(link1, link2, res[0])
                    application = ApplicationWindow(text=res[0], img = img1_link[10], img2 = img2_link[10])
                    application.show()
                    # sys.exit(app.exec_())
                    countPlates += 1
            else:
                countPlates = 0
                list_char_on_plate = []

        # the program will try to catch 11 images of the same plate and then pick the top 7 best
        # quality images out of 11. However, if the program cannot catch enough images, after
        # num_frame_without_plates frames without plates, it will process the and calculate the
        # final plate
        if (possible_plates == None):
            num_frame_without_plates += 1
            if (countPlates <= countPlates_threshold and countPlates > 0 and num_frame_without_plates > 5):
                threading.Thread(target=recognized_plate, args=(list_char_on_plate, 128)).start()
                countPlates = 0

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
    cap.release()
    cv2.destroyAllWindows()
