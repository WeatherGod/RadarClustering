#!/usr/bin/env python

from optparse import OptionParser	# Command-line parsing

from ClusterFileUtils import *		# for GetClustDataSource(), LoadClustFile(), GetClusterSizeInfo()

from ClusterMap import *		# for ClusterMap()
from LoadRastRadar import *		# for LoadRastRadar()

from RadarPlotUtils import *		# for MakeReflectPPI(), TightBounds(), PlotMapLayers()

from mpl_toolkits.basemap import Basemap
import MapUtils
import matplotlib.pyplot as pyplot
import numpy

import glob		# for filename globbing
import os		# for os.sep.join(), os.path.split(), os.path.splitext(), os.makedirs(), os.path.exists()




def ConsistentDomain(fileList, filepath) :
    minLat = None
    minLon = None
    maxLat = None
    maxLon = None

    for filename in fileList :
        dataSource = GetClustDataSource(filename)
        rastData = LoadRastRadar(os.sep.join([filepath, dataSource]))
        (lons, lats) = pylab.meshgrid(rastData['lons'], rastData['lats'])
        bounds = TightBounds(lons, lats, pylab.squeeze(rastData['vals']))

        if (minLat != None) :
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








parser = OptionParser()
parser.add_option("-r", "--run", dest="runName",
		  help="Generate cluster images for RUNNAME", metavar="RUNNAME")
parser.add_option("-p", "--path", dest="pathName",
		  help="PATHNAME for cluster files and radar data", metavar="PATHNAME", default='.')


(options, args) = parser.parse_args()

if (options.runName is None) :
    parser.error("Missing RUNNAME")



print "The runName:", options.runName


fileList = glob.glob(os.sep.join([options.pathName, 'ClustInfo', options.runName, '*.nc']))
if (len(fileList) == 0) : print "WARNING: No files found for run '" + options.runName + "'!"
fileList.sort()

    # PARRun: [-101, -97], [35, 38.5]
    # AMS_TimeSeries: [-98.5, -93.5], [35.5, 40]
    # AMS_Params: [-100.0, -96.0], [38.0, 40.0]

#(minLat, minLon, maxLat, maxLon) = (38.0, -100.0, 40.0, -96.0)
#(minLat, minLon, maxLat, maxLon) = (35.5, -98.5, 40.0, -93.5)

# Getting a consistent domain over series of images
(minLat, minLon, maxLat, maxLon) = ConsistentDomain(fileList, options.pathName)


# Map display options
mapLayers = MapUtils.mapLayers


# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=False,
				llcrnrlat = minLat, llcrnrlon = minLon,
				urcrnrlat = maxLat, urcrnrlon = maxLon)

print minLat, minLon, maxLat, maxLon

# Looping over all of the desired cluster files

for filename in fileList :
    (pathname, nameStem) = os.path.split(filename)
    (nameStem, nameExt) = os.path.splitext(nameStem)
    fig = pyplot.figure()
    ax = fig.gca()
    MapUtils.PlotMapLayers(map, mapLayers, ax)
    
    (clustParams, clusters) = LoadClustFile(filename)
    rastData = LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))
    rastData['vals'][rastData['vals'] < 0.0] = numpy.nan

    # Plotting the full reflectivity image, with significant transparency (alpha=0.25).
    # This plot will get 'dimmed' by the later ClusterMap().
    # zorder=1 so that it is above the Map Layers.
#    MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
#		   alpha=0.15, axis=ax, zorder=1, titlestr=rastData['title'], colorbar=False, axis_labels=False)
        
    (clustCnt, clustSizes, sortedIndicies) = GetClusterSizeInfo(clusters)

    ClusterMap(clusters,pylab.squeeze(rastData['vals']), sortedIndicies,#len(pylab.find(clustSizes >= (avgSize + 0.25*stdSize)))],
	       radarBG_alpha=0.15, zorder = 1.0, axis=ax)
    
    if (not os.path.exists(os.sep.join(['PPI', options.runName]))) :
        os.makedirs(os.sep.join(['PPI', options.runName]))

    outfile = os.sep.join(['PPI', options.runName, nameStem + '_clust.png'])
    fig.savefig(outfile)
    fig.clf()
    del fig




