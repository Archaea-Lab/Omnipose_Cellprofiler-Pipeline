# Omnipose_Cellprofiler-Pipeline

Author: John Mallon

For segmenting and tracking single cells during growth under a microscope. This pipeline uses Omnipose (https://github.com/kevinjohncutler/omnipose) to segment cells and Cellprofiler (https://github.com/CellProfiler) to track them. The Bisson Lab installs and uses omnipose through the use of Anaconda (https://www.anaconda.com/)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## INSTALLATIONS

### INSTALLATION OF OMNIPOSE
*For in-depth instructions refer to https://github.com/kevinjohncutler/omnipose
The instructions below were used to install Omnipose on our lab computer to run using the GPU. Our lab computer runs "Windows 11 Home Edition" with a 64-bit processor. Our GPU is a NVIDIA GeForce RTX 4090.*

1. Go to environments tab of Anaconda GUI and open a terminal in your "Base environment"
2. In terminal type "conda create -n omniposeGPU 'python==3.10.12' pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia" then hit ENTER
3. In terminal type "conda activate omniposeGPU" then hit ENTER
4. In terminal type "pip install omnipose" then hit ENTER
5. In terminal type "pip install natsort" then hit ENTER
6. In terminal type "conda remove pytorch-cuda" then hit ENTER
7. In terminal type "conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia" then hit ENTER

### INSTALLATION OF CELLPROFILER
*CellProfiler was installed using the default instructions from their website (cellprofiler.org)*

### INSTALLATION OF LabelsToROIs
*LabelsToROIs is a imageJ FIJI macro installed using its default instructions (https://labelstorois.github.io)*

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## SEGMENTATION OF CELLS

### Pre-omnipose processing of data
*Omnipose doesn't work on stacks of images so all timelapse stacks have to be made into folders contains each frame as a separate '.tif' file. The "splitStacks.py" script will do this for us.*

1. Create a folder and call it "Omnipose_Analysis"
2. Drop a single channel of a timelapse file to be segmented into Omnipose_Analysis folder
3. Open FIJI, start up the macros window, and run the "splitStacks.py" script
4. A window will pop up asking where your data is. Select the Omnipose_Analysis folder
5. When script is done, open the Ominipose_Analysis folder and remove the original timelapse file. Would should be left in the folder is the stack broken up into individual images for each frame

### Running Omnipose
*Now that a stack has been made into a series of image files Omnipose can be run.*

1. Go to environments tab of Anaconda GUI and switch your "omniposeGPU" environment and open a terminal
2. In the terminal type "omnipose --dir "C:\Users\bisso\Desktop\omniposeAnalysis" --use_gpu --pretrained_model bact_phase_omni --save_outlines --save_tif --in_folders --no_npy --exclude_on_edges". Switch out the directory so that it points to your Omnipose_Analysis folder correctly. Then hit ENTER. Omnipose will run in the terminal. It will update there as to its progress.
3. If using a custom model type this instead "omnipose --dir "C:\Users\bisso\Desktop\omniposeAnalysis" --use_gpu --pretrained_model "C:\Users\bisso\Desktop\omniposeTrain\crops\models\custom_volcaniiRodDisk" --dim 2 --nclasses 2 --nchan 1 --save_outlines --save_tif --in_folders --no_npy --exclude_on_edges". Switch out the directories so that they point to your Omnipose_Analysis folder and custom model correctly. Then hit ENTER. Omnipose will run in the terminal. It will update there as to its progress.
4. When Omnipose is done it will have stored the masks and the segmentation outlines in new folders called 'masks' and a 'outlines'.

### Assess Omnipose Results
*Omnipose has saved the masks and the outlines of those masks as images in the Omnipose_Analysis folder when it is done. The segmentation needs to be assessed for quality before moving forward. The next steps will take the outline images and convert them back to a stack for viewing.*

1. Open FIJI, start up the macros window, and run the "outlinesToStack.py" script on the "outlines" directory
2. Save the stack output by FIJI and assess the segmentation.
3. Now that you have the stack, delete all the individual outline images to save storage
4. If all doesn't look good. Rerun the omnipose with same command thought omit the "--no_npy" argument. This will allow you to load the masks in the omnipose GUI to manually correct for training purposes. (See Training Section Below)

### Convert Omnipose masks to actual masks
*https://labelstorois.github.io does a great job of explaining why this is needed. In short, the output masks of omnipose is actually what is called a 'labeled image' not a binary mask. It is a greyscale image where each object detected by omnipose is given a unique number value. We want to convert this so that all objects have a value of 255 (white) and backgound has a value of 0 (black). The "labelstorois" FIJI plugin will create a '.zip' file of the ROIs segmented and the "omniposeToMasks.py" script will take those ROIs and create a binary mask image from them. To run "labelstorois" on a folder full of images though, all images have to have the suffix "_label.tif". Our "_labels.py" script will add this to our filenames.*

1. Run "_label.py" script using the "masks" folder as the directory
2. In FIJI open the plugin "LabelsToRoi" and run the multiple image button with an erode by 1 pixel using the "masks" directory
3. Run the FIJI macro "omniposeToMask.py"
4. Save the binary mask stack that gets output by FIJI
5. Now that you have the stack, delete all the individual images to save storage

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## TRACKING OF CELLS

### Use CellProfiler to track cells over time
*CellProfiler will take the binary masks we generated from Omnipose's segmentation and use that to track our cells using the Linear Assignment Problem (LAP) algorithm.*

1. Run CellProfiler and open the "trackingSingleCells.cpproj" file
2. Drag and drop, or open, the binary mask we generated from omnipose
3. Update the metadata and grouping data by selecting their respective tabs and clicking the update buttons. Sometimes you have to alternate between "Matching Any" and "Matching All" the rules to get CellProfiler to update correctly. We don't know why you have to do this sometimes and not all the time. Just do this until you see all of your frames pop into existance within the CellProfiler GUI.
4. Run the program by hitting the play button. As it runs a window will pop up and update each frame with the outlines of objects it finds on top of the mask we used as input. Make sure this generally looks good.

### Process CellProfiler Data
*CellProfiler refers to cells as "object numbers" in its output but if we track a cell from frame to frame its object number can change especially if*

*1. There is movement of cells in the field of view and &*

*2. There is a high density of cells*

*This is because "Object Numbers" are assigned independently from frame to frame in the order of left to right and top to bottom. Cells are tracked as full lineages in CellProfiler but individual cells/cell cycles (cells-through-time) are not given clear, unique, identifiers. Finally, the tracking results CellProfiler shows you in the GUI comes from the first phase of LAP calculations, this first phase does not include the calculations done that allow for splitting of cells and so the visual tracking that pops up in the GUI is just flat out not correct. These calculations are done and the final output of numbers from CellProfiler includes this second LAP tracking phase, but we have no easy visual representation to asses the quality of the tracking. Running these next scripts will solve these issues.*

*These issues with CellProfiler are documented here:*

*https://forum.image.sc/t/track-objects-lap-2nd-phase-workaround/13081 &*

*https://forum.image.sc/t/trackobjects-lap/14030*

 1. Run "CP_analysis.py" script pointing the directory to the "FilterObjects.csv" that was output from CellProfiler
 2. The program is done when a graph is output display single cells' Area vs. Time
 3. Open the tracking '.tif' file that was output and assess the quality of the tracking
 4. If tracking looks good, you can use the output '.csv' file to for further graphing of data, where each cell has been given a unique 'Cell ID' number



# Training a custom omnipose model

1. Put 510 X 510px sized images inside a folder that you want to use as a training set. Try not to use images that have way more background vs. foreground.
2. Open a terminal in the omniposeGPU environment and type "omnipose". This will open the GUI.
3. Drag and drop one of the training images into the GUI window and segment with one of the default models.
4. Once ROIs/masks are populated in the window, manually fix the errors by:
   a) control/left-click deletes masks
   b) left-click to select a single mask then alt/left-click a second mask to merge them into a single mask
   c) right-click to start drawing the edge of a mask. Move the mouse back into the red circle to complete the drawing.
5. Click File-->save mask as .png
6. Open the .png in FIJI and save as a .tif
7. Put the .tif mask file into the same folder as the training images. Name it the same as the image it is associated with but with the "_masks.tif" extension
8. Do this for all images in the training folder. If all is set you can delete the .png files.
9. In the omniposeGPU terminal type: <omnipose --train --use_gpu --dir "C:\Users\bisso\Desktop\omniposeTrain\crops" --mask_filter _masks --pretrained_model None --diameter 0 --learning_rate 0.1 --batch_size 16 --n_epochs 4000>
   a) Most of these settings I just took from "omnipose.readthedocs.io" For a trainging set of 122 images I used a batch_size of 16. If you have fewer training images perhaps make this number lower. 
10. Trained model will now be in a "models" folder within the trainset folder. You can rename the file to something more useful.
11. You can now load this model into the Omnipose GUI and test it to see how it behaves. Repeat steps 4 through 9 accordingly.
