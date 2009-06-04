import scipy
import pylab

from ClusterFileUtils import *	# for GetClusterSizeInfo()

def ClusterMap(clusters, indiciesToShow, drawer=pylab):
    print 'producing clust map'
        
    # Display no more than atMost clusters,
    # and don't display more than the number
    # of clusters available. And not less than zero, either.
#    if (prevDispCnt == None) : prevDispCnt = max(min([atMost, clustCnt, 
#			    			 len(pylab.find(clustSizes >= minPixelCnt))]), 0)

    # Now, to determine how many to show this time..
#    dispClustCnt = clustCnt
    

#    currDispSum = scipy.sum(clustSizes[scipy.array(sortedIndicies[0:dispClustCnt])])
#    if (prevDispSum == None) : prevDispSum = currDispSum



#    iterCnt = 0
#    while (abs(currDispSum - prevDispSum) > 1.5*scipy.std(clustSizes) and (iterCnt < 5)) :
#        if currDispSum > prevDispSum :
#	    # There may be too many clusters being shown
#	    dispClustCnt -= 1
#	else :
#	    # There may be too few clusters being shown
#	    dispClustCnt += 1

#        dispClustCnt = min(clustCnt, max(dispClustCnt, 0))  # Still can't do more than there are or less than zero
#        currDispSum = scipy.sum(clustSizes[scipy.array(sortedIndicies[0:dispClustCnt])])
#        iterCnt += 1


    wasHold = pylab.ishold()   # record hold state, so that it can be returned to it after I am done.
    
    boxBoundx = None
    boxBoundy = None

    if wasHold :
	boxBoundx = pylab.xlim()
	boxBoundy = pylab.ylim()
    else :
    	boxBoundx = [min(clusters['lonAxis']), max(clusters['lonAxis'])]
    	boxBoundy = [min(clusters['latAxis']), max(clusters['latAxis'])]


    # Dimmer box
    pylab.fill([boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1]],
    	       [boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0]],
    	       'black', alpha=0.5)
     
    pylab.hold(True)

    (lons, lats) = scipy.meshgrid(clusters['lonAxis'], clusters['latAxis'])
    Z = scipy.empty_like(lons)

    # Need to draw each contour separately to guarrantee that the
    # cluster has a closed loop for itself (i.e. - not merged with
    # a neighboring cluster).
    print "ClustCnt:", len(indiciesToShow)

    for clustIndx in indiciesToShow :
	goodMembers = pylab.find(clusters['clusterIndicies'] == clustIndx)
#	print clustIndx, clustSizes[clustIndx]
	Z[:] = scipy.nan
	# There has to be an easier, faster way...
	for goodIndx in goodMembers :
		Z[clusters['members_LatLoc'][goodIndx], clusters['members_LonLoc'][goodIndx]] = 1

	drawer.contour(lons, lats, ~scipy.isnan(Z), 
		       [0, 1, 2], colors='w', linewidths=1.0)

    if (not wasHold) : pylab.hold(False)

    print 'map produced'

