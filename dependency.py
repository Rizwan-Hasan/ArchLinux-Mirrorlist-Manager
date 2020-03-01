# -*- coding: utf-8 -*-

import os
import subprocess
import sys


class checker():
    appFolder = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'

    # Package avilability checker ↓
    def __package_check(self):
        packages = "pacman-contrib pacman-mirrorlist python-pyqt5 python-pandas"
        output = subprocess.getstatusoutput("pacman -Q " + packages)
        if output[0] == 0:
            output = subprocess.getstatusoutput("which rankmirrors")
            if output[0] == 0:
                return True
            else:
                return False
        else:
            return False

    # Checking starter & returner ↓
    def check(self):
        x = self.__package_check()
        if x is True:
            return True
        else:
            return False


if __name__ == '__main__':
    print("Hello World")
