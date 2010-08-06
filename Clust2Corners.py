#!/usr/bin/env python
import argparse         # for command-line parsing
import glob				# for filename globbing
import os				# for os.sep and os.path
import pylab			# for pylab.find(), pylab.squeeze()
import numpy			# for numpy.unique(), numpy.array(), numpy.average()

import sys	
sys.path.append("../Tracking/")
from TrackFileUtils import SaveCorners


from ClusterFileUtils import LoadClustFile
from LoadRastRadar import LoadRastRadar
from RadarRastify import GreatCircleDist, Bearing
import radarsites as radar


parser = argparse.ArgumentParser("Convert a cluster file into a corner file")
parser.add_argument("-r", "--run", dest = "runName",
		  help = "Generate corner files for RUNNAME", metavar="RUNNAME")
parser.add_argument("-p", "--path", dest="pathName",
		  help = "PATHNAME for cluster files and radar data", metavar="PATHNAME", default=".")

args = parser.parse_args()

if args.runName is None :
    parser.error("Missing RUNNAME")

fileList = glob.glob(os.sep.join([args.pathName, 'ClustInfo', args.runName, '*.nc']))
if (len(fileList) == 0) : print "WARNING: No files found for run '" + args.runName + "'!"
fileList.sort()

# TODO: Temporary!!
radarName = "PAR"

volume_data = []
cornerID = 0

for frameNum, filename in enumerate(fileList) :
    (clustParams, clusters) = LoadClustFile(filename)
    rastData = pylab.squeeze(LoadRastRadar(os.sep.join([args.pathName, clustParams['dataSource']]))['vals'])

    radarSite = radar.ByName(radarName, radar.Sites)[0]

    clustMembers = [pylab.find(clusters['clusterIndicies'] == clustIndx) for clustIndx in numpy.unique(clusters['clusterIndicies'])]

    # Now, we gotta merge this information...
    # Starting with initializing the volume object.
    aVol = {'volTime': frameNum, 'stormCells': []}

    for aClust in clustMembers :
        locs = numpy.array([[clusters['members_LatLoc'][goodIndx],
		             clusters['members_LonLoc'][goodIndx]] for goodIndx in aClust])
        clustVals = [rastData[latLoc, lonLoc] for latLoc, lonLoc in locs]

        # We have everything in Lat/Lon... we need to convert to cartesian
        lats = clusters['latAxis'][locs[:, 0]]
        lons = clusters['lonAxis'][locs[:, 1]]

        dists = GreatCircleDist(radarSite['LON'], radarSite['LAT'], lons, lats)
        bearings = Bearing(radarSite['LON'], radarSite['LAT'], lons, lats)

        xLocs = dists * numpy.sin(bearings) / 1000.0
        yLocs = dists * numpy.cos(bearings) / 1000.0

        # Now find the Center of Mass.
        yLoc = numpy.average(yLocs, weights = clustVals)
        xLoc = numpy.average(xLocs, weights = clustVals)
        
        aVol['stormCells'].append({'xLocs': xLoc, 'yLocs': yLoc, 'cornerIDs': cornerID})
        cornerID += 1

    # Then build up the volume info
    volume_data.append(aVol)



if len(volume_data) != 0 :
    SaveCorners(os.sep.join([args.pathName, 'ClustInfo', args.runName, 'InputDataFile']),
				       os.sep.join([args.pathName, 'ClustInfo', args.runName, 'corner']),
				       len(volume_data), volume_data)

