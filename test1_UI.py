from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QMessageBox, QPushButton, QTextEdit
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5  import QtCore
from PyQt5 import Qt
from PyQt5.QtCore import QSize
from PyQt5.uic import loadUi


import sys
import os
import subprocess
import shutil
import subprocess
import time
import close_UI

folder_input_flag = []

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.ui = loadUi('test1.ui', self)
        self.setFixedSize(self.size())
        self.show()
        self.setWindowTitle('Anti-terrorist system')

        self.ui.runButton.clicked.connect(self.gen_cmd)
        self.ui.inputBrowse.clicked.connect(self.get_linkFolder)
        self.ui.outputBrowse.clicked.connect(self.get_linkFolderOutput)
        self.ui.check_realTime.clicked.connect(self.realTime)
        self.ui.btn_close_tool.clicked.connect(self.close_ui)

        global dirpath
        dirpath = os.getcwd() + '/' + 'detection_result.avi'
        folder_output = os.path.abspath(os.path.join(dirpath))
        self.output_txt.setText(folder_output)

    def gen_cmd(self):
        folder_input = self.input_txt.toPlainText()
        folder_output = self.output_txt.toPlainText()
        checkCfile_radio_btn = self.check_realTime.isChecked()

        # if folder_input == "" and flag_run == True and checkCfile_radio_btn == False:
        #    flag_run = False
        #    QMessageBox.about(self.centralwidget, "👿 Error", "Please check input !!!")
        # if folder_output == "" and flag_run == True:
        #     flag_run = False
        #     QMessageBox.about(self.centralwidget, "👿 Error", "Please check output !!!")
        if checkCfile_radio_btn == False and folder_input == "":
            QMessageBox.about(self.centralwidget, "👿 Error", "Please check input")
        else:
            for i in range(0,101):
                time.sleep(0.01)
                self.ui.progressBar.setValue(i)

            if checkCfile_radio_btn == True and folder_input == "":
                subprocess.Popen(["python", "yolo_object_detection.py", "-o", folder_output, "-d", "1", "-y", "yolo-weapons", "-c", "0.5", "-t", "0.3", "-u", "0"]).wait()

            if checkCfile_radio_btn == False and folder_input != "":
                subprocess.Popen(["python", "yolo_object_detection.py", "-i", folder_input, "-o", folder_output, "-d", "1", "-y", "yolo-weapons", "-c", "0.5", "-t", "0.3", "-u", "0"]).wait()
                QMessageBox.about(self.centralwidget, "😄 Completed", "DONE")
            self.ui.progressBar.setValue(0)
        # if flag_run == True and folder:
        #     QMessageBox.about(self.centralwidget, "😄 Completed", "DONE")
        # else:
        #     QMessageBox.about(self.centralwidget, "👿 Error", "Please check again !!!")

    def get_linkFolder(self):
        global folder_input
        folder_input = QFileDialog.getOpenFileName(self.centralwidget, 'Select Directiory',".", "(*.mp4);; (*.avi);; (*.MOV)")
        self.input_txt.setText(folder_input[0])

    def get_linkFolderOutput(self):
        global folder_output
        folder_output = QFileDialog.getExistingDirectory(self.centralwidget, 'Select Directiory')
        self.output_txt.setText(folder_output + '/' + 'detection_result.avi')
    
    def realTime(self):
        folder_input = self.input_txt.toPlainText()
        checkCfile_radio_btn = self.check_realTime.isChecked()
        if checkCfile_radio_btn == True:
            folder_input_flag.append(folder_input)
        if checkCfile_radio_btn == True:
            #subprocess.Popen(["python", "yolo_object_detection_old.py", "-o", folder_output, "-d", "1", "-y", "yolo-weapons", "-c", "0.5", "-t", "0.3", "-u", "0"]).wait()
            self.input_txt.setText("")
            self.input_txt.setDisabled(True)
            self.inputBrowse.setEnabled(False)
        else:
            #subprocess.Popen(["python", "yolo_object_detection_old.py", "-i", folder_input, "-o", folder_output, "-d", "1", "-y", "yolo-weapons", "-c", "0.5", "-t", "0.3", "-u", "0"]).wait()
            self.input_txt.setText(folder_input_flag[-1])
            self.input_txt.setDisabled(False)
            self.inputBrowse.setEnabled(True)

    def close_ui(self):
        dialog = QMessageBox.question(self, close_UI.msg_ttl_close, close_UI.cntnt_quit, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if dialog == QMessageBox.Yes:
            self.close()
        else:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Ui_MainWindow()
    sys.exit(app.exec_())