# Omnipose_Cellprofiler-Pipeline
For segmenting and tracking single cells during growth under a microscope



--Installation--
conda create -n omnipose 'python==3.10.12' pytorch torchvision pytorch-cuda=11.8 -c pytorch -c nvidia
conda activate omnipose
pip install omnipose
pip install natsort
conda remove pytroch-cuda
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia


ADD LABEL TO roi INSTALL

--Segment with default Omnipose model--

omnipose --dir "C:\Users\bisso\Desktop\Halofilin Small Sample\john\omnipose\HalAKODivision_fullField_3" --use_gpu --pretrained_model bact_phase_omni --save_outlines --save_tif --in_folders



1. Throw timelapse into ominpose folder
2. Run imageJ macro "splitStacks.py" -->select folder with timelapse in it
3. remove stack from the folder of images 
4. open terminal in omniposeGPU anaconda environment
5. copy command above and switch out the directory for appropriate one
6. If not needed for generating a training set, delete all of the generated _seg.npy files. These files take up a huge amount of storage space and are unnecessary for analysis.
7. Run "_label.py" script
8. Open plugin "LabelToRoi" and run multiple image button with an erode by 1 pixel
9. run fiji macro "omniposeToMask.py"
10. Save the output as a stack
11. run cell profiler 
