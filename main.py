#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys
import webbrowser

# PyQt5 Imports
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QFileDialog, QDesktopWidget

import resources
import mirrorlist
import threads
from dependency import checker


# Application root location ↓
appFolder = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'


class MainWindow(QMainWindow):

    def __init__(self):
        # noinspection PyArgumentList
        super(MainWindow, self).__init__()
        uic.loadUi(appFolder + 'MainWindow.ui', self)

        # Dependency and Files checker↓
        if checker().check() is False:
            sys.exit("Dependency missing, or you have edited something")

        # Class Object Variables ↓
        self.mirrorlist = mirrorlist.Mirrorlist()
        self.ProgressLoader = threads.ProgressLoader()
        self.ProgressLoader_Rankmirrors = threads.ProgressLoader_Rankmirrors()

        # General Variables ↓
        self.mirrorlistFile = "/etc/pacman.d/mirrorlist"
        self.mirrorlistTemp = "/tmp/mirrorlist.temp"
        self.mirrorlistData = None
        self.comboBoxEntry = None
        self.comboBoxNumberEntry = None
        self.asroot = None
        self.contactURL = 'https://github.com/Rizwan-Hasan'
        self.sourcecodeURL = 'https://github.com/Rizwan-Hasan/ArchLinux-Mirrorlist-Manager'

        # Icon's Variables ↓
        self.icon = QIcon(':icon/icon.png')
        self.done = QPixmap(':done/done.png')
        self.distro = QPixmap(self.distroVar())
        self.loadingBar = QMovie(':loading/loading.gif')
        self.loadingCube = QMovie(':loading/cube_loading.gif')

        # Calling fucntions ↓
        self.asrootDeclare()
        self.AppMainWindow()

    # Distribution checking↓
    def distroVar(self):
        distro_name = subprocess.getoutput('lsb_release -i')
        magpieos = re.compile(r'MagpieOS', re.IGNORECASE)
        manjaro = re.compile(r'Manjaro', re.IGNORECASE)
        # noinspection PyArgumentList,PyArgumentList
        if magpieos.findall(distro_name):
            return ':linux/MagpieOS.png'
        elif manjaro.findall(distro_name):
            # noinspection PyCallByClass,PyArgumentList
            QMessageBox.information(self, 'Message', "Mirrorlist Manager doesn't support Manjaro")
            sys.exit(0)
        else:
            return ':linux/archlinux.png'

    # For launching windows in center ↓
    def makeWindowCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    # Defining root permission using method ↓
    def asrootDeclare(self):
        self.asroot = "pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY "

    # Main Application Window ↓
    def AppMainWindow(self):
        # Making window centered ↓
        self.makeWindowCenter()

        # Loading mirrorlist content in textbox ↓
        self.loadSysMirrorlist(0)

        # Window customizing ↓
        self.setWindowTitle('ArchLinux Mirrorlist Manager')
        self.setWindowIcon(self.icon)

        # Header label ↓
        self.labelHeader.setText(subprocess.getoutput("uname -rm"))

        # Buttons's Actions↓
        self.pushButtonQuit.clicked.connect(lambda: self.closeDialogue())
        self.pushButtonReload.clicked.connect(lambda: self.loadSysMirrorlist())
        self.pushButtonSave.clicked.connect(lambda: self.saveButtonAction())
        self.pushButtonSaveAs.clicked.connect(lambda: self.saveFileDialog())
        self.pushButtonGenerate.clicked.connect(lambda: self.generateButtonAction())
        self.pushButtonRankmirrors.clicked.connect(lambda: self.rankmirrorsButtonAction())
        self.pushButtonContact.clicked.connect(lambda: self.browserContact())
        self.pushButtonSourcecode.clicked.connect(lambda: self.browserSourcecode())

        # Other Actions↓
        self.labelLoading.setPixmap(self.distro)
        self.labelAboutDistro.setPixmap(self.distro)
        self.comboBoxCountry.activated[str].connect(self.comboEntryMaker)
        self.comboBoxNumber.activated[str].connect(self.comboNumberEntryMaker)

    # noinspection PyArgumentList
    @pyqtSlot()  # Qt Framework's Slot Decorator
    # Close event dialogue ↓
    def closeEvent(self, event):
        # noinspection PyCallByClass
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?\nAll changes will be lost.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage('Exited.')
            event.accept()
        else:
            self.statusBar().showMessage('Welcome back.')
            event.ignore()

    # Close dialouge message ↓
    def closeDialogue(self):
        # noinspection PyCallByClass
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?\nAll changes will be lost.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage('Exited.')
            sys.exit(0)
        else:
            self.statusBar().showMessage('Welcome back.')

    # File Dialogs ↓
    def saveFileDialog(self):
        try:
            self.pushButtonSaveAs.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog # Qt's builtin File Dialogue
        # noinspection PyCallByClass
        fileName, _ = QFileDialog.getSaveFileName(self, "Open", "", "All Files (*.*)", options=options)
        if fileName:
            try:
                with open(fileName, 'w') as file:
                    file.write(self.plainTextEdit.toPlainText())
                self.statusBar().showMessage("'" + fileName + "' saved successfully")
                self.labelLoading.setPixmap(self.distro)
            except PermissionError:
                pass
                self.statusBar().showMessage("Unable to save '" + fileName + "'")
        self.pushButtonSaveAs.clicked.connect(lambda: self.saveFileDialog())

    # Save Button's Actons↓
    def saveButtonAction(self):
        try:
            self.pushButtonSave.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        self.mirrorlistData = self.plainTextEdit.toPlainText()
        with open(self.mirrorlistTemp, 'w') as file:
            file.write(self.mirrorlistData)
        status = subprocess.getstatusoutput(self.asroot + "mv -f " + self.mirrorlistTemp + " " + self.mirrorlistFile)
        if status[0] == 0:
            self.statusBar().showMessage("Saved successfully")
            self.labelLoading.setPixmap(self.distro)
        else:
            self.statusBar().showMessage("Unable to save file")
        self.pushButtonSave.clicked.connect(lambda: self.saveButtonAction())

    # Country Combox Actions ↓
    def comboEntryMaker(self, x):
        self.comboBoxEntry = str(x)

    # Number Combox Actions ↓
    def comboNumberEntryMaker(self, x):
        self.comboBoxNumberEntry = x

    # Reload Button's Actions↓
    def loadSysMirrorlist(self, x=1):
        try:
            self.pushButtonReload.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        with open(self.mirrorlistFile, 'r') as file:
            text = file.read()
        self.plainTextEdit.setPlainText(text)
        self.labelLoading.setPixmap(self.distro)
        if x is False:
            self.statusBar().showMessage("Mirrorlist has been reloaded")
        self.pushButtonReload.clicked.connect(lambda: self.loadSysMirrorlist())

    # Animation Method ↓
    def loadingBarAnimation(self, decider: bool):
        if decider is True:
            self.labelLoading.setMovie(self.loadingBar)
            self.labelLoadingCube.setMovie(self.loadingCube)
            self.loadingCube.setSpeed(150)
            self.plainTextEdit.clear()
            self.loadingBar.start()
            self.loadingCube.start()
        else:
            self.loadingBar.stop()
            self.loadingCube.stop()
            self.labelLoadingCube.clear()
            self.labelLoading.setPixmap(self.done)

    # Generate Button Action ↓
    def generateButtonAction(self):
        try:
            self.pushButtonGenerate.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        self.statusBar().showMessage("Generating mirrorlist...")
        self.loadingBarAnimation(True)
        self.ProgressLoader.send(self.comboBoxEntry)
        self.ProgressLoader.start()
        self.ProgressLoader.loaderOFF.connect(self.loadingBarAnimation)
        self.ProgressLoader.mirrorlistData.connect(self.plainTextEdit.setPlainText)
        self.ProgressLoader.status.connect(self.statusBar().showMessage)
        self.pushButtonGenerate.clicked.connect(lambda: self.generateButtonAction())

    # Rankmirrors Button's Actions ↓
    def rankmirrorsButtonAction(self):
        try:
            self.pushButtonRankmirrors.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        self.statusBar().showMessage("Ranking mirrorlist...")
        mirrorlistData = self.plainTextEdit.toPlainText()
        self.loadingBarAnimation(True)
        self.ProgressLoader_Rankmirrors.send(self.comboBoxNumberEntry, mirrorlistData)
        self.ProgressLoader_Rankmirrors.start()
        self.ProgressLoader_Rankmirrors.loaderOFF.connect(self.loadingBarAnimation)
        self.ProgressLoader_Rankmirrors.mirrorlistData.connect(self.plainTextEdit.setPlainText)
        self.ProgressLoader_Rankmirrors.status.connect(self.statusBar().showMessage)
        self.pushButtonRankmirrors.clicked.connect(lambda: self.rankmirrorsButtonAction())

    # Contact Button Action ↓
    def browserContact(self):
        try:
            self.pushButtonContact.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        webbrowser.open(self.contactURL)
        self.pushButtonContact.clicked.connect(lambda: self.browserContact())

    # Sourcecode Button Action ↓
    def browserSourcecode(self):
        try:
            self.pushButtonSourcecode.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        webbrowser.open(self.sourcecodeURL)
        self.pushButtonSourcecode.clicked.connect(lambda: self.browserSourcecode())


# Main Function ↓
def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


# Start Application ↓
if __name__ == '__main__':
    main()
