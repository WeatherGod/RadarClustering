import scipy
import pylab

from RadarPlotUtils import MakeReflectPPI

def ClusterMap(clusters, vals, indiciesToShow, drawer=pylab, zorder=0, **kwargs):
# vals must be indexed in [lat, lon] orientation

    print 'producing clust map'
        
    boxBoundx = None
    boxBoundy = None

    if pylab.ishold() :
	boxBoundx = pylab.xlim()
	boxBoundy = pylab.ylim()
    else :
    	boxBoundx = [min(clusters['lonAxis']), max(clusters['lonAxis'])]
    	boxBoundy = [min(clusters['latAxis']), max(clusters['latAxis'])]

    # Create an array of zorder values to use for the components of the ClusterMap.
    # There is the dimmer box, and then each cluster has 3 components (white and 
    # black contours, and a patch element).
    zorders = scipy.linspace(zorder, zorder + 1, num = 1 + (3*len(indiciesToShow)), endpoint=False)


    # Dimmer box
    # zorder helps to keep this dimmer box *below* the other elements that will be added
    # in this function.
    pylab.fill([boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1]],
    	       [boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0]],
    	       'black', zorder = zorders[0], alpha=0.25)
     
    #drawer.hold(True)

    (lons, lats) = scipy.meshgrid(clusters['lonAxis'], clusters['latAxis'])
    outlineGrid = scipy.empty_like(lons)
    clustVals = scipy.empty_like(lons)
#    clustVals.fill(scipy.nan)

    clustMembers = [pylab.find(clusters['clusterIndicies'] == clustIndx) for clustIndx in indiciesToShow]

    # Need to draw each contour separately to guarrantee that the
    # cluster has a closed loop for itself (i.e. - not merged with
    # a neighboring cluster).
    print "ClustCnt:", len(indiciesToShow)

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
    for i, goodMembers in enumerate(clustMembers) :
        outlineGrid.fill(scipy.nan)
	clustVals.fill(scipy.nan)

	# Finding all members of the cluster
	# There has to be an easier, faster, better way...
	for goodIndx in goodMembers :
	    outlineGrid[clusters['members_LatLoc'][goodIndx], clusters['members_LonLoc'][goodIndx]] = 1
	    clustVals[clusters['members_LatLoc'][goodIndx],
		      clusters['members_LonLoc'][goodIndx]] = vals[clusters['members_LatLoc'][goodIndx],
								   clusters['members_LonLoc'][goodIndx]]
        

	# Plotting the cluster (white line, black line, then reflectivity patch)
	outline = drawer.contour(lons, lats, ~scipy.isnan(outlineGrid), 
				 [0, 1, 2], colors='w', linewidths=6.0, zorder = zorders[1 + 3*i], hold = True)
        SetContourZorder(outline, zorders[1 + 3*i])

	outline = drawer.contour(lons, lats, ~scipy.isnan(outlineGrid), 
		       		 [0, 1, 2], colors='k', linewidths=3.0, zorder = zorders[2 + 3*i], hold = True)
        SetContourZorder(outline, zorders[2 + 3*i])

        MakeReflectPPI(clustVals, lats, lons, drawer=drawer, zorder= zorders[3 + 3*i], hold = True, **kwargs)




    print 'map produced'


def SetContourZorder(theContours, zorder) :
    """
    This is a temporary function to work around a bug where contour ignores the zorder parameter.
    """
    for col in theContours.collections :
        col.set_zorder(zorder)

