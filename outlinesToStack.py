from ij import IJ, ImagePlus, ImageStack
import os
import re

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