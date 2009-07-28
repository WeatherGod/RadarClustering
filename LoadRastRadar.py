from Scientific.IO.NetCDF import *

def LoadRastRadar(infilename) :
    nc = NetCDFFile(infilename, 'r')
    titleStr = getattr(nc, 'title')
    lats = nc.variables['lat'].getValue()
    lons = nc.variables['lon'].getValue()
    vals = nc.variables['value'].getValue()
    timestamp = nc.variables['time'].getValue()[0]

    nc.close()

    return {'title': titleStr, 'lats': lats, 'lons': lons, 'vals': vals, 'scan_time': timestamp}


