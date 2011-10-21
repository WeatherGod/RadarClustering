#!/usr/bin/env python

from optparse import OptionParser	# Command-line parsing

from ClusterFileUtils import *		# for GetClustDataSource(),
                                    # LoadClustFile(),
                                    # GetClusterSizeInfo()

import matplotlib
matplotlib.use('agg')

from ClusterMap import *		    # for ClusterMap()
#from LoadRastRadar import *		# for LoadRastRadar()
from BRadar.io import LoadRastRadar

#from RadarPlotUtils import *		# for MakeReflectPPI(),
#                                    # TightBounds(),
#                                    # PlotMapLayers()
from mpl_toolkits.axes_grid1 import AxesGrid
from mpl_toolkits.basemap import Basemap
from BRadar.maputils import PlotMapLayers, mapLayers
from BRadar.plotutils import MakeReflectPPI, TightBounds, MakeReflectColorbar
import matplotlib.pyplot as plt
import numpy as np

from glob import glob	# for filename globbing
import os		# for os.path.split(),
                # os.path.splitext(), os.makedirs(),
                # os.path.exists()
import datetime

def ConsistentDomain(fileList, filepath) :
    minLat = None
    minLon = None
    maxLat = None
    maxLon = None

    for filename in fileList :
        dataSource = GetClustDataSource(filename)
        rastData = LoadRastRadar(os.path.join(filepath,
                                              dataSource))
        (lons, lats) = np.meshgrid(rastData['lons'],
                                   rastData['lats'])
        bounds = TightBounds(lons, lats,
                             np.squeeze(rastData['vals']))

        if minLat is not None :
            minLat = min(bounds['minLat'], minLat)
            minLon = min(bounds['minLon'], minLon)
            maxLat = max(bounds['maxLat'], maxLat)
            maxLon = max(bounds['maxLon'], maxLon)
        else :
            minLat = bounds['minLat']
            minLon = bounds['minLon']
            maxLat = bounds['maxLat']
            maxLon = bounds['maxLon']

    return (minLat, minLon, maxLat, maxLon)


if __name__ == '__main__' :
    parser = OptionParser()
    parser.add_option("-r", "--run", dest="runName",
              help="Generate cluster images for RUNNAME",
              metavar="RUNNAME")
    parser.add_option("-p", "--path", dest="pathName",
              help="PATHNAME for cluster files and radar data",
              metavar="PATHNAME", default='.')

    (options, args) = parser.parse_args()

    if options.runName is None :
        parser.error("Missing RUNNAME")

    print "The runName:", options.runName

    fileList = glob(os.path.join(options.pathName, 'ClustInfo',
                                 options.runName, '*.nc'))
    if len(fileList) == 0 :
         print "WARNING: No files found for run '%s'!" % \
                                                options.runName
    fileList.sort()

        # PARRun: [-101, -97], [35, 38.5]
        # AMS_TimeSeries: [-98.5, -93.5], [35.5, 40]
        # AMS_Params: [-100.0, -96.0], [38.0, 40.0]

    #(minLat, minLon, maxLat, maxLon) = (38.0, -100.0, 40.0, -96.0)
    #(minLat, minLon, maxLat, maxLon) = (35.5, -98.5, 40.0, -93.5)

    # Getting a consistent domain over series of images
    minLat, minLon, maxLat, maxLon = ConsistentDomain(fileList,
                                                 options.pathName)

    # Map domain
    map = Basemap(projection='cyl', resolution='i',
                  suppress_ticks=False,
                  llcrnrlat=minLat, llcrnrlon=minLon,
                  urcrnrlat=maxLat, urcrnrlon=maxLon)

    print minLat, minLon, maxLat, maxLon

    # Looping over all of the desired cluster files

    ppiPath = os.path.join('PPI', options.runName)
    for filename in fileList :
        (pathname, nameStem) = os.path.split(filename)
        (nameStem, nameExt) = os.path.splitext(nameStem)
        outfile = os.path.join(ppiPath, nameStem + '_clust.png')

        if os.path.exists(outfile) :
            continue

        fig = plt.figure()
        grid = AxesGrid(fig, 111,
            nrows_ncols=(1, 1),
            axes_pad=0.22,
            cbar_mode='single',
            cbar_pad=0.05, cbar_size=0.08)
        ax = grid[0]
        PlotMapLayers(map, mapLayers, ax)
        
        (clustParams, clusters) = LoadClustFile(filename)
        rastData = LoadRastRadar(os.path.join(options.pathName,
                                       clustParams['dataSource']))
        #print type(rastData['vals'])
        #rastData['vals'][rastData['vals'] < 0.0] = np.nan

        # Plotting the full reflectivity image, with significant transparency (alpha=0.25).
        # This plot will get 'dimmed' by the later ClusterMap().
        # zorder=1 so that it is above the Map Layers.
    #    MakeReflectPPI(np.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
    #		   alpha=0.15, axis=ax, zorder=1, titlestr=rastData['title'], colorbar=False, axis_labels=False)
            
        clustCnt, clustSizes, sortedIndices = GetClusterSizeInfo(clusters)

        ClusterMap(clusters, np.squeeze(rastData['vals']),
                   sortedIndices,
        #len(pylab.find(clustSizes >= (avgSize + 0.25*stdSize)))],
                   radarBG_alpha=0.75, zorder=1.0, axis=ax)

        ax.set_title(datetime.datetime.utcfromtimestamp(
            rastData['scan_time']).strftime('%Y/%m/%d  %H:%M:%S'))
        ax.set_xlabel('Longitude (deg)')
        ax.set_ylabel('Latitude (deg)')

        MakeReflectColorbar(grid.cbar_axes[0])

        if not os.path.exists(ppiPath) :
            os.makedirs(ppiPath)

        fig.savefig(outfile)
        fig.clf()
        del fig

