"""
Created on Tue Feb 27 12:57:22 2024

@author: johnmallon


This program will take the txt files saved from omnipose and 

1. convert and save the ROIs from .txt to imageJ usable form
2. use the ROIs to create a binary mask (0/255)

This is a modified version of the 'imagej_roi_converter.py' script created by Franco D'Agostino from Cellpose github
https://github.com/MouseLand/cellpose/blob/main/imagej_roi_converter.py

It should be run in the imageJ macro window. A window will pop up asking for a directory. Please
selected where the 'txt_outlines' folder generated from Omnipose
"""

from ij import IJ, ImagePlus, ImageStack
import os
import re
from ij.plugin.frame import RoiManager
from ij.gui import PolygonRoi
from ij.gui import Roi
from java.awt import FileDialog

def imagej_roi_converter(rois,loadFolder,stack):
    imageDirectory = rois.split('txt_outlines\\')
    imageName = imageDirectory[1].split('_cp')[0]+'.tif'
    imagePath = imageDirectory[0]+imageName
    imp = IJ.openImage(imagePath)
    #imp.show()
    IJ.setForegroundColor(0, 0, 0)
    IJ.run(imp, "Select All", "")
    IJ.run(imp, "Fill", "")
   
    rm = RoiManager().getInstance()
    rm.reset()
    #imp = IJ.getImage()

    textfile = open(rois, "r")
    for line in textfile:
        lineText = line.rstrip()
        if not lineText:
            continue
        xy = map(int, line.rstrip().split(","))
        X = xy[::2]
        Y = xy[1::2]
        imp.setRoi(PolygonRoi(X, Y, Roi.POLYGON))
        # IJ.run(imp, "Convex Hull", "")
        roi = imp.getRoi()
        
        rm.addRoi(roi)
    textfile.close()
    rm.runCommand("Associate", "true")
    rm.runCommand("Show All with labels")

    roiList = rm.getRoisAsArray()
    i = list(range(len(roiList)))
    rm.setSelectedIndexes(i)
    
    rm.save(imageDirectory[0]+imageDirectory[1][:-4]+'_ROIs.zip')
    IJ.setForegroundColor(255, 255, 255)
    rm.runCommand(imp,"Fill")
    IJ.run(imp, "8-bit", "")
    stack.addSlice(imageName, imp.getProcessor())
    #imp.close()
    
    return stack
    
    
def main():
    timelapse = True
    print("Starting...")
    loadFolder = IJ.getDirectory("Input_directory") #select the 'txt_outlines' folder that omnipose generated
    files = os.listdir(loadFolder)
    if timelapse:
        files.sort(key=lambda x: int(re.search(r'^(\d+)_', x).group(1)))
    maskStack = ImageStack()
    for rois in files:
        file_path = os.path.join(loadFolder, rois)
        maskStack = imagej_roi_converter(file_path,loadFolder,maskStack) 
    outputMask = ImagePlus("Stacked Masks", maskStack)
    outputMask.setDimensions(1,1,len(files)) #set channels, Z, and T appropriately
    outputMask.show()
main()
