#import psyco
#psyco.full()

import numpy
import scipy
import math
#from shapely.geometry import Point, Polygon
#from shapely import iterops
from inpoly import *

#import time



def Rastify(statLat, statLon, origData, azimuths, 
	    rangeGates, elevAngle, deltaAz, deltaR, cellSize) :
    """
    RASTIFY    Covert data in spherical domain into rectilinear lat/lon domain

    Rastify(...) takes the vector or matrix of data points and places the
    points into a 2-D matrix organized by latitudes and longitudes.  The
    original data has a parallel vector or matrix of azimuths (in degrees North)
    and rangeGates (in meters) as well as a scalar elevAngle (in degrees).
    The origin of the spherical coordinates is given by the statLat (in
    degrees North) and statLon (in degrees East).  deltaAz denotes the 
    width of the beam in degrees while the deltaR scalar denotes the width 
    the of range gate in meters.

    The user specifies the resolution (in degrees) of the final product
    using cellSize.

    Author: Benjamin Root
    """
    goodValsInds = ~scipy.isnan(origData).flatten()
    origData = origData.flatten().compress(goodValsInds)
    azimuths = azimuths.flatten().compress(goodValsInds)
    rangeGates = rangeGates.flatten().compress(goodValsInds)
 
    # These arrays are for creating the verticies of the resolution volume
    # in 2-D.
    deltaAzMult = numpy.array([-1, -1, 1, 1])
    deltaRMult = numpy.array([-1, 1, 1, -1])
    
    # Getting the lat/lon locations of all the verticies.
    [tmpLat, tmpLon] = sph2latlon(statLat, statLon, 
				  azimuths[:, None] + (deltaAzMult[None, :] * deltaAz),
                                  rangeGates[:, None] + (deltaRMult[None, :] * deltaR), 
				  elevAngle)
    
    # Automatically determine the domain,
    # note that this isn't friendly to crossing the prime-meridian.
    latlim = [tmpLat.min(), tmpLat.max()]
    lonlim = [tmpLon.min(), tmpLon.max()]
    latAxis = numpy.arange(latlim[0], latlim[1] + cellSize, cellSize)
    lonAxis = numpy.arange(lonlim[0], lonlim[1] + cellSize, cellSize)
    
    # Automatically determine the grid size from the calculated axes.
    gridSize = [len(latAxis), len(lonAxis)]
    
    # Reference matrix is used to perform the 'affine' transformation from
    # lat/lon to the x-y coordinates that we need.
    # This can be adjusted later to allow for the user to specify a
    # different resolution for x direction from the resolution in the y
    # direction.
    R = makerefmat(lonlim[0], latlim[0], cellSize, cellSize)
    
    # Getting the x and y locations for each and every verticies.
    [tmpy, tmpx] = latlon2pix(R, tmpLat, tmpLon)
    
    # I wonder if it is computationally significant to get the min/max's of
    # each polygon's coordinates in one shot.  What about storage
    # requirements?
    
    # Initializing the data matrix.
    rastData = numpy.empty(gridSize)
    rastData[:] = numpy.nan
    
#    tic = time.time()    
    for index in xrange(0, len(origData)) :
        
#	resVol = Polygon(zip(tmpx[index, [0, 1, 2, 3, 0]], 
#			     tmpy[index, [0, 1, 2, 3, 0]]))
        resVol = zip(tmpx[index, [0, 1, 2, 3, 0]],
                     tmpy[index, [0, 1, 2, 3, 0]])


        # Getting all of the points that the polygon has, and then some.
        # This meshed grid is bounded by the domain.
        [ygrid, xgrid] = numpy.meshgrid(range(max(math.floor(min(tmpy[index, :])), 0),
					      min(math.ceil(max(tmpy[index, :]) + 1), 
						  gridSize[0]), 1),
        				range(max(math.floor(min(tmpx[index, :])), 0),
					      min(math.ceil(max(tmpx[index, :]) + 1),
						  gridSize[1]), 1))                              
#        gridPoints = [Point(xLoc, yLoc) for (xLoc, yLoc) in zip(xgrid.flat, ygrid.flat)]
	gridPoints = zip(xgrid.flat, ygrid.flat)

        
        # Determines which points fall within the resolution volume.  These
        # points will be the ones that will be assigned the value of the
        # original data point that the resolution volume represents.

#        for containedPoint in list(iterops.intersects(resVol, gridPoints, True)) :
	goodPoints = point_inside_polygon(gridPoints, resVol)
	

	    # Assign values to the appropriate locations (the grid points that
            # were inside the polygon), given that the data value that might
            # already be there is less-than the value to-be-assigned, or if
            # there hasn't been a data-value assigned yet (NAN).
            # This method corresponds with the method used by NEXRAD.

#            if (numpy.isnan(rastData[containedPoint.y, containedPoint.x])
#		or (rastData[containedPoint.y, containedPoint.x] < origData[index])) :
#		rastData[containedPoint.y, containedPoint.x] = origData[index]
	for containedPoint in zip(ygrid.flat[goodPoints], xgrid.flat[goodPoints]) :
             
            if (numpy.isnan(rastData[containedPoint])
		or (rastData[containedPoint] < origData[index])) :
		rastData[containedPoint] = origData[index]

#	if (index % 1000 == 0) :
#            toc = time.time()
#            print '[', index, ']:  ', toc - tic
#            tic = time.time()

    return [rastData, latAxis, lonAxis]



