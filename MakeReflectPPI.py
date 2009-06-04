from MakePPI import *
from Scientific.IO.NetCDF import *
import matplotlib
import numpy
import ctables

def MakeReflectPPI(inName, **kwargs) :

    nc = NetCDFFile(inName, 'r')
    
    titleStr = getattr(nc, 'title')
    lats = nc.variables['lat'].getValue()
    lons = nc.variables['lon'].getValue()
    vals = nc.variables['value'].getValue()
    
    nc.close()
   
    # lut=-1 sets up discretized cmap, rather than smoothly changing cmap 
    ref_table = ctables.get_cmap('NWSRef', lut=-1)
    norm = matplotlib.colors.normalize(vmin = 0, vmax = 80, clip=True)
    
    MakePPI(lons, 'Longitude', lats, 'Latitude', numpy.squeeze(vals), 
	    titleStr, norm, ref_table, **kwargs)
