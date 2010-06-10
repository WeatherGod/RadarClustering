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
parser.add_option("-r", "--runs", dest="runNames", action="append", type="string",
		  help="Generate cluster images for RUNNAMEs", metavar="RUNNAME", default=[])
parser.add_option("-p", "--path", dest="pathName",
		  help="PATHNAME for cluster files and radar data", metavar="PATHNAME", default='.')
parser.add_option("-t", "--test", dest="isTest", action="store_true",
                  help="If set, files will be saved in current directory", default=False)
parser.add_option("-f", "--format", dest="outputFormat",
		  help="FORMAT for output file", metavar="FORMAT", default='pdf')

(options, args) = parser.parse_args()

if len(options.runNames) == 0 :
    parser.error("Missing RUNNAMEs")



print "The runNames:", options.runNames

optionParams = {}
optionParams['WSR'] = {'runName': 'Test_WSR_Params',
			   'domain': (38.0, -100.0, 40.0, -96.0),
			   'destDir': '../../Documents/SPA'}

optionParams['NWRT'] = {'runName': 'Test_NWRT_Params',
                        'domain': (35.5, -100.0, 37.0, -97.0),
                        'destDir': '../../Documents/SPA'}

for runName in options.runNames :
    params = optionParams[runName]
    print "Curr RunName:", runName

    fileList = glob.glob(os.sep.join([options.pathName, 'ClustInfo', params['runName'], '*.nc']))
    if (len(fileList) < 9) : print "WARNING: Not enough files found for run '" + runName + "'!"
    fileList.sort()

    if options.isTest :
        params['destDir'] = '.'

    (minLat, minLon, maxLat, maxLon) = params['domain']

    # Map display options
    mapLayers = MapUtils.mapLayers

    # Map domain
    map = Basemap(projection='cyl', resolution='i', suppress_ticks=True, fix_aspect=False,
				    llcrnrlat = minLat, llcrnrlon = minLon,
				    urcrnrlat = maxLat, urcrnrlon = maxLon)

    print minLat, minLon, maxLat, maxLon
    # Looping over all of the desired cluster files


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
    
        (clustParams, clusters) = LoadClustFile(filename)
        rastData = LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))
        rastData['vals'][rastData['vals'] < 0.0] = numpy.nan

        (clustCnt, clustSizes, sortedIndicies) = GetClusterSizeInfo(clusters)

        ClusterMap(clusters, numpy.squeeze(rastData['vals']), sortedIndicies,
	           radarBG_alpha=0.10, dimmerBox_alpha=0.20,
	           rasterized=True,
	           zorder=1.0, axis=ax)

        ax.set_title('U = %.2f   n = %d' % (clustParams['devsAbove'], clustParams['subClustDepth']), fontsize=10)

    MakeReflectColorbar(grid.cbar_axes[0]) 
    #fig.colorbar(tmpIM, cax=grid.cbar_axes[0])
    print "Saving..."
    fig.savefig('%s%s%s_ParamDemo.%s' % (params['destDir'], os.sep, runName, options.outputFormat), 
                dpi=125, bbox_inches='tight')

    # Need to make sure that memory usage doesn't go out of control...
    fig.clf()
    del fig


