"""
author: johnmallon

This script takes the 'label images' masks output by Omnipose, and uses the ROIs created by 'Labels to ROIs' to convert the masks to a binary form usable for CellProfiler. The individual masks for each frame are combined
into a single stack. Make sure to MANUALLY save the stack after visual inspection.

This script should be run in the imageJ macro window
"""

from ij import IJ, ImagePlus, ImageStack
from ij.plugin.frame import RoiManager
import os
import re




def main():
    ########### USER INPUT STARTS #############
    
    singleImages = True # set to False if you have a folder of single images
    dataFolder = 'input directory of single channel raw data'
    ########### USER INPUT ENDS #############
    
    
    print("Starting...")
    loadFolder = IJ.getDirectory("Input_directory")
    files = os.listdir(loadFolder)
    tempList = []
    for f in files:
        if f[-4:] == '.tif':
            tempList.append(f)
    files = tempList
    print(files)
    if not singleImages:
        files.sort(key=lambda x: int(re.search(r'^(\d+)_', x).group(1)))
        print(files)
    else:
        dataStack = ImageStack()
    maskStack = ImageStack()
    for file_name in files:
            file_path = os.path.join(loadFolder, file_name)
            imp = IJ.openImage(file_path)
            IJ.setForegroundColor(0, 0, 0)
            IJ.run(imp, "Select All", "")
            IJ.run(imp, "Fill", "")
            IJ.setForegroundColor(255, 255, 255)
            rm = RoiManager().getInstance()
            rm.reset()
            rm.open(file_path.split('_label')[0]+"_Erosion_1px_RoiSet.zip")
            roiList = rm.getRoisAsArray()
            i = list(range(len(roiList)))
            rm.setSelectedIndexes(i)
            rm.runCommand(imp,"Fill")
            IJ.run(imp, "8-bit", "")
            maskStack.addSlice(file_name, imp.getProcessor())
            if singleImages:
                dataName = file_name.split('_cp')
                dataName = dataName[0]+'.tif'
                file_path = os.path.join(dataFolder, dataName)
                imp = IJ.openImage(file_path)
                dataStack.addSlice(file_name, imp.getProcessor())
            #Close the ImagePlus to free up resources
            #imp.close()
    outputMask = ImagePlus("Stacked Masks", maskStack)
    outputImage = ImagePlus("Stacked Data", dataStack)
    outputMask.setDimensions(1,1,len(files)) #set channels, Z, and T appropriately
    outputMask.show()
    outputImage.setDimensions(1,1,len(files)) #set channels, Z, and T appropriately
    outputImage.show()
    print("Finished converting masks to binary form.")
    print("Done!")

main()

