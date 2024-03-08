#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 17:09:57 2024

This is my same CP_analysis code but with functioning GUI interfaces for easier user input/output management.

Currently the GUI crashes after selecting output data.

@author: johnmallon
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from tqdm import tqdm
from matplotlib.colors import to_hex

def calculateShape(df,pixelConversion):
    """
    CellProfiler makes its measurements with pixel as the unit. This program converts some of the data into the more usable unit of microns based on
    your microscope's camera resolution and objective used.

    This function returns a modified version of the input dataframe with the newly calculated columns
    """
    df['AreaShape_Area_um']= df['AreaShape_Area']*(pixelConversion**2)
    df['Aspect Ratio']= df['AreaShape_MajorAxisLength']/df['AreaShape_MinorAxisLength']
    df['Shape'] = np.where(df['Aspect Ratio'] >= 2, 'rod', 'disk')
    
    return df


def findStartingCells(df):
    """
    Get the cells that start lineages and splits, and start separating the cells. These are cells with a 'TrackObjects_LinkType' of 0 and 2,
    respectively. Only one daughter in a division even gets the 'TrackObjects_LinkType' of 2 so to get the other daughter cell we look for the
    cell that that has a 'TrackObjects_LinkType' of 1 that shares the same parent cell. This function gives of the first frame of all cells-through-time
    and thus we can give them all a unique 'Cell ID' value.

    This function returns a list of the starting cells found and a modified version of the input dataframe where the starting cells have been removed.
    """
    cellID = 1
    cellList = []
    
    lineageStarts = df.loc[(df['TrackObjects_LinkType'] == 0) | (df['TrackObjects_LinkType'] == 2)]
    
    for index,row in lineageStarts.iterrows():
        cell = []
        cell.append([cellID,row])
        cellList.append(cell)
        df = df.drop(index)
        cellID += 1
    for i in tqdm(range(len(cellList))):
        if cellList[i][-1][1]['TrackObjects_LinkType'] == 2:
            splitFrame = cellList[i][-1][1]['ImageNumber']
            splitParent = cellList[i][-1][1]['TrackObjects_ParentObjectNumber']
            otherDaughter = df.loc[(df['ImageNumber']==splitFrame) &
                                       (df['TrackObjects_ParentObjectNumber']==splitParent) & 
                                       (df['TrackObjects_LinkType'] == 1)]
            #for some reason the length of this .loc is sometimes 0, i think its because cells are moving
            for index,row in otherDaughter.iterrows():
                newCell = []
                newCell.append([cellID,row])
                cellList.append(newCell)
                df = df.drop(index)
                cellID += 1
    
 
    return cellList, df


def findNextCell(df,currentCell):
    """
    Now that we have the starting frame for each cell-through-time we can follow that cell frame by frame and connect them by giving all instances
    of that cell-through-time the same Cell ID number. This is done by recursively calling this function until the end of a track is reached.

    This functions returns a a list of lists containing all instances of a single, cell-through-time.
    """
    cellID = currentCell[-1][0]
    currentFrame = currentCell[-1][1]['ImageNumber']
    currentObjectNumber = currentCell[-1][1]['ObjectNumber']
    currentLineage = currentCell[-1][1]['TrackObjects_Label']
    nextCell = df.loc[(df['TrackObjects_ParentImageNumber']==currentFrame) 
                      & (df['TrackObjects_ParentObjectNumber']==currentObjectNumber)
                      & (df['TrackObjects_Label']==currentLineage)]
    if not nextCell.empty:
        for index, row in nextCell.iterrows():
            currentCell.append([cellID,row])
            df = df.drop(index)
        findNextCell(df,currentCell)
        
    return currentCell


def formatData(cellList):
    """
    This function takes the list of lists of lists of all the cells-through-time and converts it into a dataframe.

    This function returns the new dataframe containing all the cells-through-time with their unique 'Cell ID' as a new column
    """
    data = []
    for cell in cellList:
        spots = []
        for spot in cell:
            spot[1]['cell ID'] = spot[0]
            spots.append(spot[1])
        spots = pd.DataFrame(spots)
        data.append(spots)
    data = pd.concat(data)
    
    return data


def findParents(data):
    """
    This function for any given instance of a cell-through-time, finds the parent, or mother, of that instance and records this as a new
    column in the dataframe. It also records the area of the the parent.

    This function returns this updated version of the dataframe.
    """
    parents = []
    parentsArea = []
    for index, row in data.iterrows():
        parentFrame = row['TrackObjects_ParentImageNumber']
        parentObjectNumber = row['TrackObjects_ParentObjectNumber']
        parent = data['cell ID'].loc[(data['ImageNumber']==parentFrame) & (data['ObjectNumber']==parentObjectNumber)]
        parentArea = data['AreaShape_Area_um'].loc[(data['ImageNumber']==parentFrame) & (data['ObjectNumber']==parentObjectNumber)]
        if parent.empty:
            parents.append('NaN')
        else:
            for index, value in parent.items():
                parents.append(value)
        if parentArea.empty:
            parentsArea.append('NaN')
        else:
            for index, value in parentArea.items():
                parentsArea.append(value)
    data['Parent'] = parents
    data['Parent Area'] = parentsArea
    
    return data


