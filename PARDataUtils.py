from Scientific.IO.NetCDF import *
import numpy
import math
import datetime
import Numeric


def LoadPAR_lipn(filename) :

      # TODO: Need a test to see if file opened or not...
      nc = NetCDFFile(filename, 'r')
      
      varName = 'Reflectivities'
      azimuths = numpy.array(nc.variables['Azimuth'].getValue())
      ranges = numpy.array(nc.variables['Range'].getValue()) * 1000.0    # convert to meters from km
      R0 = numpy.array(nc.variables['R0'].getValue())
      #R1 = numpy.array(nc.variables['R1_real'].getValue()) + numpy.array(nc.variables['R1_imag'].getValue())*1j
      #specWidth = numpy.sqrt(numpy.abs(numpy.log(numpy.abs(R0./R1)))) 
      #            * numpy.sign(numpy.log(numpy.abs(R0./R1))) 
      #            * (getattr(nc, 'Lambda')[0] / (2*math.sqrt(6)*math.pi*getattr(nc, 'PRT')[0]))
      parData = (10*numpy.log10(R0 / getattr(nc, 'NoiseFloor')[0]) 
		 + numpy.tile(20*numpy.log10(ranges / 1000.0), (len(azimuths), 1)) 
		 + getattr(nc, 'SNRdBtodBZ')[0])
      parData[R0 / getattr(nc, 'NoiseFloor') < 5] = numpy.nan
      
      gateLength = getattr(nc, 'GateSize')[0]
      distFirstGate = getattr(nc, 'StartRange')[0]
      gateCnt = len(ranges)
      elevAngle = getattr(nc, 'Elevation')[0]
      
      statLat = getattr(nc, 'Latitude')[0]
      statLon = getattr(nc, 'Longitude')[0]
      
      scanTime = getattr(nc, 'ScanTimeUTC')[0]
      
      nc.close()

      return {'vals': parData, 'azimuths': azimuths, 'range_gates': ranges,
	      'gate_length': gateLength, 'first_gate': distFirstGate, 'gate_cnt': gateCnt,
	      'elev_angle': elevAngle, 'stat_lat': statLat, 'stat_lon': statLon,
	      'scan_time': scanTime, 'var_name': varName}


                                            
def SavePAR_NetCDF(filename, rastPAR, latAxis, lonAxis, scanTime, varName) :
    nc = NetCDFFile(filename, 'w')
    
    # Setting Global Attribute
    nc.title = 'Rastified PAR ' + varName + ' ' + datetime.datetime.utcfromtimestamp(scanTime).strftime('%H:%M:%S UTC %m/%d/%Y')
    
    # Setting the dimensions
    nc.createDimension('lat', len(latAxis))
    nc.createDimension('lon', len(lonAxis))
    nc.createDimension('time', 1)
    
    # Setting the variables
    valueVar = nc.createVariable('value', Numeric.Float, ('time', 'lat', 'lon'))
    valueVar.long_name = 'Rastified PAR ' + varName
    valueVar.assignValue(rastPAR.reshape((1, len(latAxis), len(lonAxis))))
    
    latVar = nc.createVariable('lat', Numeric.Float, ('lat',))
    latVar.units = 'degrees_north'
    latVar.spacing = numpy.diff(latAxis).mean()
    latVar.assignValue(latAxis)
    
    lonVar = nc.createVariable('lon', Numeric.Float, ('lon',))
    lonVar.units = 'degrees_east'
    lonVar.spacing = numpy.diff(lonAxis).mean()
    lonVar.assignValue(lonAxis)
    
    timeVar = nc.createVariable('time', Numeric.Int, ('time',))
    timeVar.units = 'seconds since 1970-1-1'
    timeVar.assignValue(scanTime)
    
    nc.close()

