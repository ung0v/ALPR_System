import os
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets                     # uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QLabel, QVBoxLayout)              # +++
from cam_ui import Ui_MainWindow
from PyQt5.QtCore import Qt
import pyodbc 
###########################
dataLicensePlate = []
server = 'DESKTOP-RM7E647\SQLEXPRESS' 
database = 'nhandien' 
username = 'sa' 
password = '1' 
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
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
class video (QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()                  

#        uic.loadUi('test2.ui',self)                           # ---
        self.setupUi(self)                                     # +++

        self.btnStart.clicked.connect(self.start_webcam)
        self.btnExit.clicked.connect(self.capture_image)

        self.image_label.setScaledContents(True)

        self.cap = None                                        #  -capture <-> +cap

        self.timer = QtCore.QTimer(self, interval=5)
        self.timer.timeout.connect(self.update_frame)
        self._image_counter = 0

        
        self.model = TableModel(getPlate())
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableView.resizeColumnsToContents()


    @QtCore.pyqtSlot()
    def start_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 359)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  779)
        self.timer.start()

    @QtCore.pyqtSlot()
    def update_frame(self):
        ret, image = self.cap.read()
        simage     = cv2.flip(image, 1)
        self.displayImage(image, True)

    @QtCore.pyqtSlot()
    def capture_image(self):
        flag, frame = self.cap.read()
        path = r'C:\Users\ung0v\Desktop'                         # 
        if flag:
            QtWidgets.QApplication.beep()
            name = "my_image.jpg"
            cv2.imwrite(os.path.join(path, name), frame)
            self._image_counter += 1

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
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(outImage))
def getPlate():
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM bienso")
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
if __name__=='__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = video()
    window.setWindowTitle('main code')
    window.show()
    sys.exit(app.exec_())
