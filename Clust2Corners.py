#!/usr/bin/env python
import argparse         # for command-line parsing
import glob				# for filename globbing
import os.path
import numpy as np


from ClusterFileUtils import LoadClustFile
from BRadar.io import LoadRastRadar
from BRadar.maputils import LonLat2Cart
import radarsites as radar

import ZigZag.TrackFileUtils as TrackFileUtils
import ZigZag.TrackUtils as TrackUtils
import ZigZag.ParamUtils as ParamUtils


def _get_contour(xs, ys, feature) :
    from matplotlib._cntr import Cntr
    from itertools import chain
    c = Cntr(xs, ys, feature, None)
    # Returns a list where the first half of the elements are the boundaries
    # The second half contain connection codes that can be ignored here.
    # Can not assume clockwise or counter-clockwise traversal of the polygon
    res = c.trace(0)

    if len(res) == 0 :
        return np.empty((0, 2), dtype='i')
    else :
        # Link up the contours with a nan between them
        return np.vstack(chain(*[(ares, [(np.nan, np.nan)]) for ares in
                                 res[:len(res)//2]]))

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(
                        description="Convert a cluster file into a corner file")
    parser.add_argument("-r", "--run", dest="runName",
              help="Generate corner files for RUNNAME", metavar="RUNNAME")
    parser.add_argument("-p", "--path", dest="pathName",
              help=("PATHNAME for cluster files and radar data."
                    " Default: %(default)s"),
              metavar="PATHNAME", default=".")
    parser.add_argument("-c", "--contours", dest='savePolys',
                        help="Save polygons in a pickle called polygons.foo",
                        action='store_true', default=False)


    args = parser.parse_args()

    if args.runName is None :
        parser.error("Missing RUNNAME")

    runLoc = os.path.join(args.pathName, 'ClustInfo', args.runName)
    fileList = glob.glob(os.path.join(runLoc, '*.nc'))
    print "Run Location:", runLoc
    if (len(fileList) == 0) :
         print "WARNING: No files found for run '" + args.runName + "'!"
    fileList.sort()

    if args.savePolys :
        from cPickle import dump
        # Dictionary containing (cornerID, x-y vertices) key-value pairs
        polygons = {}


    volume_data = []
    cornerID = 0
    startTime = None

    for frameNum, filename in enumerate(fileList) :
        (clustParams, clusters) = LoadClustFile(filename)

        # Get rasterized reflectivity data
        radData = LoadRastRadar(os.path.join(args.pathName,
                                             clustParams['dataSource']))
        radarName = radData['station']
        if radarName == 'NWRT' :
            radarName = 'PAR'

        rastData = np.squeeze(radData['vals'])
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

        # For the polygons
        clustMask = np.empty(rastData.shape, dtype=bool)

        # We have everything in Lat/Lon... we need to convert to cartesian
        gridLons, gridLats = np.meshgrid(clusters['lonAxis'],
                                         clusters['latAxis'])
        gridx, gridy = LonLat2Cart(radarSite['LON'],
                                   radarSite['LAT'],
                                   gridLons, gridLats)

        dxdj, dxdi = np.gradient(gridx)
        dydj, dydi = np.gradient(gridy)

        # Now, we gotta merge this information...
        for aClust in clustMembers :
            # produce a Nx2 array
            locs = np.array([(clusters['members_LatLoc'][goodIndx],
                              clusters['members_LonLoc'][goodIndx]) for
                             goodIndx in aClust])

            if args.savePolys :
                # Reset the mask
                clustMask.fill(False)

                clustMask[clusters['members_LatLoc'][aClust],
                          clusters['members_LonLoc'][aClust]] = True

                verts = _get_contour(gridx, gridy, clustMask)
                polygons[cornerID] = verts



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
            a = np.hypot(dxdj[locIndices], dydj[locIndices])
            b = np.hypot(dxdi[locIndices], dydi[locIndices])
            dA = a * b
            sizeCentroids.append(np.sum(dA))

            # Supply this centroid's unique feature ID
            idCentroids.append(cornerID)
            cornerID += 1

        # Starting with initializing the volume object.
        aVol = {'volTime': (clustParams['scantime'] - startTime) / 60.0,
                'frameNum': frameNum,
                'stormCells': np.array(zip(xCentroids, yCentroids,
                                           sizeCentroids, idCentroids),
                                       dtype=TrackUtils.corner_dtype)}

        # Then build up the volume info
        volume_data.append(aVol)


    if len(volume_data) != 0 :
        simParams = dict()
        simParams.update(ParamUtils.simDefaults)
        simParams.update(ParamUtils.trackerDefaults)

        (xLims, yLims, tLims,
         frameLims) = TrackUtils.DomainFromVolumes(volume_data)

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
        TrackFileUtils.SaveCorners(os.path.join(runLoc,
                                                simParams['inputDataFile']),
                                   simParams['corner_file'],
                                   volume_data,
                                   path=runLoc)
        ParamUtils.SaveConfigFile(os.path.join(runLoc, 'simParams.conf'),
                                  simParams)

        if args.savePolys :
            dump(polygons, open(os.path.join(runLoc, 'polygons.foo'), 'wb'))

