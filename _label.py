# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:02:40 2023

@author: johnmallon

This program will open a folder of files and add the extension to the file name "_label"
"""
import os


def main():
    folder = R"H:\Halofilin Shape Transitions\KO Shape Transitions\HalB KO\HalBDisktoRod_FullField\masks\\"
    files = os.listdir(folder)
    for file in files:
        oldPath = os.path.join(folder, file)
        if os.path.isfile(oldPath):
            newName = file.split('.')[0] +'_label.tif'
            newPath = os.path.join(folder, newName)
            os.rename(oldPath, newPath)

main()