def relativeTiming(group):
    """
    This function creates a new column in the dataframe that normalizes the time so that the first instance of all cells-through-time starts
    at zero.

    This function returns this modified version of the dataframe.
    """
    birthTime = group['Time (hr)'].iloc[0]
    group['Relative Time'] = group['Time (hr)'] - birthTime
    
    return group

                 
def randomColoring(group):
    color =  to_hex(tuple(np.random.rand(3)))
    group['randomColor'] = color
    
    return group


def visualizeTracking(data,outputDirectory,trackImageFileName):
    """
    This function takes the X,Y center points of instances of cells-through-time and draws lines between them and displays it on top of the
    original segmentation '.tif' generated from Omnipose. This allows us to visually assess the quality of the tracking done by CellProfiler
    since the second LAP tracking phase is never shown to you while CellProfiler runs.

    This function saves a new '.tif' stack with the tracks visuallized and returns nothing.
    """
    cells = data.groupby('cell ID',group_keys=False)
    data = cells.apply(randomColoring)
    cells = data.groupby('cell ID')
    
    
    im = io.imread(trackImageFileName)
    print(im.shape)
    #frames, heightPixels, widthPixels = im.shape
    frames, heightPixels, widthPixels, channels = im.shape
    dpi = 300
    figSizeInches = (widthPixels / dpi, heightPixels / dpi)
    stackedFrames = []
    plt.show()
    plt.ioff()
    fig, tx = plt.subplots(dpi=dpi,figsize=figSizeInches)
    img = tx.imshow(im[0, :, :], cmap='gray')
    removeLine = False
    line0 = []
    for frame in tqdm(range(im.shape[0])):
        currentFrame = im[frame][:][:]
        img.set_data(currentFrame)
        if removeLine:
            for line in tx.lines:
                line.remove()
            fig.canvas.draw()
        for group, values in cells:
            if frame > 10:
                subDF = values.loc[(values['ImageNumber'] >= frame-3)&
                                   (values['ImageNumber'] <= frame+3)]
            else:
                subDF = values.loc[values['ImageNumber'] <= frame] #get 5 frames of information ahead of current frame
            x = list(subDF['Location_Center_X'])
            y = list(subDF['Location_Center_Y'])
            c = values['randomColor'].iloc[0]
            for i in range(len(x)):
                if i > 0:
                    line0, = tx.plot([x[i-1], x[i]], 
                            [y[i-1], y[i]],
                            color=c,alpha=0.8)
                    removeLine = True

        fig.canvas.draw()  # Draw the figure to update the canvas
        frame = np.array(fig.canvas.renderer.buffer_rgba())[:, :, :3]  # Extract RGB values
        stackedFrames.append(frame)
        plt.close()
    trackingImage = np.stack(stackedFrames)
    io.imsave(outputDirectory+'tracks.tif', trackingImage)
    
   
def relateFociToCells(data,dfFoci):
    cellIDs = []
    for i in tqdm(range(dfFoci.shape[0])):
        frame = dfFoci.iloc[i]['ImageNumber']
        fociParent = dfFoci.iloc[i]['Parent_FilterCells']
        cellID = int(data['cell ID'].loc[(data['ImageNumber']==frame) &
                                       (data['ObjectNumber']==fociParent)])
        cellIDs.append(cellID)
    
    return cellIDs

def select_columns(dataframe):
    columns = list(dataframe.columns)
    selected_columns = []

    def submit_columns():
        for index, var in enumerate(vars):
            if var.get():
                selected_columns.append(columns[index])
        outputSelection.destroy()

    outputSelection = tk.Toplevel()
    outputSelection.title("Select Output Columns")

    vars = []
    num_columns = 3  # Change this to the desired number of columns
    for i, col in enumerate(columns):
        var = tk.BooleanVar()
        chk = tk.Checkbutton(outputSelection, text=col, variable=var)
        row = i // num_columns
        column = i % num_columns
        chk.grid(row=row, column=column, sticky=tk.W)
        vars.append(var)

    submit_button = ttk.Button(outputSelection, text="Submit", command=submit_columns)
    submit_button.grid(row=row+1, columnspan=4)

    outputSelection.mainloop()

    return selected_columns


