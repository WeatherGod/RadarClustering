#!/usr/bin/env python

from optparse import OptionParser	# Command-line parsing
import matplotlib
matplotlib.use("Agg")	# Agg seems to be more efficient of a backend than GTKAgg for this purpose

from ClusterFileUtils import *		# for GetClustDataSource(), LoadClustFile(), GetClusterSizeInfo()

from ClusterMap import *		# for ClusterMap()
from LoadRastRadar import *		# for LoadRastRadar()

from RadarPlotUtils import *		# for MakeReflectPPI(), TightBounds(), PlotMapLayers()

from mpl_toolkits.axes_grid1 import AxesGrid
from mpl_toolkits.basemap import Basemap
import MapUtils				# for PlotMapLayers and default mapLayers structure
import matplotlib.pyplot as pyplot
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
parser.add_option("-f", "--format", dest="outputFormat",
		  help="FORMAT for output file", metavar="FORMAT", default='pdf')

(options, args) = parser.parse_args()

if (options.runName == None) :
    parser.error("Missing RUNNAME")



print "The runName:", options.runName

optionParams = {}
optionParams['WSR'] = {'runName': 'Test_WSR_Params',
			   'domain': (38.0, -100.0, 40.0, -96.0),
			   'destDir': '../../Documents'}

optionParams['NWRT'] = {'runName': 'Test_NWRT_Params',
                        'domain': (35.5, -100.0, 37.0, -97.0),
                        'destDir': '../../Documents/SPA'}


fileList = glob.glob(os.sep.join([options.pathName, 'ClustInfo', optionParams[options.runName]['runName'], '*.nc']))
if (len(fileList) == 0) : print "WARNING: No files found for run '" + options.runName + "'!"
fileList.sort()

if options.isTest :
   optionParams[options.runName]['destDir'] = '.'

# AMS_Params: [-100.0, -96.0], [38.0, 40.0]
(minLat, minLon, maxLat, maxLon) = optionParams[options.runName]['domain']



# Map display options
mapLayers = MapUtils.mapLayers

# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=True, fix_aspect=False,
				llcrnrlat = minLat, llcrnrlon = minLon,
				urcrnrlat = maxLat, urcrnrlon = maxLon)

print minLat, minLon, maxLat, maxLon
# Looping over all of the desired cluster files


#fig = pyplot.figure(figsize=(5.0, 9.65))	# should be good for 3x3 grid
fig = pyplot.figure(figsize=(9.65, 5.0))	# should be good for 3x3 grid
figLayout = (3, 3)
grid = AxesGrid(fig, 111,
                nrows_ncols = (3, 3),
		axes_pad=0.22,
		cbar_mode='single',
		cbar_pad=0.05, cbar_size=0.08)

for figIndex, filename in enumerate(fileList[0:9]):
    pathname, nameStem = os.path.split(filename)
    ax = grid[figIndex]
    #ax = fig.add_subplot(figLayout[0], figLayout[1], figIndex + 1)

    MapUtils.PlotMapLayers(map, mapLayers, axis=ax)
    

#    ax.set_aspect('auto')

    (clustParams, clusters) = LoadClustFile(filename)
    rastData = LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))
    rastData['vals'][rastData['vals'] < 0.0] = numpy.nan

    # Plotting the full reflectivity image, with significant transparency (alpha=0.25).
    # This plot will get 'dimmed' by the later ClusterMap().
    # zorder=1 so that it is above the Map Layers.
    #MakeReflectPPI(numpy.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
    #		   colorbar=False, axis_labels=False, axis=ax, zorder=1, alpha=0.15,
    #		   titlestr = "U = %.2f     n = %d" % (clustParams['devsAbove'], clustParams['subClustDepth']),
    #		   titlesize = 16, rasterized=True)
    
    
    (clustCnt, clustSizes, sortedIndicies) = GetClusterSizeInfo(clusters)

    tmpIM = ClusterMap(clusters, numpy.squeeze(rastData['vals']), sortedIndicies,#len(numpy.nonzero(clustSizes >= (avgSize + 0.25*stdSize)))],
	       doRadarBG=True, radarBG_alpha=0.10,
               doDimmerBox=True, dimmerBox_alpha=0.20,
	       axis_labels=False, colorbar=False,
	       titlestr='U = %.2f   n = %d' % (clustParams['devsAbove'], clustParams['subClustDepth']),
	       titlesize=10, rasterized=True,
	       zorder=1.0, axis=ax)

    # Makes sure that the axes gets the proper limits as originally set by the Basemap.

    #map.set_axes_limits(ax=ax)
    #ax.set_xlim((minLon, maxLon))
    #ax.set_ylim((minLat, maxLat))

MakeRadarColorbar(tmpIM, "Reflectivity [dBZ]", fig, cax=grid.cbar_axes[0]) 
#fig.colorbar(tmpIM, cax=grid.cbar_axes[0])
print "Saving..."
fig.savefig('%s%s%s_ParamDemo.%s' % (optionParams[options.runName]['destDir'], os.sep, options.runName, options.outputFormat), 
            dpi=125, bbox_inches='tight')


