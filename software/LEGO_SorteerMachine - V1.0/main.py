import sys
import os
import cv2
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtCore, QtWidgets
from main_window_ui import Ui_MainWindow
import time
from imutils.video import VideoStream
import threading
from program import main_program, stopAll
from serialcom import serialTh, update_dict, serialBoot
import serialcom
import var
import jetson.utils


#vs = VideoStream(src=0).start()
var.streamInput = jetson.utils.videoSource('/dev/video0')
time.sleep(2.0)


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionExit.triggered.connect(self.exit)
        self.actionAbout.triggered.connect(self.about)
        self.actionStart.triggered.connect(self.start)
        self.actionStop.triggered.connect(self.stop)
        self.actionSettings.triggered.connect(self.settings)
        self.actionTrays.triggered.connect(self.trays)


    def about(self):
        var.currentMode = 1
        QMessageBox.about(
            self,
            "About Sample Editor",
            "<p>A sample text editor app built with:</p>"
            "<p>- PyQt</p>"
            "<p>- Qt Designer</p>"
            "<p>- Python</p>",
        )
        
    
    def trays(self):
        print("trays")
        dialog = traysDialog(self)
        dialog.exec()

    def exit(self):
        print("exit")

        stopAll()

        #stream_th.run = False
        #stream_th.join()
        
        program_th.run = False
        program_th.join(timeout=1)
        
        self.close()
        quit()
        
    
    def start(self):
        print ("Start")
        if (var.currentMode == 3):
            var.currentMode = 5
        else:
            QMessageBox.about(
                self,
                "Kan alleen gestart worden ",
                "<p>als machine in mode Ready is.</p>"
                "<p></p>",
            )


    def stop(self):
        if (var.currentMode == 5):
            stopAll()
            var.currentMode = 3

    def settings(self):
        print ("Settings")

class traysDialog(QDialog):
    print("trays")
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/bakkjes.ui", self) #for linux
        #loadUi(os.path.dirname(__file__)+"/ui/find_replace.ui", self) #for windows



def videoStream (self):
    stream_th = threading.currentThread()
    while getattr(stream_th, "run", True):
        rotate_transform = QTransform()
        rotate_transform.rotate(180)  
        #var.newestFrame = input.Capture()
        self.images = var.newestFrame
        self.images = QtGui.QImage(self.images.data, self.images.shape[1], self.images.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.images =  self.images.scaledToWidth(700)
        self.image.setPixmap(QtGui.QPixmap.fromImage(self.images.transformed(rotate_transform)))
        time.sleep(0.1)
    
    #vs.stop()
    #vs.stream.release()
        



if __name__ == "__main__": 
    print("hallo")
    app = QApplication(sys.argv)
    win = Window()
    win.showFullScreen()
    #win.showMaximized()
    win.show()

    serialBoot()

    stream_th = threading.Thread(target=videoStream, args=(win,))
    stream_th.start()
    
    program_th = threading.Thread(target=main_program)
    program_th.start()

    #security_th = threading.Thread(target=securityTh)
    #security_th.start()

    #serial_th = threading.Thread(target=serialTh)
    #serial_th.start()

   

    time.sleep(0.05)	#Wait for a short time to ensure QApplication instance created.
    sys.exit(app.exec())
