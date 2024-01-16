# Jython script to split a stack into individual images and save them

from ij import IJ, ImagePlus
import os

loadFolder = IJ.getDirectory("Input_directory")
for file in os.listdir(loadFolder):
	f= os.path.join(loadFolder, file)
# Get the active image stack

imp = IJ.openImage(f)
stack = imp.getStack()

# Get the number of slices in the stack
n_slices = stack.getSize()
print(n_slices)
# Loop through each slice in the stack
for slice_index in range(1, n_slices + 1):
    # Select the current slice
    imp.setSlice(slice_index)

    # Duplicate the current slice
    duplicate = stack.getProcessor(slice_index).duplicate()
    duplicate_image = ImagePlus("Slice_" + str(slice_index), duplicate)

    # Save the duplicated slice
    save_path = loadFolder + str(slice_index) + ".tif"
    IJ.save(duplicate_image, save_path)

    # Close the duplicated slice
    duplicate_image.close()

# Close the original stack
imp.close()