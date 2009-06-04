import matplotlib       # for colors.normalize()
import numpy		# using .ma for Masked Arrays, also for .isnan()
import pylab		# for Matlab-like features
import ctables		# for color table for reflectivities
import os		# for various filepath-related tasks
from matplotlib.toolkits.basemap import Basemap   # for .drawstates(), .readshapefile(), 
						  # .drawrivers(), .drawcountries()

def MakeReflectPPI(vals, lats, lons, titleStr, **kwargs) :   
    # lut=-1 sets up discretized cmap, rather than smoothly changing cmap 
    ref_table = ctables.get_cmap('NWSRef', lut=-1)
    norm = matplotlib.colors.normalize(vmin = 0, vmax = 80, clip=True)
    
    MakePPI(lons, 'Longitude', lats, 'Latitude', vals, 
	    titleStr, norm, ref_table, **kwargs)



def MakePPI(x, xlabStr, y, ylabStr, vals, titleStr, colornorm, colorMap, drawer=pylab, **kwargs):
    
    (newx, newy) = pylab.meshgrid(x, y)
    
    drawer.pcolor(newx, newy, 
		 numpy.ma.masked_array(vals, mask=numpy.isnan(vals)),
		 cmap=colorMap, norm=colornorm, shading='flat', **kwargs)
    pylab.title(titleStr, fontsize=14)
    pylab.xlabel(xlabStr)
    pylab.ylabel(ylabStr)
    pylab.colorbar()



def PlotMapLayers(map, layerOptions):

    for layer in layerOptions :
	if layer[0] == 'states' :
	    map.drawstates(**layer[1])
	elif layer[0] == 'counties' :
	    map.readshapefile(os.sep.join([os.path.dirname(__file__), 'shapefiles', 'countyp020']), 
			      name='counties', **layer[1])
	elif layer[0] == 'rivers' :
	    map.drawrivers(**layer[1])
	elif layer[0] == 'roads' :
	    map.readshapefile(os.sep.join([os.path.dirname(__file__), 'shapefiles', 'road_l']), 
			      name='road', **layer[1])
	elif layer[0] == 'countries':
	    map.drawcountries(**layer[1])
	else :
	    raise TypeError('Unknown map_layer type: ' + layer[0])


def TightBounds(lons, lats, vals) :
    # Now that I understand numpy better, this can be improved
    goodVals = ~numpy.isnan(vals)
    minLat = min(lats.flatten()[pylab.find(goodVals)])
    maxLat = max(lats.flatten()[pylab.find(goodVals)])
    minLon = min(lons.flatten()[pylab.find(goodVals)])
    maxLon = max(lons.flatten()[pylab.find(goodVals)])
    return {'minLat': minLat, 'minLon': minLon, 'maxLat': maxLat, 'maxLon': maxLon}
