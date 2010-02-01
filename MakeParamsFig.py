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
import os		# for os.sep.join(), os.path.split(), os.path.splitext(), os.makedirs(), os.path.exists()




parser = OptionParser()
parser.add_option("-r", "--run", dest="runName",
		  help="Generate cluster images for RUNNAME", metavar="RUNNAME")
parser.add_option("-p", "--path", dest="pathName",
		  help="PATHNAME for cluster files and radar data", metavar="PATHNAME", default='.')
parser.add_option("-t", "--test", dest="isTest", action="store_true",
                  help="If set, files will be saved in current directory as 'tempy*.png'", default=False)

(options, args) = parser.parse_args()

if (options.runName == None) :
    parser.error("Missing RUNNAME")



print "The runName:", options.runName

optionParams = {}
optionParams['WSR'] = {'runName': 'Test_WSR_Params',
			   'domain': (38.0, -100.0, 40.0, -96.0),
			   'destNameStem': '../../Documents/SPA/WSR_Demo%d'}

optionParams['NWRT'] = {'runName': 'Test_NWRT_Params',
                        'domain': (35.5, -100.0, 37.0, -97.0),
                        'destNameStem': '../../Documents/SPA/NWRT_Demo%d'}


fileList = glob.glob(os.sep.join([options.pathName, 'ClustInfo', optionParams[options.runName]['runName'], '*.nc']))
if (len(fileList) == 0) : print "WARNING: No files found for run '" + options.runName + "'!"
fileList.sort()

if options.isTest :
   optionParams[options.runName]['destNameStem'] = 'tempyDemo%d'

# AMS_Params: [-100.0, -96.0], [38.0, 40.0]
(minLat, minLon, maxLat, maxLon) = optionParams[options.runName]['domain']



# Map display options
mapLayers = [['states', {'linewidth':1.5, 'color':'k', 'zorder':0}], 
	     ['counties', {'linewidth':0.5, 'color':'k', 'zorder':0}],
	     ['rivers', {'linewidth':0.5, 'color':'b', 'zorder':0}],
	     ['roads', {'linewidth':0.75, 'color':'r', 'zorder':0}]]


# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=True,
				llcrnrlat = minLat, llcrnrlon = minLon,
				urcrnrlat = maxLat, urcrnrlon = maxLon)

print minLat, minLon, maxLat, maxLon
# Looping over all of the desired cluster files


for (figIndex, filename) in enumerate(fileList):
    (pathname, nameStem) = os.path.split(filename)

    PlotMapLayers(map, mapLayers)

    (clustParams, clusters) = LoadClustFile(filename)
    rastData = LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))
    rastData['vals'][rastData['vals'] < 0.0] = numpy.nan

    # Plotting the full reflectivity image, with significant transparency (alpha=0.25).
    # This plot will get 'dimmed' by the later ClusterMap().
    # zorder=1 so that it is above the Map Layers.
    MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
		   colorbar=False, axis_labels=False, drawer=map, zorder=1, alpha=0.15,
		   titlestr = "U = %.2f     n = %d" % (clustParams['devsAbove'], clustParams['subClustDepth']), titlesize = 16)
    
    
    (clustCnt, clustSizes, sortedIndicies) = GetClusterSizeInfo(clusters)

    ClusterMap(clusters,pylab.squeeze(rastData['vals']), sortedIndicies,#len(pylab.find(clustSizes >= (avgSize + 0.25*stdSize)))],
	       axis_labels=False, colorbar=False, zorder=2.0, drawer=map)


    # Commenting out .eps file, they are coming out waaayyy too big!
    #pylab.savefig(('%s_Raw.eps' % (optionParams[options.runName]['destNameStem'])) % figIndex)
    pylab.savefig(('%s_Raw.png' % (optionParams[options.runName]['destNameStem'])) % figIndex, dpi=250)
    pylab.clf()

