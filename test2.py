from PyQt5 import QtWidgets
from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from design import Ui_Form
import sys

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, text):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.text = text
        self.ui.label_28.setText(QCoreApplication.translate("MainWindow", self.text, None))


def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()