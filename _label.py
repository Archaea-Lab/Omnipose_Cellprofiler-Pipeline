# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:02:40 2023

@author: bisso

This program will open a folder of files and add the extension to the file name "_label"
"""


import os


def main():
    #open folder
    folder = R"H:\Halofilin Shape Transitions\KO Shape Transitions\HalB KO\HalBDisktoRod_FullField\masks\\"
    files = os.listdir(folder)
    for file in files:
       if os.path.isfile(os.path.join(folder, file)):
           newName = file.split('.')[0] +'_label.tif'
           #Rename the file
           oldPath = os.path.join(folder, file)
           newPath = os.path.join(folder, newName)
           os.rename(oldPath, newPath)

main()

