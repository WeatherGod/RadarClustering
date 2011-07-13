#!/usr/bin/env python
import argparse         # for command-line parsing
import glob				# for filename globbing
import os.path
import numpy as np


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

runLoc = os.path.join(args.pathName, 'ClustInfo', args.runName)
fileList = glob.glob(os.path.join(runLoc, '*.nc'))
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
    rastData = np.squeeze(LoadRastRadar(os.path.join(args.pathName, clustParams['dataSource']))['vals'])
    # Get site info
    radarSite = radar.ByName(radarName, radar.Sites)[0]
    # Get cluster info
    clustMembers = [np.nonzero(clusters['clusterIndicies'] == clustIndx) for
                    clustIndx in np.unique(clusters['clusterIndicies'])]

    if startTime is None :
        startTime = clustParams['scantime']

    xCentroids = []
    yCentroids = []
    sizeCentroids = []
    idCentroids = []

    # Now, we gotta merge this information...
    for aClust in clustMembers :
        # produce a Nx2 array
        locs = np.array([(clusters['members_LatLoc'][goodIndx],
                          clusters['members_LonLoc'][goodIndx]) for goodIndx in aClust])

        # We have everything in Lat/Lon... we need to convert to cartesian
        gridLons, gridLats = np.meshgrid(clusters['lonAxis'], clusters['latAxis'])

        dists = GreatCircleDist(radarSite['LON'], radarSite['LAT'],
                                gridLons, gridLats)
        bearings = Bearing(radarSite['LON'], radarSite['LAT'],
                           gridLons, gridLats)

        gridx = dists * np.sin(bearings) / 1000.0
        gridy = dists * np.cos(bearings) / 1000.0

        dxdj, dxdi = np.gradient(gridx)
        dydj, dydi = np.gradient(gridy)

        locIndices = zip(*locs)

        yLocs = gridy[locIndices]
        xLocs = gridx[locIndices]


        # Find the Center of Mass.
        clustVals = rastData[locIndices]
        yCentroids.append(np.average(yLocs, weights=clustVals))
        xCentroids.append(np.average(xLocs, weights=clustVals))

        # Find the size of the feature.
        # This method assumes that the voxels are rhombus-shaped.
        # TODO: A better assumption would be parallelogram-shaped
        a = np.sqrt(dxdj[locIndices]**2 + dydj[locIndices]**2)
        b = np.sqrt(dxdi[locIndices]**2 + dydi[locIndices]**2)
        dA = a * b
        sizeCentroids.append(np.sum(dA))

        # Supply this centroid's unique feature ID
        idCentroids.append(cornerID)
        cornerID += 1

    # Starting with initializing the volume object.
    aVol = {'volTime': (clustParams['scantime'] - startTime) / 60.0,
            'frameNum': frameNum,
            'stormCells': np.array(zip(xCentroids, yCentroids, sizeCentroids, idCentroids),
                                      dtype=TrackUtils.corner_dtype)}

    # Then build up the volume info
    volume_data.append(aVol)



if len(volume_data) != 0 :

    simParams = dict()
    simParams.update(ParamUtils.simDefaults)
    simParams.update(ParamUtils.trackerDefaults)

    xLims, yLims, tLims, frameLims = TrackUtils.DomainFromVolumes(volume_data)

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
    TrackFileUtils.SaveCorners(os.path.join(runLoc, simParams['inputDataFile']),
                               simParams['corner_file'],
                               volume_data,
                               path=runLoc)
    ParamUtils.SaveConfigFile(os.path.join(runLoc, 'simParams.conf'), simParams)

