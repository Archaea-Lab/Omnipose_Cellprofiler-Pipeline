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

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## SEGMENTATION OF CELLS

### Pre-omnipose processing of data
*Omnipose doesn't work on stacks of images so all timelapse stacks have to be made into folders contains each frame as a separate '.tif' file. The "splitStacks.py" script will do this for us. If your data is already in the form of single '.tif' images, it will still be essential for us to create a stacked version of the data for later steps...*

1. Create a folder and call it "Omnipose_Analysis"
2. All analysis done by Ominpose will be on SINGLE CHANNEL images. If you have more than one channel the first thing to do is, in imageJ, click Image --> Color --> Split Channels and save each channel as a separate '.tif' file
3. Are you running an analysis on a stack? If yes, skip to step 7
4. If you have a folder with a bunch of images not in a stack, we should create a stack of those images. Open FIJI, start up the macros window, and run the "imagesToStack.py" script.
5. A window will pop up asking where your data is. Select the folder that contains all the images.
6. Save the stack output by imageJ
7. Drop the single channel stack of your data, to be segmented by Omnipose, into Omnipose_Analysis folder
3. Open FIJI, start up the macros window, and run the "splitStacks.py" script
4. A window will pop up asking where your data is. Select the Omnipose_Analysis folder
5. When script is done, open the Ominipose_Analysis folder and remove the original stack file. What should be left in the folder is the stack broken up into individual images.

### Running Omnipose
*Now that a stack has been made into a series of image files Omnipose can be run.*

1. Go to environments tab of Anaconda GUI and switch your "omniposeGPU" environment and open a terminal
2. For using pretrained Ominpose models use step 3. For Bisson Lab custom models use step 4 instead. Use either or, not both steps.
3. In the terminal type "omnipose --dir "C:\Users\bisso\Desktop\omniposeAnalysis" --use_gpu --pretrained_model bact_phase_omni --save_outlines --save_txt --in_folders --no_npy --exclude_on_edges". Switch out the directory so that it points to your Omnipose_Analysis folder correctly. Also change the pretrained model name to the appropriate one you want to use. "bact_phase_omni" is the default Omnipose model for segmenting cells in phase channel images. Then hit ENTER. Omnipose will run in the terminal. It will update there as to its progress.
4. If using a custom model type this instead "omnipose --dir "C:\Users\bisso\Desktop\omniposeAnalysis" --use_gpu --pretrained_model "C:\Users\bisso\Desktop\omniposeTrain\cells\crops\models\custom_volcaniiRodDisk" --dim 2 --nclasses 2 --nchan 1 --save_outlines --save_txt --in_folders --no_npy --exclude_on_edges". Switch out the directories so that they point to your Omnipose_Analysis folder and custom model correctly. Then hit ENTER. Omnipose will run in the terminal. It will update there as to its progress.
5. When Omnipose is done it will have stored the segmentation outlines and ROIs as txt files in new folders called 'outlines' and 'txt_outlines'. It also creates a "masks" folder that you can ignore because it is empty.

### Assess Omnipose Results
*Omnipose has saved the masks and the outlines of those masks as images in the Omnipose_Analysis folder when it is done. The segmentation needs to be assessed for quality before moving forward. The next steps will take the outline images and convert them back to a stack for viewing.*

1. Open FIJI, start up the macros window, and run the "imagesToStack.py" script on the "outlines" directory. Make sure you first scroll down to main function and set the "timelapse" variable to 'True' or 'False' accordingly.
2. Save the stack output by imageJ to the 'omniposeAnalysis' folder and assess the segmentation.
3. If all doesn't look good. Rerun Omnipose (from step 3a/3b above) with same command though omit the "--no_npy" argument. This will allow you to load the masks in the omnipose GUI to manually correct for training purposes. (See Training Section Below). If segmentation looks good, continue on.

### Convert Omnipose ROI txt files to binary masks
We now need to convert the '.txt' files Omnipose generated to ROIs usuable by imageJ. Then use the ROIs to make a binary mask where the background is set to 0 (black) and the foreground is set to 255 (white).

