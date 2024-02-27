# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:02:40 2023

@author: johnmallon

This program will open a folder of files and add the extension to the file name "_label"

This program should be run in the imageJ macro window.
"""
import os
from ij import IJ


def main():
    print("Starting...")
    loadFolder = IJ.getDirectory("Input_directory")
    files = os.listdir(loadFolder)
    for file in files:
        oldPath = os.path.join(loadFolder, file)
        if os.path.isfile(oldPath):
            newName = file.split('.')[0] +'_label.tif'
            newPath = os.path.join(loadFolder, newName)
            os.rename(oldPath, newPath)
    print(" '_label' added as suffix to all files.")
    print("Done!")

main()

