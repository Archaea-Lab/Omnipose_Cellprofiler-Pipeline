from ij import IJ, ImagePlus, ImageStack
from ij.plugin.frame import RoiManager
import os
import re

loadFolder = IJ.getDirectory("Input_directory")
files = os.listdir(loadFolder)
#look only at .tifs
tempList = []
for f in files:
	if f[-4:] == '.tif':
		tempList.append(f)
files = tempList
print(files)
#sort the files
files.sort(key=lambda x: int(re.search(r'^(\d+)_', x).group(1)))
print(files)
#create empty stack
stack = ImageStack()
IJ.setForegroundColor(255, 255, 255)
# Loop through each file in the directory
print(files)
for file_name in files:
	#Create an ImagePlus from the file
    file_path = os.path.join(loadFolder, file_name)
    imp = IJ.openImage(file_path)
	#open associated ROIs
    rm = RoiManager().getInstance()
    rm.reset()
    rm.open(file_path.split('_label')[0]+"_Erosion_1px_RoiSet.zip")
	#run through the ROIs and color white
    roiList = rm.getRoisAsArray()
    i = list(range(len(roiList)))
    rm.setSelectedIndexes(i)
    rm.runCommand(imp,"Combine")
    rm.runCommand(imp,"Fill")

	#add image to stack
    stack.addSlice(file_name, imp.getProcessor())
	# Close the ImagePlus to free up resources
    #imp.close()
    
#save stack
#create stack as a physical image
output_image = ImagePlus("Stacked Images", stack)
#set channels, Z, and T appropriately
output_image.setDimensions(1,1,len(files))
#Display the new stack
output_image.show()


