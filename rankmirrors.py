#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dependency import checker
from subprocess import getoutput


# Mirrorlist Ranker ↓
class MirrorRanker(checker):

    def __init__(self):
        super(MirrorRanker, self).__init__()

    # Rankmirrors ↓
    def rank(self, num=3, mirrorfile='/etc/pacman.d/mirrorlist'):
        if self.check() is True:
            cmd = getoutput("which rankmirrors") + " -n " + str(num) + " " + mirrorfile
            output = getoutput(cmd)
            return output
        else:
            return False


if __name__ == '__main__':
    print("Hello World")
