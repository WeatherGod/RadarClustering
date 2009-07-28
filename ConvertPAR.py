#!/usr/bin/env python

import os
import glob

from PARDataUtils import *
import numpy			# for .meshgrid()
import scipy.signal		# for .medfilt2d()
from RadarRastify import *

dataDirname = "/tint/PAR_lipn/2009/02/10"
rastDirname = "/tint/PAR_lipn/2009/02/10"


filelist = glob.glob(os.path.join(dataDirname, '*.lipn'))
filelist.sort()

for filename in filelist :
    print filename
    # Loads the data from a file.
    parData = LoadPAR_lipn(filename)

    parData['vals'] = scipy.signal.medfilt2d(parData['vals'], [1, 25])
        
    # Rastify the data onto a Lat-Lon grid
    [rastData, latAxis, lonAxis] = Rastify(parData['stat_lat'], parData['stat_lon'], 
					   parData['vals'], parData['azimuth'], parData['range_gate'],
                                           parData['elev_angle'], parData['beam_width'], parData['gate_length'],
					   0.005)

    outfile = os.sep.join([rastDirname, datetime.datetime.utcfromtimestamp(parData['scan_time']).strftime('PAR_%Y%m%d_%H%M%S_rast.nc')])
    SavePAR_NetCDF(outfile, rastData, latAxis, lonAxis, parData['scan_time'], parData['var_name'])
    print outfile

 
                                            
