import matplotlib       # for colors.BoundaryNorm()
import numpy		# using .ma for Masked Arrays, also for .isnan()
import pylab		# for Matlab-like features
import ctables		# for color table for reflectivities
import os		# for various filepath-related tasks
from mpl_toolkits.basemap import Basemap   # for .drawstates(), .readshapefile(), 
						  # .drawrivers(), .drawcountries()

def ReflectInfo():
    # lut=-1 sets up discretized colormap, rather than smoothly changing colormap 
    ref_table = ctables.get_cmap('NWSRef', lut=-1)

    # Not quite sure what this does, but it was used in other code that developed professional looking plots...
    ref_table.set_over('0.25')
    ref_table.set_under('0.75')

    return({'ref_table': ref_table,
	    'norm': matplotlib.colors.BoundaryNorm(numpy.arange(0, 80, 5), ref_table.N, clip=False)})


def MakeReflectPPI(vals, lats, lons, axis_labels=True, **kwargs) :
# The Lats and Lons should be parallel arrays to vals.

    colorInfo = ReflectInfo()

    if axis_labels : kwargs.update(xlabel="Longitude", ylabel="Latitude")
    kwargs.setdefault('colorbarLabel', 'Reflectivity [dBZ]')

    MakePPI(lons, lats, vals, colorInfo['norm'], colorInfo['ref_table'], **kwargs)



def MakePPI(x, y, vals, norm, ref_table, drawer=pylab,
	    xlabel=None, ylabel=None, colorbar=True, colorbarLabel=None, titlestr=None, titlesize=12, **kwargs):
# It would be best if x and y were parallel arrays to vals.
# I haven't tried to see what would happen if they were just 1-D arrays each...
    
    thePlot = drawer.pcolor(x, y, 
			    numpy.ma.masked_array(vals, mask=numpy.isnan(vals)),
			    cmap=ref_table, norm=norm, **kwargs)

    if (titlestr is not None) : pylab.title(titlestr, fontsize=titlesize)
    if (xlabel is not None) : pylab.xlabel(xlabel)
    if (ylabel is not None) : pylab.ylabel(ylabel)
    # Makes the colorbar a little bit smaller than usual.
    if colorbar :
        tempBar = pylab.colorbar(thePlot, fraction=0.05, shrink=0.92)
	tempBar.set_label(colorbarLabel)

def PlotMapLayers(map, layerOptions):

    for layer in layerOptions :
	if layer[0] == 'states' :
	    map.drawstates(**layer[1])
	elif layer[0] == 'counties' :
	    map.readshapefile(os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'shapefiles', 'countyp020']), 
			      name='counties', **layer[1])
	elif layer[0] == 'rivers' :
	    map.drawrivers(**layer[1])
	elif layer[0] == 'roads' :
	    map.readshapefile(os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'shapefiles', 'road_l']), 
			      name='road', **layer[1])
	elif layer[0] == 'countries':
	    map.drawcountries(**layer[1])
	else :
	    raise TypeError('Unknown map_layer type: ' + layer[0])


def TightBounds(lons, lats, vals) :
    # Now that I understand numpy better, this can be improved
    # TODO: What the hell did I mean by that statement?
    #       I wish I could remember what idea I had...

    goodVals = ~numpy.isnan(vals)
    minLat = min(lats.flatten()[pylab.find(goodVals)])
    maxLat = max(lats.flatten()[pylab.find(goodVals)])
    minLon = min(lons.flatten()[pylab.find(goodVals)])
    maxLon = max(lons.flatten()[pylab.find(goodVals)])
    return {'minLat': minLat, 'minLon': minLon, 'maxLat': maxLat, 'maxLon': maxLon}



