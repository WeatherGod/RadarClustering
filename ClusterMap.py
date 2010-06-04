import numpy
import matplotlib.pyplot as pyplot
import inpoly

from RadarPlotUtils import MakeReflectPPI

def ClusterMap(clusters, vals, indicesToShow,
	       doRadarBG=True, doDimmerBox=True,
	       radarBG_alpha=0.15, dimmerBox_alpha=0.25,
	       colorbar=False, titlestr=None, titlesize=12, axis_labels=False,
	       zorder=0, axis=None, **kwargs):
    """
    Plot the clusters of the radar reflectivities in a really cool way.

    vals must be indexed in [lat, lon] orientation

    doRadarBG       - (Boolean) Do we want all reflectivities plotted as a background to the clusters?
    radarBG_alpha   - (float)   How opaque should the radar reflectivities be?
    doDimmerBox     - (Boolean) Do we want a 'greying' effect below the clusters?
    dimmerBox_alpha - (float)   How opaque should the dimmer box be?

    colorbar	    - (Boolean) Do we want a colorbar for the plot?
    titlestr	    - (string)  Title of the plot
    axis_labels     - (Boolean) Do we want the axes labeled?

    zorder	    - (float)   The zorder for the plot.  Note that this plot will internally use zorders 
                                from zorder to zorder + 1
    """
    if axis is None :
        axis = pyplot.gca()

    print 'producing clust map'
        
    boxBoundx = None
    boxBoundy = None

    holdStatus = axis.ishold()

    if holdStatus :
    	boxBoundx = axis.get_xlim()
    	boxBoundy = axis.get_ylim()
    else :
        boxBoundx = (min(clusters['lonAxis']), max(clusters['lonAxis']))
        boxBoundy = (min(clusters['latAxis']), max(clusters['latAxis']))

    bbBoxX = (boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1])
    bbBoxY = (boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0])
    bbBox = zip(bbBoxX, bbBoxY)

    (lons, lats) = numpy.meshgrid(clusters['lonAxis'], clusters['latAxis'])
    
    domainMask = (lats < boxBoundy[0]) | (lats > boxBoundy[1]) | (lons < boxBoundx[0]) | (lons > boxBoundx[1]) | numpy.isnan(vals)




    # elementCount determines how many things are going to be displayed in this
    #    plotting function.  To start, there will be len(indicesToShow) clusters
    #    to plot, each of those are plotted with three elements (white contour,
    #    black contour, and a patch).
    #    Then there is the possible radar background.
    #    Lastly, there is the possible dimmer box.
    elementCount = (3*len(indicesToShow)) + doRadarBG + doDimmerBox

    # Create an array of zorder values to use for the components of the ClusterMap.
    zorders = numpy.linspace(zorder, zorder + 1, num = elementCount, endpoint=False)

    zorderIndex = 0

    #  ------ Radar Background --------------
    if doRadarBG :
        MakeReflectPPI(vals, lats, lons, mask=domainMask,
        	       colorbar=False, axis_labels=False, titlestr=None, axis=axis,
		       zorder=zorders[zorderIndex], alpha=radarBG_alpha,
		       **kwargs)
        zorderIndex += 1
        axis.hold(True)




    # --------Dimmer box--------
    if doDimmerBox :
        print "doing Dimmer Box"
        axis.fill(bbBoxX, bbBoxY,
    	          'black', zorder = zorders[zorderIndex], alpha=dimmerBox_alpha)
        zorderIndex += 1
        axis.hold(True)


    # -------- Clusters ------------
    clustMask = numpy.empty(vals.shape, dtype=bool)
    #clustVals = numpy.empty_like(vals)

    clustMembers = [numpy.nonzero(clusters['clusterIndicies'] == clustIndx) for clustIndx in indicesToShow]

    # Need to draw each contour separately to guarrantee that the
    # cluster has a closed loop for itself (i.e. - not merged with
    # a neighboring cluster).
    print "ClustCnt:", len(indicesToShow)

    
    # Plot the outlines of the clusters by initializing an array with NaNs,
    # and then assigning ones to the pixels for a particular cluster.
    # Then plot the contour of this array, forcing it to use only one contour level.
    # The clusters are done separately so that clusters that touch or even share a few
    # pixels are still distinguishable.
    for index, goodMembers in enumerate(clustMembers) :
        # If the cluster does not exist within the bounding box, don't bother rendering it.
        if not numpy.any(numpy.logical_not(domainMask[clusters['members_LatLoc'][goodMembers],
				           	      clusters['members_LonLoc'][goodMembers]])) :
            continue

        clustMask.fill(True)
	#clustVals.fill(numpy.nan)

	# Finding all members of the cluster
        clustMask[clusters['members_LatLoc'][goodMembers],
		  clusters['members_LonLoc'][goodMembers]] = False

	# Plotting the cluster (white line, black line, then reflectivity patch)
	# This could probably be improved
        # white highlight
	outline = axis.contour(lons, lats, clustMask, 
			       [0, 1], colors='w', linewidths=7.0, zorder = zorders[zorderIndex])
        SetContourZorder(outline, zorders[zorderIndex])

        # black outline
	outline = axis.contour(lons, lats, clustMask, 
		       	       [0, 1], colors='k', linewidths=4.5, zorder = zorders[zorderIndex + 1])
        SetContourZorder(outline, zorders[zorderIndex + 1])

        tmpIM = MakeReflectPPI(vals, lats, lons, mask=clustMask, axis=axis, zorder=zorders[zorderIndex + 2],
		       axis_labels=False, colorbar=False, titlestr=None, **kwargs)
        zorderIndex += 3
    


    # Do colorbar, axis_labels, and titlestr when finished...
    if titlestr is not None :
        axis.set_title(titlestr, fontsize=titlesize)

    if axis_labels :
        axis.set_xlabel('Longitude [deg]')
        axis.set_ylabel('Latitude [deg]')

    # FIXME: This won't work right...
    if colorbar :
        # Makes the colorbar a little bit smaller than usual.
        tempBar = axis.figure.colorbar(tmpIM, fraction=0.05, shrink=0.92)
        tempBar.set_label('Reflectivity [dBZ]')

    # Return axis to whatever hold status it had before.
    axis.hold(holdStatus)

    print 'map produced'
    # TODO: Really, I need to come up with a way to play with polycollections, and pass that in, I think...
    return tmpIM


def SetContourZorder(theContours, zorder) :
    """
    This is a temporary function to work around a bug where contour ignores the zorder parameter.
    """
    for col in theContours.collections :
        col.set_zorder(zorder)

