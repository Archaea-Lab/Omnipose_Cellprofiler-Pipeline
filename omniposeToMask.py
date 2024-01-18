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
	print("Starting...")
	loadFolder = IJ.getDirectory("Input_directory")
	files = os.listdir(loadFolder)
	tempList = []
	for f in files:
		if f[-4:] == '.tif':
			tempList.append(f)
	files = tempList
	print(files)
	files.sort(key=lambda x: int(re.search(r'^(\d+)_', x).group(1)))
	print(files)
	stack = ImageStack()
	IJ.setForegroundColor(255, 255, 255)
	for file_name in files:
    		file_path = os.path.join(loadFolder, file_name)
    		imp = IJ.openImage(file_path)
    		rm = RoiManager().getInstance()
    		rm.reset()
    		rm.open(file_path.split('_label')[0]+"_Erosion_1px_RoiSet.zip")
    		roiList = rm.getRoisAsArray()
    		i = list(range(len(roiList)))
    		rm.setSelectedIndexes(i)
    		rm.runCommand(imp,"Combine")
    		rm.runCommand(imp,"Fill")
    		stack.addSlice(file_name, imp.getProcessor())
		# Close the ImagePlus to free up resources
    		#imp.close()
	output_image = ImagePlus("Stacked Images", stack)
	output_image.setDimensions(1,1,len(files)) #set channels, Z, and T appropriately
	output_image.show()
	print("Finished converting masks to binary form.")
	print("Done!")

main()

