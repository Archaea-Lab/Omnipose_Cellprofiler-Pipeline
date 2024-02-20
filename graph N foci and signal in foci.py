# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 18:26:20 2024

@author: jmall
"""


import matplotlib.pyplot as plt
import seaborn
import pandas as pd


inputDirectory = '/Users/johnmallon/Downloads/CP test for foci/'
inputFileName = 'cellsThroughTime.csv'
df = pd.read_csv(inputDirectory+inputFileName)

df = df.loc[df['cell ID']==2]

#% F in foci
df['% F in Foci'] = df['Intensity_IntegratedIntensity_foci']/(df['Intensity_IntegratedIntensity_foci']+df['Intensity_IntegratedIntensity_GFPinCells'])*100

figure, ax = plt.subplots(dpi=300) 
seaborn.scatterplot(data=df,ax=ax,
               x='Time (hr)',y='% F in Foci',
               edgecolor="k",linewidth=0.75,
               zorder=1.0)



#foci count
figure, bx = plt.subplots(dpi=300)
seaborn.scatterplot(data=df,ax=bx,
               x='Time (hr)',y='Children_foci_Count',
               edgecolor="k",linewidth=0.75,
               zorder=1.0)
cx = bx.twinx()
seaborn.lineplot(data=df,ax=cx,
               x='Time (hr)',y='Area',
               zorder=1.0)



#foci count
figure, dx = plt.subplots(dpi=300)
seaborn.scatterplot(data=df,ax=dx,
               x='Time (hr)',y='% F in Foci',
               edgecolor="k",linewidth=0.75,
               zorder=1.0)
ex = dx.twinx()
seaborn.lineplot(data=df,ax=ex,
               x='Time (hr)',y='Area',
               zorder=1.0)


