#! /usr/bin/env python

from ClusterMap import *
from LoadRastRadar import *
from RadarPlotUtils import *

from mpl_toolkits.basemap import Basemap

import pylab

theFile = 'TestData.nc'


rastData = LoadRastRadar(theFile)

print pylab.nanmin(pylab.squeeze(rastData['vals']))

mapLayers = [['states', {'linewidth':1.5, 'color':'k', 'zorder':0}],
             ['counties', {'linewidth':0.5, 'color':'k', 'zorder':0}],
             ['rivers', {'linewidth':0.5, 'color':'b', 'zorder':0}],
             ['roads', {'linewidth':0.75, 'color':'r', 'zorder':0}]]


# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=False,
                                llcrnrlat = rastData['lats'].min(), llcrnrlon = rastData['lons'].min(),
                                urcrnrlat = rastData['lats'].max(), urcrnrlon = rastData['lons'].max())

pylab.figure(figsize = (15.0, 6.0))

pylab.subplot(1, 2, 1)
PlotMapLayers(map, mapLayers)
pylab.hold(True)

MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
               drawer=map, zorder=1, hold = True, titlestr=rastData['title'])


pylab.subplot(1, 2, 2)
PlotMapLayers(map, mapLayers)
pylab.hold(True)
MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
               drawer=map, zorder=1, alpha=0.05, hold = True, titlestr=rastData['title'])

boxBoundx = pylab.xlim()
boxBoundy = pylab.ylim()


pylab.fill([boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1]],
           [boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0]],
           'black', alpha=0.35, hold=True, zorder=1)

pylab.xlim(boxBoundx)
pylab.ylim(boxBoundy)


pylab.show()
