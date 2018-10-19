#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Rizwan Hasan"
__copyright__ = "Copyright 2018"
__license__ = "GPL3"
__version__ = "1.0"
__maintainer__ = "Rizwan Hasan"
__email__ = "rizwan.hasan486@gmail.com"

"""

import os
import sys
import time
import subprocess
import webbrowser
from functools import partial

# My Imports
import threads
import resources
import mirrorlist
import rankmirrors
from dependency import checker

# PyQt5 Imports
import sip
from PyQt5 import uic
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QPushButton
from PyQt5.QtWidgets import QFileDialog, QDesktopWidget, QTextEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread

# Application root location ↓
appFolder = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(appFolder + 'MainWindow.ui', self)

        # ↓
        if checker().check() is False:
            sys.exit("Dependency missing")

        # Class Object Variables ↓
        self.mirrorlist = mirrorlist.Mirrorlist()
        self.ProgressLoader = threads.ProgressLoader()
        self.ProgressLoader_Rankmirrors = threads.ProgressLoader_Rankmirrors()

        # Normal Variables ↓
        self.mirrorlistFile = "/etc/pacman.d/mirrorlist"
        self.mirrorlistTemp = "/tmp/mirrorlist.temp"
        self.mirrorlistData = None
        self.comboBoxEntry = None
        self.comboBoxNumberEntry = None
        self.asroot = None

        # Icon Variables ↓
        self.icon = QIcon(':icon/icon.png')
        self.done = QPixmap(':done/done.png')
        self.distro = QPixmap(self.distroVar())
        self.loadingBar = QMovie(':loading/loading.gif')
        self.loadingCube = QMovie(':loading/cube_loading.gif')

        self.asrootDeclare()
        self.AppMainWindow()

    def distroVar(self):
        distro_name = subprocess.getoutput('lsb_release -i')
        distro_name = distro_name.split()
        distro_name = distro_name[2:]
        if distro_name[0] == 'MagpieOS':
            return ':linux/MagpieOS.png'
        else:
            return ':linux/archlinux.png'

    def makeWindowCenter(self):
        # For launching windows in center
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def asrootDeclare(self):
        if os.path.isfile('/usr/bin/gui-sudo') is True:
            self.asroot = "/usr/bin/gui-sudo "
        else:
            self.asroot = "pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY "

    def AppMainWindow(self):
        # Making window centered ↓
        self.makeWindowCenter()

        # Loading mirrorlist content in textbox ↓
        self.loadSysMirrorlist(0)

        # Window customizing ↓
        self.setWindowTitle('ArchLinux Mirrorlist Manager')
        self.setWindowIcon(self.icon)

        self.statusBar().showMessage("Hello World")

        # ↓
        self.labelHeader.setText(subprocess.getoutput("uname -rom"))

        # ↓
        self.pushButtonQuit.clicked.connect(self.closeDialogue)
        self.pushButtonReload.clicked.connect(self.loadSysMirrorlist)
        self.pushButtonSave.clicked.connect(self.saveButtonAction)
        self.pushButtonSaveAs.clicked.connect(self.saveFileDialog)
        self.pushButtonGenerate.clicked.connect(self.generateButtonAction)
        self.pushButtonRankmirrors.clicked.connect(self.rankmirrorsButtonAction)
        self.pushButtonContact.clicked.connect(self.browserContact)
        self.pushButtonSourcecode.clicked.connect(self.browserSourcecode)

        # ↓
        self.labelLoading.setPixmap(self.distro)
        self.labelAboutDistro.setPixmap(self.distro)
        self.comboBoxCountry.activated[str].connect(self.comboEntryMaker)
        self.comboBoxNumber.activated[str].connect(self.comboNumberEntryMaker)

    @pyqtSlot()  # Qt Framework's Slot Decorator
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?\nAll changes will be lost.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage('Exited.')
            event.accept()
        else:
            self.statusBar().showMessage('Welcome back.')
            event.ignore()

    def closeDialogue(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?\nAll changes will be lost.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.statusBar().showMessage('Exited.')
            sys.exit()
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
        self.pushButtonSaveAs.clicked.connect(self.saveFileDialog)

    # ↓
    def saveButtonAction(self):
        try:
            self.pushButtonSave.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        self.mirrorlistData = self.plainTextEdit.toPlainText()
        with open(self.mirrorlistTemp, 'w') as file:
            file.write(self.mirrorlistData)
        status = subprocess.getstatusoutput(self.asroot + "mv -f " + self.mirrorlistTemp + " " + self.mirrorlistFile)
        if status[0] is 0:
            self.statusBar().showMessage("Saved successfully")
            self.labelLoading.setPixmap(self.distro)
        else:
            self.statusBar().showMessage("Unable to save file")
        self.pushButtonSave.clicked.connect(self.saveButtonAction)

    # Combox Actions ↓
    def comboEntryMaker(self, x):
        self.comboBoxEntry = str(x)

    def comboNumberEntryMaker(self, x):
        self.comboBoxNumberEntry = x

    # ↓
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
        self.pushButtonReload.clicked.connect(self.loadSysMirrorlist)

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
        self.pushButtonGenerate.clicked.connect(self.generateButtonAction)

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
        self.pushButtonRankmirrors.clicked.connect(self.rankmirrorsButtonAction)

    # Contact Button Action ↓
    def browserContact(self, link):
        try:
            self.pushButtonContact.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        webbrowser.open('https://github.com/Rizwan-Hasan')
        self.pushButtonContact.clicked.connect(self.browserContact)

    # Sourcecode Button Action ↓
    def browserSourcecode(self, link):
        try:
            self.pushButtonSourcecode.clicked.disconnect()
        except (AttributeError, TypeError):
            pass
        webbrowser.open('https://bing.com')
        self.pushButtonSourcecode.clicked.connect(self.browserSourcecode)


def darkTheme(x):
    with open('darkorange.qss', 'r') as file:
        x.setStyleSheet(file.read())


# Main Function ↓
def main():
    app = QApplication(sys.argv)
    # darkTheme(app)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


# Start Application ↓
if __name__ == '__main__':
    main()