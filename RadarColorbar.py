#!/usr/bin/env python
from RadarPlotUtils import ReflectInfo


'''
Make a colorbar as a separate figure.
'''

from matplotlib import pyplot, mpl

# Make a figure and axes with dimensions as desired.
fig = pyplot.figure()
ax1 = fig.add_axes([0.45, 0.05, 0.03, 0.75])

# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
colorInfo = ReflectInfo()

# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=colorInfo['ref_table'],
                                   norm=colorInfo['norm'])
cb1.set_label('Reflectivity [dBZ]')

pyplot.savefig('../../Documents/SPA/Colorbar_Raw.eps')
pyplot.savefig('../../Documents/SPA/Colorbar_Raw.png', dpi=200)


