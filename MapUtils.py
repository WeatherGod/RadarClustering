import os.path			# for os.path.dirname(), os.path.abspath(), os.path.sep


# Default Map display options
mapLayers = [['states', {'linewidth':1.5, 'color':'k', 'zorder':0}],
             ['counties', {'linewidth':0.5, 'color':'k', 'zorder':0}],
             ['roads', {'linewidth':0.75, 'color':'r', 'zorder':0}],
             ['rivers', {'linewidth':0.5, 'color':'b', 'zorder':0}]]



def PlotMapLayers(map, layerOptions, axis=None):

    for layer in layerOptions :
        if layer[0] == 'states' :
            map.drawstates(ax=axis, **layer[1])
        elif layer[0] == 'counties' :
            map.readshapefile(os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), 'shapefiles', 'countyp020']),
                              name='counties', ax=axis, **layer[1])
        elif layer[0] == 'rivers' :
            map.drawrivers(ax=axis, **layer[1])
        elif layer[0] == 'roads' :
            map.readshapefile(os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'shapefiles', 'road_l']),
                              name='road', ax=axis, **layer[1])
        elif layer[0] == 'countries':
            map.drawcountries(ax=axis, **layer[1])
        else :
            raise TypeError('Unknown map_layer type: ' + layer[0])
