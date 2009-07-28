from Scientific.IO.NetCDF import *
import numpy
import math
import datetime
import Numeric

class WDSSII_Error(Exception) : 
    def __init__(self, typeName) :
        self.badType = typeName

    def __repr__(self) :
        return "Unknown WDSSII PAR datatype %s" % (self.badType)

    def __str__(self) :
        return "Unknown WDSSII PAR datatype %s" % (self.badType)



# All of the loading functions will load the data into (theta, r) coordinates
# They will also produce coordinate data that will be parallel to the data array.
# In other words, you will have three 2-D arrays: data, range gate [Meters], azimuth [DEGREES north]

# TODO: These functions still need proper error handling...


def LoadPAR_wdssii(filename) :
# This loader will retreive the radar moments data obtained from the wdssii.arrc.nor.ouint computer

    nc = NetCDFFile(filename, 'r')

    varName = getattr(nc, 'TypeName')
    
    azimuths = numpy.array(nc.variables['Azimuth'].getValue())
    gateWidths = numpy.array(nc.variables['GateWidth'].getValue())
    beamWidths = numpy.array(nc.variables['BeamWidth'].getValue())

    missingData = getattr(nc, 'MissingData')[0]
    rangeFolded = getattr(nc, 'RangeFolded')[0]

    elevAngle = getattr(nc, 'Elevation')[0]
    statLat = getattr(nc, 'Latitude')[0]
    statLon = getattr(nc, 'Longitude')[0]
    scanTime = getattr(nc, 'Time')[0]

    parData = None
    aziLen = None
    rangeLen = None

    dataType = getattr(nc, 'DataType')

    if (dataType == 'SparseRadialSet') :
        rawParData = numpy.array(nc.variables[varName].getValue())
        xLoc = nc.variables['pixel_x'].getValue()
        yLoc = nc.variables['pixel_y'].getValue()

        (aziLen, rangeLen) = (azimuths.shape[0], yLoc.max() + 1)

        parData = numpy.empty((aziLen, rangeLen))
        parData.fill(numpy.nan)
        parData[xLoc, yLoc] = rawParData

    elif (dataType == 'RadialSet') :
        parData = numpy.array(nc.variables[varName].getValue())

        (aziLen, rangeLen) = parData.shape

    else :
        raise WDSSII_Error(dataType)

    
    rangeGrid = getattr(nc, 'RangeToFirstGate')[0] + (numpy.tile(numpy.arange(rangeLen), (aziLen, 1)) * 
						      numpy.tile(gateWidths, (rangeLen, 1)).T)
    aziGrid = numpy.tile(azimuths, (rangeLen, 1)).T


    # TODO: Maybe we should be using masks?
    parData[numpy.logical_or(parData == missingData, parData == rangeFolded)] = numpy.nan

    nc.close()

    
    return {'vals': parData,
	    'azimuth': aziGrid, 'range_gate': rangeGrid, 'elev_angle': elevAngle,
	    'stat_lat': statLat, 'stat_lon': statLon,
	    'scan_time': scanTime, 'var_name': varName,
	    'gate_length': numpy.median(gateWidths), 'beam_width': numpy.median(beamWidths)}



# TODO: Maybe adjust the code so that a parameterized version of this function can choose
#       what moment(s) to calculate from the data?
def LoadPAR_lipn(filename) :
# This function will load the radar data from a "Level-I Plus" file and produce Reflectivity moments.
# These files were generated by Boon Leng Cheong's program to process PAR data streams.

      # TODO: Need a test to see if file opened or not...
      nc = NetCDFFile(filename, 'r')
      
      varName = 'Reflectivity'
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

      # Maybe I should be using a mask?
      parData[R0 / getattr(nc, 'NoiseFloor') < 5] = numpy.nan

      (rangeGrid, aziGrid) = numpy.meshgrid(ranges, azimuths)

      gateLength = getattr(nc, 'GateSize')[0]
      
      elevAngle = getattr(nc, 'Elevation')[0]
      statLat = getattr(nc, 'Latitude')[0]
      statLon = getattr(nc, 'Longitude')[0]
      scanTime = getattr(nc, 'ScanTimeUTC')[0]
      
      nc.close()

      return {'vals': parData,
	      'azimuth': aziGrid, 'range_gate': rangeGrid, 'elev_angle': elevAngle,
	      'stat_lat': statLat, 'stat_lon': statLon,
	      'scan_time': scanTime, 'var_name': varName,
	      'gate_length': gateLength, 'beam_width': 1.0}



                                         
def SavePAR_NetCDF(filename, rastPAR, latAxis, lonAxis, scanTime, varName) :
# For saving radar data stored in Lat/Lon coordinates.
# TODO: Could probably make this better with varargs to give a chance to store more attributes.
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

