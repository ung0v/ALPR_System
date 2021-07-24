import cv2
import pyodbc 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt,QObject, QThread, pyqtSignal
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt, QThread)
from design import Ui_Form
from cam_ui import Ui_MainWindow

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
from configparser import ConfigParser
import serial
import serial.tools.list_ports
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
dataLicensePlate = []

config_object = ConfigParser()
config_object.read("config/config.ini")
dbinfo = config_object["DATABASECONFIG"]
server = dbinfo['server']
database = dbinfo['database']
username = dbinfo['username']
password = dbinfo['password']
stringSql = 'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
print(stringSql)
cnxn = pyodbc.connect(stringSql)
# cnxn = pyodbc.connect(r'Driver=SQL Server;Server=.\SQLEXPRESS;Database=myDB;Trusted_Connection=yes;')
app = QtWidgets.QApplication(sys.argv)
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    def run(self, ser):
        while 1:            
            arduinoData = ser.readline().decode('ascii')
            print(arduinoData)

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self,text, img, img2):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.text = text
        self.img = img
        self.img2 = img2
        self.ui.label_28.setText(QCoreApplication.translate("MainWindow", text, None))
        self.ui.label_3.setPixmap(QtGui.QPixmap(img))
        self.ui.label_6.setPixmap(QtGui.QPixmap(img2))
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

        # change name of header columns
        self.header_labels = ['Ảnh', 'Biển số', 'Thời gian']
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)
        
    def data(self, index, role):
        if role == Qt.DisplayRole and index.column() != 0:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

        # convert data to image
        if role == Qt.DecorationRole:
                # imageLabel = QtWidgets.QLabel()
                # imageLabel.setText("")
                # imageLabel.setPixmap(QtGui.QPixmap(self._data[index.row()][index.column()]))
                value = self._data[index.row()][index.column()]
                return QtGui.QPixmap(value)
            
    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
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
def getPlate():
    cursor = cnxn.cursor()    
    try:
        cursor.execute("SELECT * FROM bienso order by ID desc")
    except:
        cursor.execute("CREATE TABLE bienso(ID int not null primary key identity(1,1),Image ntext,Image2 ntext,LicensePlate varchar(50),CreatedDate datetime)")
        return [['1','1',datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")]]
    rows = cursor.fetchall()
    dataPlate = []
    for row in rows:
        data = []
        image = row[1].split("|")
        data.append(image[len(image) - 1])
        data.append(row[3])
        data.append(row[4].strftime("%m/%d/%Y %H:%M:%S"))
        dataPlate.append(data)
    return dataPlate
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
def getCOMPORTS():
    ports = serial.tools.list_ports.comports()
    lstCOMPORTS = []
    for port, desc, hwid in sorted(ports):
        lstCOMPORTS.append(port)
    return lstCOMPORTS
class video (QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()                  

#        uic.loadUi('test2.ui',self)                           # ---
        self.setupUi(self)                                     # +++

        self.btnStart.clicked.connect(self.start_webcam)
        self.btnExit.clicked.connect(self.exit_app)
        self.btnStop.clicked.connect(self.stop_cap)
        self.btnOpen.clicked.connect(self.OpenCOMPORT)
        # adding list of items to combo box 
        self.comboBox.addItems(getCOMPORTS()) 

        # adding resource to table
        self.model = TableModel(getPlate())
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableView.resizeColumnsToContents()
        
        self.image_label_2.setScaledContents(True)

        self.cap = None                                        #  -capture <-> +cap

        self.timer = QtCore.QTimer(self, interval=5)
        self.timer.timeout.connect(self.update_frame)
        self._image_counter = 0

    @QtCore.pyqtSlot()
    def start_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 359)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  749)
        self.timer.start()
    @QtCore.pyqtSlot()
    def update_frame(self):
        global num_frame_without_plates
        global countPlates
        global list_char_on_plate
        global coordinates
        ret, frame = self.cap.read()
        while(self.cap.isOpened):
            self.displayImage(frame, True)
            ret, frame = cap.read()
            if (frame is None):
                print("[INFO] End of Video")
                break

            # _frame = cv2.resize(frame, (960, 540)) # resize the frame to fit the screen
            frame_height, frame_width = frame.shape[:2]
            # _frame_height, _frame_width = _frame.shape[:2]
            _frame_height, _frame_width = frame.shape[:2]
            cropped_frame = frame[int(frame_height*0.3):frame_height, 0:int(frame_width*0.8)] # crop the ROI
            # cv2.rectangle(_frame, (0, int(_frame_height*0.01)), (int(_frame_width*1), _frame_height), (255, 0, 0), 2) # draw a
            cv2.rectangle(frame, (0, int(_frame_height*0.01)), (int(_frame_width*1), _frame_height), (255, 0, 0), 2) # draw a
            # rectangle to locate the ROI

            # print the result
            # cv2.rectangle(_frame, (0, 0), (190, 40), (0, 0, 0), -1)
            cv2.rectangle(frame, (0, 0), (190, 40), (0, 0, 0), -1)
            # cv2.putText(_frame, recog_plate, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, recog_plate, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            # out.write(_frame)
            # window=Tk()
            # window.title('Nhận diện biển số')
            # window.geometry("960x540+10+10")
            # window.mainloop()
            
            # cv2.imshow('video', _frame)

            possible_plates = plateDetector.find_possible_plates(cropped_frame)
            # cv2.imshow('morphed', plateDetector.after_preprocess)
            if possible_plates is not None:
                num_frame_without_plates = 0
                distance = tracking(coordinates, plateDetector.corresponding_area[0]) # calculates the distance between two plates
                coordinates = plateDetector.corresponding_area[0] # get the coordinate of the detected plate
                if (distance < 100):
                    if(countPlates < countPlates_threshold):
                        # cv2.imshow('Plate', possible_plates[0])
                        im = Image.fromarray(possible_plates[0])
                        image = cap.read()
                        
                        # img.save('image.png')
                        
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
                        directory = "Regcognized_Plates"
                        plate = res[0]
                        path = os.getcwd() + '\\' +  directory + "\\"
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        if not os.path.exists(path + plate):
                            os.makedirs(path + plate)
                        img1_link = (path + plate + "\\"+ "regconized%d.png" % countPlates)
                        img2_link = (path + plate + "\\" + "frame%d.jpg" % countPlates)
                        im.save(img1_link)  
                        cv2.imwrite(img2_link, image[1])
                        insertDB(img1_link, img2_link, plate)
                        self.model = TableModel(getPlate())
                        self.tableView.setModel(self.model)
                        application = ApplicationWindow(text=plate, img = img1_link, img2 = img2_link)
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

    # @QtCore.pyqtSlot()
    # def capture_image(self):
    #     flag, frame = self.cap.read()
    #     path = r'C:\Users\ung0v\Desktop'                         # 
    #     if flag:
    #         QtWidgets.QApplication.beep()
    #         name = "my_image.jpg"
    #         cv2.imwrite(os.path.join(path, name), frame)
    #         self._image_counter += 1

    def displayImage(self, img, window=True):
        qformat = QtGui.QImage.Format_Indexed8
        if len(img.shape)==3 :
            if img.shape[2]==4:
                qformat = QtGui.QImage.Format_RGBA8888
            else:
                qformat = QtGui.QImage.Format_RGB888
        outImage = QtGui.QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        if window:
            self.image_label_2.setPixmap(QtGui.QPixmap.fromImage(outImage))

    def OpenCOMPORT(self):
        currentCOMPORT = self.getCOMPORT_isSelected()
        ser = serial.Serial(currentCOMPORT, baudrate=9600, timeout=1)
        ser.write(b'gggggg')
         # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run(ser))
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()
        self.btnOpen.setEnabled(False)
            
    def UpdateValues(self, text):
        self.textEdit.append(text)

    def getCOMPORT_isSelected(self):
        currentValue = self.comboBox.currentText()
        return currentValue
    
    @QtCore.pyqtSlot()
    def exit_app(self):
        sys.exit(app.exit())

    @QtCore.pyqtSlot()
    def stop_cap(self):
        self.cap.release()
        self.cv2.destroyAllWindows()

cap = cv2.VideoCapture(0) # video path
img1_link = []
img2_link = [] 
if __name__=="__main__":
    window = video()
    window.start_webcam
    window.setWindowTitle('main code')
    window.show()
    sys.exit(app.exec_())
    
