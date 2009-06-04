def PlotMapLayers(map, layerOptions):

    for layer in layerOptions :
	if layer[0] == 'states' :
	    map.drawstates(**layer[1])
	elif layer[0] == 'counties' :
	    map.readshapefile('shapefiles/countyp020', name='counties', **layer[1])
	elif layer[0] == 'rivers' :
	    map.drawrivers(**layer[1])
	elif layer[0] == 'roads' :
	    map.readshapefile('shapefiles/road_l', name='road', **layer[1])
	elif layer[0] == 'countries':
	    map.drawcountries(**layer[1])
	else :
	    raise TypeError('Unknown maplayer type: ' + layer[0])

