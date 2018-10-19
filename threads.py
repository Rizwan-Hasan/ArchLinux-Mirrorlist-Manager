#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from mirrorlist import Mirrorlist
from rankmirrors import MirrorRanker
from PyQt5.QtCore import pyqtSignal, QThread


class ProgressLoader(QThread):

    loaderOFF = pyqtSignal(bool)
    status = pyqtSignal(str)
    mirrorlistData = pyqtSignal(str)

    def __init__(self):
        super(ProgressLoader, self).__init__()

        self.comboBoxEntry = None

    def run(self):
        data = Mirrorlist().get_mirrorlist(self.comboBoxEntry)
        self.loaderOFF.emit(False)
        self.status.emit("Mirrorlist has been generated successfully")
        self.mirrorlistData.emit(data)

    def send(self, comboBox):
        if comboBox is None:
            self.comboBoxEntry = "all"
        else:
            self.comboBoxEntry = comboBox


class ProgressLoader_Rankmirrors(QThread):

    loaderOFF = pyqtSignal(bool)
    status = pyqtSignal(str)
    mirrorlistData = pyqtSignal(str)

    def __init__(self):
        super(ProgressLoader_Rankmirrors, self).__init__()

        self.num = int()
        self.mirrorlistFile = None

    def run(self):
        data = MirrorRanker().rank(self.num, self.mirrorlistFile)
        self.loaderOFF.emit(False)
        self.status.emit("Mirrorlist has been ranked successfully")
        self.mirrorlistData.emit(data)

    def send(self, num: int, mirrorlist):
        tmpMirrorFile = '/tmp/.mirror.txt.tmp'
        os.system('rm -rf ' + tmpMirrorFile)
        with open(tmpMirrorFile, 'w') as file:
            file.write(mirrorlist)
        self.num = num
        self.mirrorlistFile = tmpMirrorFile


if __name__ == '__main__':
    print("Hello World")
