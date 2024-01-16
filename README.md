# Omnipose_Cellprofiler-Pipeline

For segmenting and tracking single cells during growth under a microscope. This pipeline uses Omnipose (https://github.com/kevinjohncutler/omnipose) to segment cells and Cellprofiler (https://github.com/CellProfiler) to track them. The Bisson Lab installs and uses omnipose through the use of Anaconda (https://www.anaconda.com/)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Installations:

--INSTALLATION OF OMNIPOSE-- 
For in-depth instructions refer to https://github.com/kevinjohncutler/omnipose

The instructions below were used to install Omnipose on our lab computer to run using the GPU. Our lab computer runs "Windows 11 Home Edition" with a 64-bit processor. Our GPU is a NVIDIA GeForce RTX 4090.

1. Go to environments tab of Anaconda GUI and open a terminal in your "Base environment"
2. In terminal type "conda create -n omniposeGPU 'python==3.10.12' pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia" then hit ENTER
3. In terminal type "conda activate omniposeGPU" then hit ENTER
4. In terminal type "pip install omnipose" then hit ENTER
5. In terminal type "pip install natsort" then hit ENTER
6. In terminal type "conda remove pytroch-cuda" then hit ENTER
7. In terminal type "conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia" then hit ENTER

--INSTALLATION OF CELLPROFILER--
CellProfiler was installed using the default instructions from their website (cellprofiler.org)

--INSTALLATION OF LabelsToROIs--
LabelsToROIs is a imageJ FIJI macro installed using its default instructions (https://labelstorois.github.io)

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--SEGMENTATION OF CELLS--
"""
Pre-omnipose processing of data:

Omnipose doesn't work on stacks of images so all timelapse stacks have to be made into folders contains each frame as a separate '.tif' file. The "splitStacks.py" script will do this for us.
"""
1. Create a folder and call it "Omnipose_Analysis"
2. Drop a timelapse file into Omnipose_Analysis folder
3. Open FIJI, start up the macros window, and run the "splitStacks.py" script
4. A window will pop up asking where your data is. Select the Omnipose_Analysis folder
5. When script is done, open the Ominipose_Analysis folder and remove the original timelapse file. Would should be left in the folder is the stack broken up into individual images for each frame

"""
Running Omnipose:

Now that a stack has been made into a series of image files Omnipose can be run.
"""
1. Go to environments tab of Anaconda GUI and switch your "omniposeGPU" environment and open a terminal
2. In the terminal type "omnipose --dir "C:\Users\bisso\Desktop\Halofilin Small Sample\john\Omnipose_Analysis" --use_gpu --pretrained_model bact_phase_omni --save_outlines --save_tif --in_folders". Switch out the directory so that it points to your Omnipose_Analysis folder correctly. Then hit ENTER. Omnipose will run in the terminal. It will update there as to its progress.

"""
Assess Omnipose Results:

Omnipose has saved the masks and the outlines of those masks as images in the Omnipose_Analysis folder when it is done. The segmentation needs to be assessed for quality before moving forward. The next steps will take the outline images and convert them back to a stack for viewing.
"""
1. Open FIJI, start up the macros window, and run the "omniposeTo.py" script
2. 



7. If not needed for generating a training set, delete all of the generated _seg.npy files. These files take up a huge amount of storage space and are unnecessary for analysis.
8. Run "_label.py" script
9. Open plugin "LabelToRoi" and run multiple image button with an erode by 1 pixel
10. run fiji macro "omniposeToMask.py"
11. Save the output as a stack
12. run cell profiler 
