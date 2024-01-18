"""
Created on Wed Oct  4 13:03:06 2023

@author: johnmallon

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
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from tqdm import tqdm

def calculateShape(df,pixelConversion):
    """
    CellProfiler makes its measurements with pixel as the unit. This program converts some of the data into the more usable unit of microns based on
    your microscope's camera resolution and objective used.

    This function returns a modified version of the input dataframe with the newly calculated columns
    """
    df['AreaShape_Area_um']= df['AreaShape_Area']*(pixelConversion**2)
    df['Circularity']= 1/df['AreaShape_Compactness'] #circularity is the reciprocal of compactness
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
    cellsToRemove = []
    count = 0
    
    lineageStarts = df.loc[(df['TrackObjects_LinkType'] == 0) | (df['TrackObjects_LinkType'] == 2)]
    for index,row in lineageStarts.iterrows():
        cell = []
        cell.append([cellID,row])
        cellList.append(cell)
        cellsToRemove.append(index)
        cellID += 1
    for cell in cellList:
        if cell[-1][1]['TrackObjects_LinkType'] == 2:
            splitFrame = cell[-1][1]['ImageNumber']
            splitParent = cell[-1][1]['TrackObjects_ParentObjectNumber']
            otherDaughter = df.loc[(df['ImageNumber']==splitFrame) &
                                       (df['TrackObjects_ParentObjectNumber']==splitParent) & 
                                       (df['TrackObjects_LinkType'] == 1)]
            #for some reason the length of this .loc is sometimes 0, i think its because cells are moving
            for index,row in otherDaughter.iterrows():
                cell = []
                cell.append([cellID,row])
                cellList.append(cell)
                cellsToRemove.append(index)
                cellID += 1
    df = df.drop(cellsToRemove)
    
    return cellList, df


def findNextCell(df,currentCell):
    """
    Now that we have the starting frame for each cell-through-time we can follow that cell frame by frame and connect them by giving all instances
    of that cell-through-time the same Cell ID number. This is done by recursively calling this function until the end of a track is reached.

    This functions returns a a list of lists containing all instances of a single, cell-through-time.
    """
    cellsToRemove = []
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
            cellsToRemove.append(index)
        df = df.drop(cellsToRemove)
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
            for index, value in parent.iteritems():
                parents.append(value)
        if parentArea.empty:
            parentsArea.append('NaN')
        else:
            for index, value in parentArea.iteritems():
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
                 

def visualizeTracking(data,outputDirectory):
    """
    This function takes the X,Y center points of instances of cells-through-time and draws lines between them and displays it on top of the
    original segmentation '.tif' generated from Omnipose. This allows us to visually assess the quality of the tracking done by CellProfiler
    since the second LAP tracking phase is never shown to you while CellProfiler runs.

    This function saves a new '.tif' stack with the tracks visuallized and returns nothing.
    """
    ###I think i have to group by cell ID####
    data['randomColor'] = data.groupby('TrackObjects_Label').apply(lambda x: np.random.rand(3,)).reset_index(level=0, drop=True)
    data['randomColor'].fillna('gray', inplace=True)
    cells = data.groupby('cell ID')
    im = io.imread('/Users/johnmallon/Downloads/131Frames.tif')
    heightPixels, widthPixels, channels = image.shape
    dpi = 300
    figSizeInches = (width_pixels / dpi, height_pixels / dpi)
    stackedFrames = []
    plt.show()
    plt.ioff()
    fig, tx = plt.subplots(dpi=dpi,figsize=figSizeInches)
    img = tx.imshow(im[0, :, :], cmap='gray')
    
    print('Tracking Cells...')
    for frame in tqdm(range(im.shape[0])):
        currentFrame = im[frame][:][:]
        img.set_data(currentFrame)
        tx.lines.clear()
        for group, values in cells:
            if frame > 10:
                subDF = values.loc[(values['ImageNumber'] >= frame-3)&
                                   (values['ImageNumber'] <= frame+3)]
            else:
                subDF = values.loc[values['ImageNumber'] <= frame+3] #get 5 frames of information ahead of current frame
            x = list(subDF['Location_Center_X'].iloc[-5:])
            y = list(subDF['Location_Center_Y'].iloc[-5:])
            for i in range(len(x)):
                if i > 0:
                    tx.plot([x[i-1], x[i]], 
                            [y[i-1], y[i]],
                            color='cyan',alpha=0.4)  

        fig.canvas.draw()  # Draw the figure to update the canvas
        frame = np.array(fig.canvas.renderer.buffer_rgba())[:, :, :3]  # Extract RGB values
        stackedFrames.append(frame)
        plt.close()
    print('\nSAVING IMAGE...')
    trackingImage = np.stack(stackedFrames)
    io.imsave(outputDirectory+'tracks.tif', trackingImage)
    
def main():
    #####################################################
    ####### USER INPUT INFORMATION START HERE ###########
    inputDirectory = '/Users/johnmallon/Downloads/'
    inputFileName = "FilterObjects.csv"
    qualitative_colors = seaborn.color_palette("Set3")
    pixelConversion = 0.065  # Pixel conversion to um for a 100X objective using Bisson Lab Microscope (Tupan)
    timeInterval = 15/60  #in hours
    outputDirectory = '/Users/johnmallon/Downloads/'
    outputFileName = 'cellsThroughTime.csv'
    outputColumnOrder = ['Lineage','cell ID','Location_Center_X','Location_Center_Y','Shape',
                         'ImageNumber','Time (hr)','Relative Time','Area','Aspect Ratio',
                         'Circularity','Solidity','Parent','Parent Area']
    ####### USER INPUT INFORMATION END HERE #############
    #####################################################
    
    df = pd.read_csv(inputDirectory+inputFileName)
    df = df.sort_values(by=['ImageNumber']) #sort all data by 'time'
    df = calculateShape(df,pixelConversion)
    df['Time (hr)'] = (df['ImageNumber']-1)*timeInterval
    initialDataSize = df.shape[0]
    
    cellList,df = findStartingCells(df)
    data = []
    for cell in cellList:
        stitchedCell = findNextCell(df,cell)
        data.append(stitchedCell)
    data = formatData(data)
    finalDataDize = data.shape[0]
    try:
        if initialDataSize != finalDataDize:
            raise ValueError("Something went wrong with the concatenation of cells!")
        else:
            print('Cells successfully connected through time!')
    except ValueError as e:
        print(f"Error: {e}")
    
    cells = data.groupby('cell ID',group_keys=False)
    data = cells.apply(relativeTiming)
    data = findParents(data)
    visualizeTracking(data,outputDirectory)

     #plot data with time and relative time
    figure, ax = plt.subplots(dpi=300) 
    seaborn.scatterplot(data=data,ax=ax,hue='cell ID',
                   x='Time (hr)',y='AreaShape_Area_um',
                   edgecolor="k",linewidth=0.75,palette=qualitative_colors,
                   zorder=1.0)
    ax.get_legend().set_visible(False)
    
    data = data.rename(columns={'TrackObjects_Label': 'Lineage'})
    data = data.rename(columns={'AreaShape_Area_um': 'Area'})
    data = data.rename(columns={'AreaShape_Solidity': 'Solidity'})
    outputDF = data[outputColumnOrder] 
    outputDF.to_csv(outputDirectory+outputFileName, index=False, header=True)                


main()
