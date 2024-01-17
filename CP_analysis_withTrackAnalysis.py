"""
Created on Wed Oct  4 13:03:06 2023

@author: johnmallon

This Program takes output information for Cell Profiler, running Cellpose, and graphs the information.

Specifically, its graphs:
    
1.area of time
2.circularity over time, for rods and disks separetly

"""
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
import numpy as np
from skimage import io
from tqdm import tqdm

def calculateShape(df,pixelConversion):
    #calculate shape parameters
    #convert pixels to um
    df['AreaShape_Area_um']= df['AreaShape_Area']*(pixelConversion**2)
    
    #calculate circularity, this is the reciprocal of the measurement "compactness" that cell profiler makes 
    df['Circularity']= 1/df['AreaShape_Compactness']
    
    #calculate Aspect Ratio, and asign rod vs. disk
    df['Aspect Ratio']= df['AreaShape_MajorAxisLength']/df['AreaShape_MinorAxisLength']
    df['Shape'] = np.where(df['Aspect Ratio'] >= 2, 'rod', 'disk')
    
    return df


def findStartingCells(df):
    cellID = 1
    cellList = []
    cellsToRemove = []
    count = 0
    
    #get the cells that start lineages and splits, and start separate the cells
    #these cells have a LinkType == 0 and 2 repectively
    lineageStarts = df.loc[(df['TrackObjects_LinkType'] == 0) | (df['TrackObjects_LinkType'] == 2)]
    
    for index,row in lineageStarts.iterrows():
        cell = []
        cell.append([cellID,row])
        cellList.append(cell)
        cellsToRemove.append(index)
        cellID += 1
    #get the cells that are the other half of the splits (linkType of 2), 
    #these have a LinkType of 1 but are associated with the splits by being in the same frame AND haveing the same parent
    #print(count) the amount of 0's and 2's were correctly found
    for cell in cellList:
        if cell[-1][1]['TrackObjects_LinkType'] == 2:
            splitFrame = cell[-1][1]['ImageNumber']
            splitParent = cell[-1][1]['TrackObjects_ParentObjectNumber']
            otherDaughter = df.loc[(df['ImageNumber']==splitFrame) &
                                       (df['TrackObjects_ParentObjectNumber']==splitParent) & 
                                       (df['TrackObjects_LinkType'] == 1)]  #do i deal with linktypes of 3 (mitosis) or 4 (orphans/gaps)?
            #for some reason the length of this .loc is sometimes 0, i think its because cells are moving
            
            for index,row in otherDaughter.iterrows():
                cell = []
                cell.append([cellID,row])
                cellList.append(cell)
                cellsToRemove.append(index)
                cellID += 1
    df = df.drop(cellsToRemove)
    return cellID, cellList, cellsToRemove, df


def findNextCell(df,currentCell):
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
    return parents,parentsArea


def relativeTiming(group):
    birthTime = group['Time (hr)'].iloc[0]
    group['Relative Time'] = group['Time (hr)'] - birthTime
    return group
                 

def main():
    ###############################################
    ####### USER INPUT INFORMATION START HERE ###########
    
    
    #directory = R"C:\Users\bisso\Desktop\H26FullField4\\"
    directory = '/Users/johnmallon/Downloads/'
    file = "FilterObjects.csv"
    #set colors for graphs
    qualitative_colors = seaborn.color_palette("Set3")
    pixelConversion = 0.065  #Tupan's pixel conversion to um for the 100X objective
    timeInterval = 15/60  #in hours
    outputFileName = 'test.csv'
    outputColumnOrder = ['Lineage','cell ID','Location_Center_X','Location_Center_Y','Shape',
                         'ImageNumber','Time (hr)','Relative Time','Area','Aspect Ratio',
                         'Circularity','Solidity','Parent','Parent Area']

    ####### USER INPUT INFORMATION END HERE ###########
    ##############################################
    
    
    df = pd.read_csv(directory+file)
    df = df.sort_values(by=['ImageNumber']) #sort all data by 'time'
    df = calculateShape(df,pixelConversion)
    df['Time (hr)'] = (df['ImageNumber']-1)*timeInterval
    print(df.shape[0])
 
    
    cellID,cellList,cellsToRemove,df = findStartingCells(df)
    data = []
    for cell in cellList:
        stitchedCell = findNextCell(df,cell)
        data.append(stitchedCell)
    
    
    data = formatData(data)
    print(data.shape[0])
    
    
    cells = data.groupby('cell ID',group_keys=False)
    data = cells.apply(relativeTiming)
    
    
    #plot data with time and relative time
    figure, ax = plt.subplots(dpi=300) 
    seaborn.scatterplot(data=data,ax=ax,hue='cell ID',
                   x='Time (hr)',y='AreaShape_Area_um',
                   edgecolor="k",linewidth=0.75,palette=qualitative_colors,
                   zorder=1.0)
    ax.get_legend().set_visible(False)
 
    
    parents,parentsArea = findParents(data)
    data['Parent'] = parents
    data['Parent Area'] = parentsArea
    
    
    


    #Calculate figure size in inches
    width_pixels = 2048 #size of image when opened in FIJI
    height_pixels = 2044 
    dpi = 300
    fig_size_inches = (width_pixels / dpi, height_pixels / dpi)
    
    
    
    ###I think i have to group by cell ID####
    data['randomColor'] = data.groupby('TrackObjects_Label').apply(lambda x: np.random.rand(3,)).reset_index(level=0, drop=True)
    data['randomColor'].fillna('gray', inplace=True)
    cells = data.groupby('cell ID')

 
    
    im = io.imread('/Users/johnmallon/Downloads/131Frames.tif')
    stackedFrames = []
    plt.show()
    plt.ioff()
    fig, tx = plt.subplots(dpi=dpi,figsize=fig_size_inches)
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
    #io.imsave('/Users/johnmallon/Downloads/tracks.tif', trackingImage)
    #select data to output
    data = data.rename(columns={'TrackObjects_Label': 'Lineage'})
    data = data.rename(columns={'AreaShape_Area_um': 'Area'})
    data = data.rename(columns={'AreaShape_Solidity': 'Solidity'})
    outputDF = data[outputColumnOrder] 
    #outputDF.to_csv(directory+outputFileName, index=False, header=True)     
           
        
main()