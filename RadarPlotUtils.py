import matplotlib       # for colors.BoundaryNorm()
import numpy		# using .ma for Masked Arrays, also for .isnan()
import matplotlib.pyplot as pyplot
import ctables		# for color table for reflectivities
import os		# for various filepath-related tasks


# lut=-1 sets up discretized colormap, rather than smoothly changing colormap 
ref_table = ctables.get_cmap('NWSRef', lut=-1)

# Not quite sure what this does, but it was used in other code that developed professional looking plots...
ref_table.set_over('0.25')
ref_table.set_under('0.75')

colorInfo = {'ref_table': ref_table,
	     'norm': matplotlib.colors.BoundaryNorm(numpy.arange(0, 80, 5), ref_table.N, clip=False)}


def MakeReflectPPI(vals, lats, lons, axis_labels=True, **kwargs) :
# The Lats and Lons should be parallel arrays to vals.

    if axis_labels : kwargs.update(xlabel="Longitude [deg]", ylabel="Latitude [deg]")
    kwargs.setdefault('colorbarLabel', 'Reflectivity [dBZ]')

    return MakePPI(lons, lats, vals, colorInfo['norm'], colorInfo['ref_table'], **kwargs)



def MakePPI(x, y, vals, norm, ref_table, axis=None, mask=None,
	    xlabel=None, ylabel=None, labelsize=10, colorbar=True, 
	    colorbarLabel=None, titlestr=None, titlesize=12, rasterized=False, **kwargs):
    # It would be best if x and y were parallel arrays to vals.
    # I haven't tried to see what would happen if they were just 1-D arrays each...
    if axis is None :
        axis = pyplot.gca()

    if mask is None :
        mask = numpy.isnan(vals)
    
    thePlot = axis.pcolor(x, y,
    			  numpy.ma.masked_array(vals, mask=mask),
    			  cmap=ref_table, norm=norm, **kwargs)
    thePlot.set_rasterized(rasterized)
#    thePlot = axis.imshow(numpy.ma.masked_array(vals, mask=numpy.isnan(vals)),
#			  cmap=ref_table, norm=norm, origin='lower',
#			  extent=(x.min(), x.max(), y.min(), y.max()), **kwargs)

    if (titlestr is not None) : axis.set_title(titlestr, size=titlesize)
    if (xlabel is not None) : axis.set_xlabel(xlabel, size=labelsize)
    if (ylabel is not None) : axis.set_ylabel(ylabel, size=labelsize)


    if colorbar :
        MakeRadarColorbar(thePlot, colorbarLabel)

    return thePlot

def MakeRadarColorbar(thePlot, colorbarLabel, figure=None, cax=None) :
    if figure is None:
        figure = pyplot.gcf()

    if cax is None :
        # If there is no specified caxis, then the figure has to make a new one,
        # so let's specify the parameters for it...
        # fraction and shrink makes the colorbar a little bit smaller than usual.
        cBar = figure.colorbar(thePlot, fraction=0.95, shrink=0.92)
    else :
        # There is already a caxis, so let's not play around with it...
        cBar = figure.colorbar(thePlot, cax=cax)

    cBar.set_label(colorbarLabel)
    return cBar

# Maybe this should go into MapUtils?
def TightBounds(lons, lats, vals) :
    badVals = numpy.isnan(vals)
    lats_masked = numpy.ma.masked_array(lats, mask=badVals)
    lons_masked = numpy.ma.masked_array(lons, mask=badVals)
    minLat = min(lats_masked)
    maxLat = max(lats_masked)
    minLon = min(lons_masked)
    maxLon = max(lons_masked)
    return {'minLat': minLat, 'minLon': minLon, 'maxLat': maxLat, 'maxLon': maxLon}



