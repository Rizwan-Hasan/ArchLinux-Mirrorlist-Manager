#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import pandas as pd


class Mirrorlist():
    # Application root location ↓
    appFolder = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'

    def __init__(self):
        self.mirrorfile = "/tmp/mirrorlist.txt"
        self.country_code_dataset = self.appFolder + 'country_code.data'
        self.url = "https://www.archlinux.org/mirrorlist/?COUNTRYCODEprotocol=http&protocol=https&ip_version=4"

    # Mirrorlist getting ↓
    def get_mirrorlist(self, country_code):
        """
        try:
            os.remove(self.mirrorfile)
        except FileNotFoundError:
            pass
        """
        country_code = self.country_code_detect(country_code)

        url = "'" + self.create_url(country_code) + "'"
        subprocess.getoutput("curl -L -o " + self.mirrorfile + " " + url)

        mirrordata = None
        with open(self.mirrorfile, 'r') as file:
            mirrordata = file.read()
        os.remove(self.mirrorfile)

        distro_name = subprocess.getoutput('lsb_release -i')
        distro_name = distro_name.split()
        distro_name = distro_name[2:]
        distro_name = "## " + ' '.join(distro_name)

        mirrordata = mirrordata.replace("#Server =", "Server =")
        mirrordata = mirrordata.replace("## Arch Linux", distro_name)
        mirrordata = mirrordata.replace("Generated", "Generated with Mirrorlist Manager")
        # with open(self.mirrorfile, 'w') as file:
        #     file.write(mirrordata)
        # os.system('chmod 777 ' + self.mirrorfile)
        return mirrordata

    # Mirrolist url creator ↓
    def create_url(self, country_code='country=all&'):
        url = self.url
        country_code = country_code.strip()
        country_code = country_code.split()

        if(country_code[0] == "all"):
            x = 'country=' + country_code[0] + '&'
            url = url.replace('COUNTRYCODE', x)
            return url

        for cntrycode in country_code:
            if (cntrycode == country_code[len(country_code) - 1]):
                x = 'country=' + cntrycode.upper() + '&'
            else:
                x = 'country=' + cntrycode.upper() + '&' + 'COUNTRYCODE'
            url = url.replace('COUNTRYCODE', x)
        return url

    # Country code detector ↓
    def country_code_detect(self, cinput):
        if (cinput == "all"):
            return "all"
        cinput = cinput.strip()
        df = pd.read_csv(self.country_code_dataset)
        match = df['Country'].str.match(cinput)
        contry_code = df[match].values[0][1]
        return contry_code


if __name__ == '__main__':
    print("Hello World")
