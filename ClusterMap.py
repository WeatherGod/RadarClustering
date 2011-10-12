import numpy as np
import matplotlib.pyplot as plt
from matplotlib import transforms

from BRadar.plotutils import MakeReflectPPI
#from RadarPlotUtils import MakeReflectPPI

def ClusterMap(clusters, vals, indicesToShow,
               radarBG_alpha=0.15, dimmerBox_alpha=0.25,
               zorder=0, axis=None, **kwargs):
    """
    Plot the clusters of the radar reflectivities in a
    really cool way.

    vals must be indexed in [lat, lon] orientation

    radarBG_alpha   - (float)
        How opaque should the radar reflectivities be?
	    Set to zero if you don't want any radar background.

    dimmerBox_alpha - (float)
        How opaque should the dimmer box be?
        Set to zero if you don't want any dimmer box

    zorder	    - (float)
        The zorder for the plot.
        Note that this plot will internally use zorders 
             from *zorder* to *zorder* + 1
    """
    if axis is None :
        axis = plt.gca()

    print 'producing clust map'
        
    boxBoundx = None
    boxBoundy = None

    holdStatus = axis.ishold()

    if holdStatus :
    	boxBoundx = axis.get_xlim()
    	boxBoundy = axis.get_ylim()
    else :
        boxBoundx = (min(clusters['lonAxis']),
                     max(clusters['lonAxis']))
        boxBoundy = (min(clusters['latAxis']),
                     max(clusters['latAxis']))

    bbBoxX = (boxBoundx[0], boxBoundx[0],
              boxBoundx[1], boxBoundx[1])
    bbBoxY = (boxBoundy[0], boxBoundy[1],
              boxBoundy[1], boxBoundy[0])
    bbBox = zip(bbBoxX, bbBoxY)

    (lons, lats) = np.meshgrid(clusters['lonAxis'],
                               clusters['latAxis'])
    
    domainMask = (lats < boxBoundy[0]) | (lats > boxBoundy[1]) | \
                 (lons < boxBoundx[0]) | (lons > boxBoundx[1]) | \
                 np.isnan(vals)


    # Create a transform object for the drop shadow.
    dx, dy = 2/72., -2/72.
    #white_offset = axis.transData + transforms.ScaledTranslation(dx, dy, axis.figure.dpi_scale_trans)
    black_offset = axis.transData + \
                    transforms.ScaledTranslation(dx, dy,
                                    axis.figure.dpi_scale_trans)


    # elementCount determines how many things are going to be
    # displayed in this plotting function.  To start, there
    # will be len(indicesToShow) clusters to plot, each of
    # those are plotted with three elements (white contour,
    # black contour, and a patch).
    # Then there is the possible radar background.
    # Lastly, there is the possible dimmer box.
    # Note: this can be an over-estimate many clusters might be
    # outside the bounding box.
    elementCount = ((2*len(indicesToShow)) + (radarBG_alpha > 0.0)
                     + (dimmerBox_alpha > 0.0))

    # Create an array of zorder values to use for the components
    # of the ClusterMap.
    zorders = np.linspace(zorder, zorder + 1, num=elementCount,
                          endpoint=False)

    zorderIndex = 0

    #  ------ Radar Background --------------
    # Don't bother plotting the BG if alpha is zero.
    if radarBG_alpha > 0.0 :
        MakeReflectPPI(vals, lats, lons, mask=domainMask,
               colorbar=False, axis_labels=False, ax=axis,
		       zorder=zorders[zorderIndex], alpha=radarBG_alpha,
               meth='im',
		       **kwargs)
        zorderIndex += 1
        axis.hold(True)


    # --------Dimmer box--------
    # Don't bother plotting the dimmer box if it is zero.
    if dimmerBox_alpha > 0.0 :
        axis.fill(bbBoxX, bbBoxY,
    	          'black', zorder=zorders[zorderIndex],
                  alpha=dimmerBox_alpha)
        zorderIndex += 1
        axis.hold(True)


    # -------- Clusters ------------
    clustMask = np.empty(vals.shape, dtype=bool)
    #clustVals = np.empty_like(vals)

    clustMembers = [np.nonzero(clusters['clusterIndicies'] ==
                               clustIndx) for clustIndx in
                    indicesToShow]

    # Need to draw each contour separately to guarrantee that the
    # cluster has a closed loop for itself (i.e. - not merged with
    # a neighboring cluster).
    print "ClustCnt:", len(indicesToShow)

    
    # Plot the outlines of the clusters by initializing an
    # array with NaNs, and then assigning ones to the pixels
    # for a particular cluster. Then plot the contour of this
    # array, forcing it to use only one contour level.
    # The clusters are done separately so that clusters that
    # touch or even share a few pixels are still distinguishable.
    for index, goodMembers in enumerate(clustMembers) :
        # If the cluster does not exist within the bounding box,
        # don't bother rendering it.
        if not np.any(~domainMask[clusters['members_LatLoc'][goodMembers],
                                  clusters['members_LonLoc'][goodMembers]]) :
            continue

        clustMask.fill(True)

        # Finding all members of the cluster
        clustMask[clusters['members_LatLoc'][goodMembers],
                  clusters['members_LonLoc'][goodMembers]] = False

        # Plotting the cluster (white line, black line, then
        # reflectivity patch). This could probably be improved

        # black outline
        outline = axis.contour(lons, lats, clustMask,
                               [0, 1], colors='k', linewidths=2.5,
                               zorder=zorders[zorderIndex + 0])
        SetContourZorder(outline, zorders[zorderIndex + 1])
        SetContourTransform(outline, black_offset)

        # white highlight... save time by re-using contour data.
        #for aPath in outline.collections[0].get_paths() :
        #    axis.plot(*aPath.vertices.T, c='k', lw=2.5, zorder=zorders[zorderIndex],
        #              transform=white_offset)
        
        MakeReflectPPI(vals, lats, lons, mask=clustMask,
                       ax=axis, zorder=zorders[zorderIndex + 1],
                       axis_labels=False, colorbar=False,
                       meth='im', **kwargs)
        zorderIndex += 2

    # Return axis to whatever hold status it had before.
    axis.hold(holdStatus)

    print 'map produced'


def SetContourZorder(theContours, zorder) :
    """
    This is a temporary function to work around a bug where
    contour ignores the zorder parameter.
    """
    for col in theContours.collections :
        col.set_zorder(zorder)

def SetContourTransform(theContours, trans) :
    for col in theContours.collections :
        col.set_transform(trans)