1. Open the imageJ macro "generateROIsAndBinaryMasks.py". Make sure you first scroll down to main function and set the "timelapse" and "foci" variables to 'True' or 'False' accordingly.
2. A window will pop up asking for a folder. Selected the 'txt_outlines' folder generated from Omnipose
3. Save the binary mask stack that is output by imageJ. The ROIs are saved as '.zip' files automatically to the 'omniposeAnalysis' folder
4. Now that you have the masks, delete the 'outlines' , 'txt_outlines' and 'masks' folders and all the individual images. You should be left with a stack of the original images, a stack of the binary masks, and the '.zip' files of the ROIs
5. For each additional channel you need segmented by Omnipose, repeat everything above from step 7 of "Pre-omnipose processing of data" onward.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## TRACKING OF CELLS

### Use CellProfiler to track cells over time
*CellProfiler will take the binary masks we generated from Omnipose's segmentation and use that to track our cells using the Linear Assignment Problem (LAP) algorithm.*

1. Run CellProfiler and open the "trackingSingleCells.cpproj" file
2. Drag and drop, the binary mask and raw data into the 'Image' tab
3. Open the 'Metadata' tab and click the 'Extract metadata' button.
4. Open the 'NamesAndTypes' tab and correctly assign each file to the right object/type. By default, it is set up so that your raw data is a two channel image with the word 'data' somewhere in the file name, the GFP binary mask contains 'gfp_binaryMasks' in the filename, and the Phase binary mask contains 'phase_binaryMasks' in the filename.
5. Click 'Update' button and the table should populate your files correctly. If it doesn't make sure you did step 4 correctly.
6. Open the 'SaveImages' tab and make sure the save directory is the 'omniposeAnalysis' folder
7. Open the 'ExportToSpreadsheet' tab and make sure the save directory is the 'omniposeAnalysis' folder
8. Also in the 'ExportToSpreadsheet' tab click the 'Press button to select measurements' button to review what measurements you want to save. Don't bother with 'Cells' data. 'FilterCells' contains all the cellular measurments. Here is a list of what CellProfiler can measure: https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-3.0.0/modules/measurement.html
9. Run the program by hitting the play button. As it runs a window will pop up and update each frame with the outlines of objects it finds on top of the mask we used as input. Make sure this generally looks good.

### Process CellProfiler Data
*CellProfiler refers to cells as "object numbers" in its output but if we track a cell from frame to frame its object number can change especially if*

*1. There is movement of cells in the field of view and &*

*2. There is a high density of cells*

*This is because "Object Numbers" are assigned independently from frame to frame in the order of left to right and top to bottom. Cells are tracked as full lineages in CellProfiler but individual cells/cell cycles (cells-through-time) are not given clear, unique, identifiers. Finally, the tracking results CellProfiler shows you in the GUI comes from the first phase of LAP calculations, this first phase does not include the calculations done that allow for splitting of cells and so the visual tracking that pops up in the GUI is just flat out not correct. These calculations are done and the final output of numbers from CellProfiler includes this second LAP tracking phase, but we have no easy visual representation to asses the quality of the tracking. Running these next scripts will solve these issues.*

*These issues with CellProfiler are documented here:*

*https://forum.image.sc/t/track-objects-lap-2nd-phase-workaround/13081 &*

*https://forum.image.sc/t/trackobjects-lap/14030*

 1. Open "CP_analysis.py" script pointing the directory to the "FilterObjects.csv" that was output from CellProfiler. You also must specify:
  - if the data is from a timelapse (True) or not (False).
  - pixel conversion factor for the objective used
  - the time interval used
  - if a timelapse, the directory and filname of the image you want to draw the tracks on (I suggest the stack of the phase channel only)
  - output file name and directory (I at least suggest the omniposeAnalysis folder)
  - the columns of data you want to take from the 'FilterCells.csv' generated from CellProfiler. There is a bunch of columns that CellProfiler measures that are not necessary for most of our analysis. This is where you can customize the output of the data for your  specific analysis needs. You just need to add the column names from 'FilterCells.csv' here that you want to keep.
 
 
 2. Run the script by pressing the 'play' button
 3. The program will display 'Finished!!!' when done.
 4. For a timelapse, open the tracking '.tif' file that was output and assess the quality of the tracking
 5. If tracking looks good, you can use the output '.csv' file for further graphing of data, where each cell has been given a unique 'Cell ID' number. If tracking isn't great, you may have to play with the tracking parameters in CellProfiler

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