def analyzeCPData():
    """
    This Program takes output information for Cell Profiler, running Cellpose/Omnipose, and prepares the data to be used for downstream analysis
    and graphing.

    CellProfiler has unique identifiers for lineages but no clear distinction for daughter cells. Half the daughters are given the same 'label' as the
    mother and the other have get unique identifiers. This program uses the time of division calculated during CellProfiler's LAP tracking ('TrackObjects_LinkType')
    to split all cells up within lineages and give them a unique 'Cell ID' number. This allows for easier manipulation of data in our downstream analysis.
    
    Input:
        1. CellProfiler datatable that contains all the single cell information over time. It is by default called 'FilterObjects.csv'

    Output: 
        1. A new '.csv' file containing single cell data along with the unique 'Cell IDs'
        2. A new '.tif' stack that maps the LAP tracking done by CellProfiler onto of the segmentation done by Omnipose.
        3. A graph of Area vs. Time is output for all single cells tracked for you to generally asses if things are working.

    Caveats:
        1. This program does not deal with a value of 3 (mitosis) or 4 (gap in track) from CellProfiler's 'TrackObjects_LinkType'

    """
    
    
    print('\n')
    print('Pixel Conversion: ', pixelConversion)
    print('Input Directory: ', inputDirectory)
    print('Input Cell Filename: ', inputCellFileName)
    print('Timelapse: ', timelapse.get())
    if timelapse.get():
        print('Time Interval (hr): ', timeInterval)
        print('Track Filename: ',trackImageFileName)
    print('Foci: ', foci.get())
    if foci.get():
        print('Input Foci Filename: ',inputFociFileName)
    print('Output Directory: ',outputDirectory)
    
    
    df = pd.read_csv(inputDirectory+inputCellFileName)
    df = df.sort_values(by=['ImageNumber']) #sort all data by 'time'
    df = calculateShape(df,pixelConversion)
    df['Time (hr)'] = (df['ImageNumber']-1)*timeInterval
    initialDataSize = df.shape[0]
    #print(initialDataSize)
    
    print('Finding Cells...')
    if timelapse.get():
        cellList,df = findStartingCells(df)
        print('Found!!!')
    
    if timelapse.get():
        data = []
        print('Stiching Mothers and Daughters Through Time...')
        for i in tqdm(range(len(cellList))):
            stitchedCell = findNextCell(df,cellList[i])
            data.append(stitchedCell)
        print('Formating...')
        data = formatData(data)
        finalDataDize = data.shape[0]
        #print(finalDataDize)
        try:
            if initialDataSize != finalDataDize:
                raise ValueError("Something went wrong with the concatenation of cells!")
            else:
                print('Cells successfully connected through time!!!')
        except ValueError as e:
            print(f"Error: {e}")
   
    
        cells = data.groupby('cell ID',group_keys=False)
        data = cells.apply(relativeTiming)
        data = findParents(data)
        print('Tracking Cells...')
        visualizeTracking(data,outputDirectory,trackImageFileName)
        print('Tracked!!!')
        plt.ion()
        #plot data with time and relative time
        figure, ax = plt.subplots(dpi=300) 
        seaborn.scatterplot(data=data,ax=ax,hue='cell ID',
                   x='Time (hr)',y='AreaShape_Area_um',
                   edgecolor="k",linewidth=0.75,palette=qualitative_colors,
                   zorder=1.0)
        ax.get_legend().set_visible(False)
    else:
        data = df
        ids = list(range(data.shape[0]))
        data['cell ID'] = ids
        print('Found!!!')
        
    if foci.get():
        dfFoci = pd.read_csv(inputFociFileName)
        dfFoci = calculateShape(dfFoci,pixelConversion)
        print('Assigning Foci to Cells...')
        cellIDs = relateFociToCells(data,dfFoci)
        dfFoci['cell ID'] = cellIDs
        print('Assigned!!!')
        
        
        
    data = data.rename(columns={'TrackObjects_Label': 'Lineage'})
    data = data.rename(columns={'AreaShape_Solidity': 'Solidity'})
    data = data.rename(columns={'AreaShape_FormFactor': 'Circularity'})
    
    outputColumnOrder = select_columns(data)
    outputDF = data[outputColumnOrder] 
    outputDF.to_csv(outputDirectory+outputCellFileName, index=False, header=True)
    
    if foci.get():
        outputColumnOrder = select_columns(dfFoci)
        outputDF = dfFoci[outputColumnOrder]
        outputDF = outputDF.sort_values(by=['cell ID'])
        outputDF.to_csv(outputDirectory+outputFociFileName, index=False, header=True)                 
    print('Finished!!!')
    
def open_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)  # Clear previous entry
    entry.insert(0, file_path)  


def select_directory():
    global outputDirectory
    file_path = filedialog.askdirectory()
    var6_entry.delete(0, tk.END)  # Clear previous entry
    var6_entry.insert(0, file_path)  # Insert sele
    outputDirectory = file_path + '/'

