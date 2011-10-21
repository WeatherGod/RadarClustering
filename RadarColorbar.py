#!/usr/bin/env python
from BRadar.plotutils import NWS_Reflect


'''
Make a colorbar as a separate figure.
'''

#from matplotlib import pyplot, mpl
import matplotlib.pyplot as plt
from matplotlib.colorbar import ColorbarBase

# Make a figure and axes with dimensions as desired.
fig = plt.figure()
ax1 = fig.add_axes([0.45, 0.05, 0.03, 0.75])


# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb1 = ColorbarBase(ax1, cmap=NWS_Reflect['ref_table'],
                                   norm=NWS_Reflect['norm'])
cb1.set_label('Reflectivity [dBZ]')

#pyplot.savefig('../../Documents/SPA/Colorbar_Raw.eps')
#pyplot.savefig('../../Documents/SPA/Colorbar_Raw.png', dpi=250)

plt.show()
