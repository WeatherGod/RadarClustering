#!/usr/bin/env python

import os
import glob

from PARDataUtils import *
import numpy			# for numpy.meshgrid()
from RadarRastify import *

lipnDirname = "../data/PAR_Feb102009"
ncDirname = "../data/PAR_Feb102009"


filelist = glob.glob(os.path.join(lipnDirname, '*.lipn'))

for filename in filelist :
    # Loads the data from a file.
    parData = LoadPAR_lipn(filename)
    
    [gateGrid, aziGrid] = numpy.meshgrid(parData['range_gates'], parData['azimuths'])
    
    # Rastify the data onto a Lat-Lon grid
    [rastData, latAxis, lonAxis] = Rastify(parData['stat_lat'], parData['stat_lon'], 
					   parData['vals'], aziGrid, gateGrid,
                                           parData['elev_angle'], 1.0, parData['gate_length'],
					   0.005)

    outfile = os.path.join(ncDirname, datetime.datetime.utcfromtimestamp(parData['scan_time']).strftime('PAR_%Y%m%d_%H%M%S_rast.nc'))
    SavePAR_NetCDF(outfile, rastData, latAxis, lonAxis, parData['scan_time'], parData['var_name'])
    print outfile

 
                                            