def submit_values():
    #Function to handle submission of values
    global pixelConversion,timeInterval,inputFociFileName,trackImageFileName,inputCellFileName, inputDirectory
    
    file_path = str(var1_entry.get())
    file_path = file_path.replace("/" , "~/~")
    pathSplit = file_path.split('~')
    inputCellFileName = pathSplit[-1]
    inputDirectory = pathSplit[:-1]
    inputDirectory = ''.join(inputDirectory)
    
    
    ###must check that these are nubmers
    pixelConversion = var2_entry.get()
    try:
        pixelConversion = int(pixelConversion)  # Convert to integer
    except ValueError:
        try:
            pixelConversion = float(pixelConversion)  # Try converting to float if int conversion fails
        except ValueError:
            # Handle error if the string is not a valid number
            print("Error: Pixel Conversion must be a number")
            return  # Exit the function if conversion fails
    if timelapse.get():
        timeInterval = var3_entry.get()
        try:
            timeInterval = float(timeInterval)  # Convert to float
            timeInterval = timeInterval/60
        except ValueError:
            # Handle error if the string is not a valid number
            print("Error: Time Interval must be a number")
            return  # Exit the function if conversion fails
        trackImageFileName = var4_entry.get()
    if foci.get():
        inputFociFileName = var5_entry.get()
    
        
    
    #Call the main function and pass the entered values to it
    analyzeCPData()
    
  
def toggle_additional_entries(checkbox, *entries):
        state = tk.NORMAL if checkbox.get() else tk.DISABLED
        for entry in entries:
            entry.config(state=state)
    
root = tk.Tk()
root.title("Cell Profiler Analysis Variable Input")

#global variables from user
inputDirectory = ''
inputCellFileName = ''
pixelConversion = 0
timeInterval = 0
timelapse = tk.BooleanVar()
foci = tk.BooleanVar()
outputDirectory = ''

inputFociFileName = ''
trackImageFileName = ''
qualitative_colors = seaborn.color_palette("Set3")
outputCellFileName = 'output_cells.csv'
outputFociFileName = 'output_foci.csv'
    

var1_label = tk.Label(root, text="Input Cellular Data File:")
var1_label.grid(row=0, column=0)
var1_entry = tk.Entry(root)
var1_entry.grid(row=0, column=1)
var1_button = tk.Button(root, text="Select File", command=lambda: open_file(var1_entry))
var1_button.grid(row=0, column=2)

var2_label = tk.Label(root, text="Pixel Conversion Factor:")
var2_label.grid(row=1, column=0)
var2_entry = tk.Entry(root)
var2_entry.grid(row=1, column=1)

checkbox_label_1 = tk.Label(root, text="Timelapse?")
checkbox_label_1.grid(row=2, column=0)
checkbox_1 = tk.Checkbutton(root, text="Yes", variable=timelapse, onvalue=True, offvalue=False,command=lambda: toggle_additional_entries(timelapse, var3_entry,var4_entry))
checkbox_1.grid(row=2, column=1)

var3_label = tk.Label(root, text="Time Interval:")
var3_label.grid(row=3, column=0)
var3_entry = tk.Entry(root, state=tk.DISABLED)
var3_entry.grid(row=3, column=1)

var4_label = tk.Label(root, text="Track file:")
var4_label.grid(row=4, column=0)
var4_entry = tk.Entry(root,state=tk.DISABLED)
var4_entry.grid(row=4, column=1)
var4_button = tk.Button(root, text="Select File", command=lambda: open_file(var4_entry))
var4_button.grid(row=4, column=2)

checkbox_label_2 = tk.Label(root, text="Foci?")
checkbox_label_2.grid(row=5, column=0)
checkbox_2 = tk.Checkbutton(root, text="Yes", variable=foci, onvalue=True, offvalue=False,command=lambda: toggle_additional_entries(foci, var5_entry))
checkbox_2.grid(row=5, column=1)

var5_label = tk.Label(root, text="Input Foci Data File:")
var5_label.grid(row=6, column=0)
var5_entry = tk.Entry(root,state=tk.DISABLED)
var5_entry.grid(row=6, column=1)
var5_button = tk.Button(root, text="Select File", command=lambda: open_file(var5_entry))
var5_button.grid(row=6, column=2)

var6_label = tk.Label(root, text="Output Directory:")
var6_label.grid(row=7, column=0)
var6_entry = tk.Entry(root)
var6_entry.grid(row=7, column=1)
var6_button = tk.Button(root, text="Select Output Directory", command=select_directory)
var6_button.grid(row=7, column=2)


submit_button = tk.Button(root, text="Run", command=submit_values)
submit_button.grid(row=8, columnspan=4)

root.mainloop()  

 