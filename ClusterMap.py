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

    #if holdStatus :
    #	boxBoundx = axis.get_xlim()
    #	boxBoundy = axis.get_ylim()
    #else :
    boxBoundx = (min(clusters['lonAxis']), max(clusters['lonAxis']))
    boxBoundy = (min(clusters['latAxis']), max(clusters['latAxis']))

    bbBoxX = [boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1]]
    bbBoxY = [boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0]]
    bbBox = zip(bbBoxX, bbBoxY)

    


    (lons, lats) = numpy.meshgrid(clusters['lonAxis'], clusters['latAxis'])

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
        MakeReflectPPI(vals, lats, lons,
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
    outlineGrid = numpy.empty_like(lons)
    clustVals = numpy.empty_like(lons)
#    clustVals.fill(scipy.nan)

    clustMembers = [numpy.nonzero(clusters['clusterIndicies'] == clustIndx) for clustIndx in indicesToShow]

    # Need to draw each contour separately to guarrantee that the
    # cluster has a closed loop for itself (i.e. - not merged with
    # a neighboring cluster).
    print "ClustCnt:", len(indicesToShow)

    # Assigning all radar values for those pixels in the clusters to clustVals,
    # which was initialized with NaNs.  When plotted, this has the effect of plotting
    # only the pixels that were clustered.
#    for goodMembers in clustMembers :
#	for goodIndx in goodMembers :

    # Plot the reflectivities of *just* the clustered pixels
    # zorder=3 helps to keep it *above* the dimmer box.
    # Note that it seems that a zorder of 2 does not sufficiently place
    # this pcolor above the dimmer box.  I don't know why...
#    MakeReflectPPI(clustVals, lats, lons, alpha=0.5, drawer=drawer, hold = True, **kwargs)


    # Plot the outlines of the clusters by initializing an array with NaNs,
    # and then assigning ones to the pixels for a particular cluster.
    # Then plot the contour of this array, forcing it to use only one contour level.
    # The clusters are done separately so that clusters that touch or even share a few
    # pixels are still distinguishable.
    for index, goodMembers in enumerate(clustMembers) :
        # If the cluster does not exist within the bounding box, don't bother rendering it.
	if not numpy.any(inpoly.point_inside_polygon(zip(clusters['lonAxis'][clusters['members_LonLoc'][goodMembers]],
						         clusters['latAxis'][clusters['members_LatLoc'][goodMembers]]),
						 bbBox)) :
            continue

        outlineGrid.fill(numpy.nan)
	clustVals.fill(numpy.nan)

	# Finding all members of the cluster
	# While this is an improvement, There has to be an easier, faster, better way...
	#for goodIndx in goodMembers :
	#    outlineGrid[clusters['members_LatLoc'][goodIndx], clusters['members_LonLoc'][goodIndx]] = 1
	#    clustVals[clusters['members_LatLoc'][goodIndx],
	#	      clusters['members_LonLoc'][goodIndx]] = vals[clusters['members_LatLoc'][goodIndx],
	#							   clusters['members_LonLoc'][goodIndx]]
        outlineGrid[clusters['members_LatLoc'][goodMembers],
		    clusters['members_LonLoc'][goodMembers]] = 1
        clustVals[clusters['members_LatLoc'][goodMembers],
		  clusters['members_LonLoc'][goodMembers]] = vals[clusters['members_LatLoc'][goodMembers],
								  clusters['members_LonLoc'][goodMembers]]
        

	# Plotting the cluster (white line, black line, then reflectivity patch)
	# This could probably be improved
	outline = axis.contour(lons, lats, ~numpy.isnan(outlineGrid), 
			       [0, 1, 2], colors='w', linewidths=6.0, zorder = zorders[zorderIndex])
        SetContourZorder(outline, zorders[zorderIndex])

        # shadow of the white line
	outline = axis.contour(lons, lats, ~numpy.isnan(outlineGrid), 
		       	       [0, 1, 2], colors='k', linewidths=3.0, zorder = zorders[zorderIndex + 1])
        SetContourZorder(outline, zorders[zorderIndex + 1])

        tmpIM = MakeReflectPPI(clustVals, lats, lons, axis=axis, zorder=zorders[zorderIndex + 2],
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

