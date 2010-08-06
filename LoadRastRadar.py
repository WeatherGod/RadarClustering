import numpy
from scipy.io import netcdf

def LoadRastRadar(infilename) :
    nc = netcdf.netcdf_file(infilename, 'r')
    titleStr = (nc.title).replace("Rastified", "Rasterized")
    lats = nc.variables['lat'][:].astype(numpy.float32)
    lons = nc.variables['lon'][:].astype(numpy.float32)
    vals = nc.variables['value'][:].astype(numpy.float32)
    timestamp = nc.variables['time'][0]

    nc.close()

    return {'title': titleStr, 'lats': lats, 'lons': lons, 'vals': vals, 'scan_time': timestamp}


