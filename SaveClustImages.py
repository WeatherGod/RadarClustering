#!/usr/bin/env python

from optparse import OptionParser	# Command-line parsing

from ClusterFileUtils import *		# for GetClustDataSource(), LoadClustFile(), GetClusterSizeInfo()

from ClusterMap import *		# for ClusterMap()
from LoadRastRadar import *		# for LoadRastRadar()

from RadarPlotUtils import *		# for MakeReflectPPI(), TightBounds(), PlotMapLayers()

from mpl_toolkits.basemap import Basemap
import pylab
import numpy

import glob		# for filename globbing
import os		# for os.sep.join(), os.path.split(), os.path.splitext(), os.mkdir()




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

if (options.runName == None) :
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
mapLayers = [['states', {'linewidth':1.5, 'color':'k', 'zorder':0}], 
	     ['counties', {'linewidth':0.5, 'color':'k', 'zorder':0}],
	     ['rivers', {'linewidth':0.5, 'color':'b', 'zorder':0}],
	     ['roads', {'linewidth':0.75, 'color':'r', 'zorder':0}]]


# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=False,
				llcrnrlat = minLat, llcrnrlon = minLon,
				urcrnrlat = maxLat, urcrnrlon = maxLon)

print minLat, minLon, maxLat, maxLon

# Looping over all of the desired cluster files

for filename in fileList :
    (pathname, nameStem) = os.path.split(filename)
    (nameStem, nameExt) = os.path.splitext(nameStem)
    
    PlotMapLayers(map, mapLayers)

    pylab.hold(True)
    
    (clustParams, clusters) = LoadClustFile(filename)
    rastData = LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))

    # Plotting the full reflectivity image, with significant transparency (alpha=0.25).
    # This plot will get 'dimmed' by the later ClusterMap().
    # zorder=1 so that it is above the Map Layers.
    MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
		   alpha=0.25, drawer=map, zorder=1, titlestr=rastData['title'], colorbar=False, axis_labels=False)
    pylab.hold(True)
    
    (clustCnt, clustSizes, sortedIndicies) = GetClusterSizeInfo(clusters)

    ClusterMap(clusters,pylab.squeeze(rastData['vals']), sortedIndicies,#len(pylab.find(clustSizes >= (avgSize + 0.25*stdSize)))],
	       drawer=map)
    pylab.hold(False)

    # TODO: May be able to update this with os.path.exists() or something like that...
    if (not os.access(os.sep.join(['PPI', options.runName]), os.F_OK)) :
    	os.mkdir(os.sep.join(['PPI', options.runName]))

    outfile = os.sep.join(['PPI', options.runName, nameStem + '_clust.png'])
    pylab.savefig(outfile)
    pylab.clf()




