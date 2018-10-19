#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class checker():

    def __init__(self):
        self.result = bool()
        self.package_check()

    def package_check(self):
        import subprocess  # 'subprocess' Module Import
        output = subprocess.getstatusoutput("pacman -Q pacman-contrib pacman-mirrorlist magpie-mirrorlist")
        if output[0] is 0:
            output = subprocess.getstatusoutput("which rankmirrors")
            if output[0] is 0:
                self.result = True
            else:
                self.result = False
        else:
            self.result = False

    def check(self):
        return self.result


if __name__ == '__main__':
    print("Hello World")

