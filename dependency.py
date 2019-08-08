#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from mirrorlist import Mirrorlist


class checker():
    appFolder = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'

    def __init__(self):
        # Hash Variable
        self.country_data = 'b6bd3a5c2044346efb684bf053b535c3'
        self.MainWindowUi = '3f454854f53d873c21c6b44d60b6df6d'

    # Package avilability checker ↓
    def package_check(self):
        packages = "pacman-contrib pacman-mirrorlist pyqt5-common python-pyqt5 python-sip-pyqt5 python-pandas"
        output = subprocess.getstatusoutput("pacman -Q " + packages)
        if output[0] is 0:
            output = subprocess.getstatusoutput("which rankmirrors")
            if output[0] is 0:
                return True
            else:
                return False
        else:
            return False

    # Files hash checker
    def hashcheck(self):

        # country_code.data ↓
        x = subprocess.getoutput('md5sum ' + Mirrorlist().country_code_dataset)
        if x.split()[0] == self.country_data:
            pass
        else:
            return False

        # MainWindow.ui ↓
        x = subprocess.getoutput('md5sum ' + self.appFolder + 'MainWindow.ui')
        if x.split()[0] == self.MainWindowUi:
            pass
        else:
            return False

        return True

    # Checking starter & returner ↓
    def check(self):
        x = self.package_check()
        y = self.hashcheck()
        if (x is True and y is True):
            return True
        else:
            return False


if __name__ == '__main__':
    print("Hello World")