def sph2latlon(locLat, locLon, azis, gates, elevAngle) :
   """
   azis and gates are parallel vectors (or matrix) of azimuth angles (0 deg is
   north) and Range Gate distance (meters).  locLat and locLon are the
   latitude and longitude of the station in degrees.  elevAngle is the
   elevation angle in degrees.

   RETURNS: latout and lonout are vectors (or matricies)
   parallel to the spherical coordinates specified.
   Assumes that calculation applies to Earth.

   (Double-check this statement)
   Also, does not account for curvature of planet when determining the ground
   distance covered by the radial.
   """
   groundDist = gates * math.cos(math.radians(elevAngle))
   [latout, lonout] = LatLonFrom(locLat, locLon, groundDist, azis)
   return [latout, lonout]



def GreatCircleDist(fromLons, fromLats, toLons, toLats, radius=6367470.0) :
    fromLons = numpy.radians(fromLons)
    fromLats = numpy.radians(fromLats)
    toLons = numpy.radians(toLons)
    toLats = numpy.radians(toLats)

    return(radius * 2.0 * numpy.arcsin(numpy.sqrt(numpy.sin((toLats - fromLats)/2.0) ** 2
					      + numpy.cos(fromLats) * numpy.cos(toLats)
						* numpy.sin((toLons - fromLons)/2.0) **2)))

def Bearing(fromLons, fromLats, toLons, toLats) :
    fromLons = numpy.radians(fromLons)
    fromLats = numpy.radians(fromLats)
    toLons = numpy.radians(toLons)
    toLats = numpy.radians(toLats)

    return(numpy.arctan2( numpy.sin(toLons - fromLons) * numpy.cos(toLats),
			numpy.cos(fromLats) * numpy.sin(toLats)
			- numpy.sin(fromLats) * numpy.cos(toLats) * numpy.cos(toLons - fromLons) ) )

def LatLonFrom(fromLat, fromLon, dist, azi, radius=6367470.0) :
    """
    RETURNS (toLat, toLon)
    """
    fromLat = math.radians(fromLat)
    fromLon = math.radians(fromLon)
    azi = numpy.radians(azi)

    radianDist = dist/radius

    toLat = numpy.arcsin(math.sin(fromLat)*numpy.cos(radianDist)
		       + math.cos(fromLat)*numpy.sin(radianDist)*numpy.cos(azi))
    dlon = numpy.arctan2(-numpy.sin(azi)*numpy.sin(radianDist)*math.cos(fromLat),
			 numpy.cos(radianDist)-math.sin(fromLat)*math.sin(fromLat))
    toLon = zero22pi(fromLon - dlon + math.pi) - math.pi

    return (numpy.degrees(toLat), numpy.degrees(toLon))

def npi2pi(inAngle) :
    return(math.pi * ((numpy.abs(inAngle)/math.pi) 
		      - 2.0*numpy.ceil(((numpy.abs(inAngle)/math.pi)-1.0)/2.0))
           * numpy.sign(inAngle))

# TODO: FIX THIS!!!!
def zero22pi(inAngle) :
    outAngle = npi2pi(inAngle)
    outAngle[scipy.nonzero(outAngle < 0.0)] = outAngle[scipy.nonzero(outAngle < 0.0)] + 2.0 * math.pi
    return(outAngle)

def makerefmat(crnrlon, crnrlat, dx, dy) :
    return numpy.dot(numpy.array([[0.0, dx, crnrlon], 
				  [dy, 0.0, crnrlat]]),
		     numpy.array([[0.0, 1.0, -1.0],
				  [1.0, 0.0, -1.0],
				  [0.0, 0.0, 1.0]])).conj().T


def map2pix(refMat, X, Y) :
    [col, row] = numpy.linalg.solve(refMat[0:2, :].T, 
				     numpy.array([X.flat - refMat[2, 0], Y.flat - refMat[2, 1]]))
    return [row.reshape(Y.shape), col.reshape(X.shape)]

def latlon2pix(refMat, lat, lon) :
    # The following is a bit convoluded, but it is to get rid
    # of any possible issues with longitudinal abiguity
    [row1, col1] = map2pix(refMat, lon, lat)
    [row2, col2] = map2pix(refMat, lon + 360.0, lat)

    [rowsLow, rowsUp] = find_limits(row1, row2)
    [colsLow, colsUp] = find_limits(col1, col2)

    cycleCnt = numpy.maximum(rowsLow, colsLow)
    indicate = numpy.minimum(rowsUp, colsUp)
    cycleCnt[cycleCnt == -numpy.inf] = indicate[cycleCnt == -numpy.inf]
    cycleCnt[cycleCnt == -numpy.inf] = 0

    [row, col] = map2pix(refMat, lon + 360.0 * cycleCnt, lat)
    # need to correct for 0-base indexing
    return [row - 1, col - 1]

def find_limits(index1, index2) :
    diff = index2 - index1
    Z = (0.5 - index1) / diff
    lowerLims = -numpy.inf * numpy.ones_like(Z)
    lowerLims[diff > 0.0] = numpy.ceil(Z[diff > 0.0])
    upperLims = numpy.inf * numpy.ones_like(Z)
    upperLims[diff < 0.0] = numpy.floor(Z[diff < 0.0])
    return [lowerLims, upperLims]
