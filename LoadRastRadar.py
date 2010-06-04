from Scientific.IO.NetCDF import *
import numpy

def LoadRastRadar(infilename) :
    nc = NetCDFFile(infilename, 'r')
    titleStr = getattr(nc, 'title').replace("Rastified", "Rasterized")
    lats = nc.variables['lat'].getValue().astype(numpy.float32)
    lons = nc.variables['lon'].getValue().astype(numpy.float32)
    vals = nc.variables['value'].getValue().astype(numpy.float32)
    timestamp = nc.variables['time'].getValue()[0]

    nc.close()

    return {'title': titleStr, 'lats': lats, 'lons': lons, 'vals': vals, 'scan_time': timestamp}


