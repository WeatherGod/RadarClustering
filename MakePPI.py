import numpy		# using .ma for Masked Arrays, also for .isnan()
import pylab		# for Matlab-like features

def MakePPI(x, xlabStr, y, ylabStr, vals, titleStr, colornorm, colorMap, drawer=pylab, **kwargs):
    
    (newx, newy) if (x.ndim == 1) pylab.meshgrid(x, y) else (x, y)
    
    drawer.pcolor(newx, newy, 
		 numpy.ma.masked_array(vals, mask=numpy.isnan(vals)),
		 cmap=colorMap, norm=colornorm, shading='flat', **kwargs)
    pylab.title(titleStr, fontsize=14)
    pylab.xlabel(xlabStr)
    pylab.ylabel(ylabStr)
    pylab.colorbar()
