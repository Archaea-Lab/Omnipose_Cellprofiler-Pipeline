"""
author: johnmallon

This script takes individual images a creates a stack of them. You should MANUALLY save the stack after inspecting it.

This script should be run in the imageJ macro window.
"""
from ij import IJ, ImagePlus, ImageStack
import os
import re


def main():
	################# USER INPUT STARTS HERE ##########################
	timelapse = False
	################# USER INPUT ENDS HERE ##########################
	print("Starting...")
	loadFolder = IJ.getDirectory("Input_directory")
	files = os.listdir(loadFolder)
	if timelapse:
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
