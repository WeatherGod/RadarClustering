#! /usr/bin/env python

from ClusterMap import *
from LoadRastRadar import *
from RadarPlotUtils import *
import MapUtils

from mpl_toolkits.basemap import Basemap

import pylab

theFile = 'TestData.nc'
rasterized = False
namestem = ""


rastData = LoadRastRadar(theFile)

print pylab.nanmin(pylab.squeeze(rastData['vals']))

mapLayers = MapUtils.mapLayers


# Map domain
map = Basemap(projection='cyl', resolution='i', suppress_ticks=False,
                                llcrnrlat = rastData['lats'].min(), llcrnrlon = rastData['lons'].min(),
                                urcrnrlat = rastData['lats'].max(), urcrnrlon = rastData['lons'].max())

fig = pylab.figure(figsize = (15.0, 6.0))

ax = fig.add_subplot(1, 2, 1)

#map.drawstates(ax=ax, linewidth=1.5, color='k')
#map.drawrivers(ax=ax, linewidth=0.5, color='b')

MapUtils.PlotMapLayers(map, mapLayers, ax)

print rastData['lats'].shape

lonGrid, latGrid = numpy.meshgrid(rastData['lons'], rastData['lats'])

boxBoundx = ax.get_xlim()
boxBoundy = ax.get_ylim()

MakeReflectPPI(pylab.squeeze(rastData['vals']), latGrid, lonGrid,
               zorder=1, titlestr=rastData['title'], rasterized=rasterized, axis=ax)

#ax.set_xlim(boxBoundx)
#ax.set_ylim(boxBoundy)

ax = fig.add_subplot(1, 2, 2)
MapUtils.PlotMapLayers(map, mapLayers, ax)
#MakeReflectPPI(pylab.squeeze(rastData['vals']), rastData['lats'], rastData['lons'],
#               zorder=0.5, alpha=0.05, titlestr=rastData['title'], rasterized=rasterized, axis=ax)



print boxBoundx
print boxBoundy

ax.fill([boxBoundx[0], boxBoundx[0], boxBoundx[1], boxBoundx[1]],
           [boxBoundy[0], boxBoundy[1], boxBoundy[1], boxBoundy[0]],
           'black', alpha=0.35, zorder=1)


#ax.set_xlim(boxBoundx)
#ax.set_ylim(boxBoundy)

print ax.get_xlim()
print ax.get_ylim()



#print "Saving PNG"
#fig.savefig("testppi_%s.png" % namestem)
#print "Saving PDF"
#fig.savefig("testppi_%s.pdf" % namestem)
#print "Saving EPS"
#fig.savefig("testppi_%s.eps" % namestem)

pylab.show()

