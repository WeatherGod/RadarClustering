#!/usr/bin/env python
import argparse         # for command-line parsing
import glob				# for filename globbing
import os				# for os.sep and os.path
import pylab			# for pylab.find(), pylab.squeeze()
import numpy			# for numpy.unique(), numpy.array(), numpy.average()


from ClusterFileUtils import LoadClustFile
from LoadRastRadar import LoadRastRadar
from RadarRastify import GreatCircleDist, Bearing
import radarsites as radar

#import sys	
#sys.path.append("../Tracking/")
import ZigZag.TrackFileUtils as TrackFileUtils
import ZigZag.TrackUtils as TrackUtils
import ZigZag.ParamUtils as ParamUtils

parser = argparse.ArgumentParser(description="Convert a cluster file into a corner file")
parser.add_argument("-r", "--run", dest = "runName",
		  help = "Generate corner files for RUNNAME", metavar="RUNNAME")
parser.add_argument("-p", "--path", dest="pathName",
		  help = "PATHNAME for cluster files and radar data. Default: %(default)s",
          metavar="PATHNAME", default=".")

args = parser.parse_args()

if args.runName is None :
    parser.error("Missing RUNNAME")

runLoc = args.pathName + os.sep + 'ClustInfo' + os.sep + args.runName
fileList = glob.glob(runLoc + os.sep + '*.nc')
print "Run Location:", runLoc
if (len(fileList) == 0) : print "WARNING: No files found for run '" + args.runName + "'!"
fileList.sort()


# TODO: Temporary!!
radarName = "PAR"

volume_data = []
cornerID = 0
startTime = None

for frameNum, filename in enumerate(fileList) :
    (clustParams, clusters) = LoadClustFile(filename)

    # Get rasterized reflectivity data
    rastData = numpy.squeeze(LoadRastRadar(args.pathName + os.sep + clustParams['dataSource'])['vals'])
    # Get site info
    radarSite = radar.ByName(radarName, radar.Sites)[0]
    # Get cluster info
    clustMembers = [pylab.find(clusters['clusterIndicies'] == clustIndx) for clustIndx in numpy.unique(clusters['clusterIndicies'])]

    if startTime is None :
        startTime = clustParams['scantime']

    xCentroids = []
    yCentroids = []
    idCentroids = []

    # Now, we gotta merge this information...
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
        yCentroids.append(numpy.average(yLocs, weights=clustVals))
        xCentroids.append(numpy.average(xLocs, weights=clustVals))
        idCentroids.append(cornerID)
        cornerID += 1

    # Starting with initializing the volume object.
    aVol = {'volTime': (clustParams['scantime'] - startTime) / 60.0,
            'stormCells': numpy.array(zip(xCentroids, yCentroids, idCentroids),
                                      dtype=TrackUtils.corner_dtype)}

    # Then build up the volume info
    volume_data.append(aVol)



if len(volume_data) != 0 :

    simParams = dict()
    simParams.update(ParamUtils.simDefaults)
    simParams.update(ParamUtils.trackerDefaults)

    xLims, yLims, tLims = TrackUtils.DomainFromVolumes(volume_data)

    simParams['xLims'] = xLims
    simParams['yLims'] = yLims
    simParams['tLims'] = tLims
    simParams['frameCnt'] = len(volume_data)

    # These parameters are irrelevant.
    simParams.pop('seed')
    simParams.pop('totalTracks')
    simParams.pop('endTrackProb')
    simParams.pop('simConfFile')
    simParams.pop('analysis_stem')

    simParams['simName'] = args.runName
    TrackFileUtils.SaveCorners(runLoc + os.sep + simParams['inputDataFile'],
                               simParams['corner_file'],
                               volume_data,
                               path=runLoc)
    ParamUtils.SaveConfigFile(runLoc + os.sep + 'simParams.conf', simParams)

