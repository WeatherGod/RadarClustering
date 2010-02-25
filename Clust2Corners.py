#!/usr/bin/env python
from optparse import OptionParser	# for command-line parsing
import glob				# for filename globbing
import os				# for os.sep and os.path
import pylab				# for pylab.find(), pylab.squeeze()
import numpy				# for numpy.unique(), numpy.array(), numpy.average()

import sys	
sys.path.append("../Tracking/")
from TrackFileUtils import SaveCorners


from ClusterFileUtils import LoadClustFile
from LoadRastRadar import LoadRastRadar
from RadarRastify import GreatCircleDist, Bearing
import radarsites as radar


parser = OptionParser()
parser.add_option("-r", "--run", dest = "runName",
		  help = "Generate corner files for RUNNAME", metavar="RUNNAME")
parser.add_option("-p", "--path", dest="pathName",
		  help = "PATHNAME for cluster files and radar data", metavar="PATHNAME", default=".")

(options, args) = parser.parse_args()

if options.runName is None :
    parser.error("Missing RUNNAME")

fileList = glob.glob(os.sep.join([options.pathName, 'ClustInfo', options.runName, '*.nc']))
if (len(fileList) == 0) : print "WARNING: No files found for run '" + options.runName + "'!"
fileList.sort()

# TODO: Temporary!!
radarName = "PAR"

volume_data = []

for frameNum, filename in enumerate(fileList) :
    (clustParams, clusters) = LoadClustFile(filename)
    rastData = pylab.squeeze(LoadRastRadar(os.sep.join([options.pathName, clustParams['dataSource']]))['vals'])

    radarSite = radar.ByName(radarName, radar.Sites)[0]

    clustMembers = [pylab.find(clusters['clusterIndicies'] == clustIndx) for clustIndx in numpy.unique(clusters['clusterIndicies'])]

    # Now, we gotta merge this information...
    # Starting with initializing the volume object.
    aVol = {'volTime': frameNum, 'stormCells': []}

    for aClust in clustMembers :
        locs = numpy.array([[clusters['members_LatLoc'][goodIndx],
		             clusters['members_LonLoc'][goodIndx]] for goodIndx in aClust])
	clustVals = [rastData[latLoc, lonLoc] for latLoc, lonLoc in locs]

        lats = clusters['latAxis'][locs[:, 0]]
        lons = clusters['lonAxis'][locs[:, 1]]

        dists = GreatCircleDist(radarSite['LON'], radarSite['LAT'], lons, lats)
        bearings = Bearing(radarSite['LON'], radarSite['LAT'], lons, lats)

        xLocs = dists * numpy.sin(bearings) / 1000
        yLocs = dists * numpy.cos(bearings) / 1000

        yLoc = numpy.average(yLocs, weights = clustVals)
	xLoc = numpy.average(xLocs, weights = clustVals)
        
	aVol['stormCells'].append({'xLoc': xLoc, 'yLoc': yLoc})

    # Then build up the volume info
    volume_data.append(aVol)



if len(volume_data) != 0 : SaveCorners(os.sep.join([options.pathName, 'ClustInfo', options.runName, 'InputDataFile']),
				       os.sep.join([options.pathName, 'ClustInfo', options.runName, 'corner']),
				       len(volume_data), volume_data)
