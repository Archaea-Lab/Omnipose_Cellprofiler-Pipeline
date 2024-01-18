"""
author: johnmallon

This script takes the individual segmentation images for each frame that omnipose outputs and stiched them together into a single stack and displays the stack. You should MANUALLY save the stack after inspecting it.

This script should be run in the imageJ macro window.
"""
from ij import IJ, ImagePlus, ImageStack
import os
import re


def main():
	print("Starting...")
	loadFolder = IJ.getDirectory("Input_directory")
	files = os.listdir(loadFolder)
	tempList = []
	for f in files:
		if f[-4:] == '.png':
			tempList.append(f)
	files = tempList
	files.sort(key=lambda x: int(re.search(r'^(\d+)_', x).group(1)))
	stack = ImageStack()

	for frame in files:
   		file_path = os.path.join(loadFolder, frame)
   		imp = IJ.openImage(file_path)
   		stack.addSlice(frame, imp.getProcessor())
   		imp.close()
    
	output_image = ImagePlus("Stacked Images", stack)
	output_image.setDimensions(1,1,len(files)) #set channels, Z, and T appropriately
	output_image.show()
	print("Stack created")
	print("Done!")

main()
