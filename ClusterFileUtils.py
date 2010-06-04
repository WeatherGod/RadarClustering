from Scientific.IO.NetCDF import *
import numpy


def LoadClustFile(filename):
    print 'Loading clust file: ' + filename
    
    # Need a test to see if file opened or not...
    nc = NetCDFFile(filename, 'r')


    clusters = {'clusterIndicies': nc.variables['clusterIndex'].getValue(), 
		'members_LonLoc': nc.variables['pixel_xLoc'].getValue(), 
		'members_LatLoc': nc.variables['pixel_yLoc'].getValue(), 
		'latAxis': nc.variables['lat'].getValue().astype(numpy.float32),
		'lonAxis': nc.variables['lon'].getValue().astype(numpy.float32)}

    clustParams = {'xSize': len(clusters['lonAxis']), 'ySize': len(clusters['latAxis']), 
		   'devsAbove': getattr(nc, 'Upper_Sensitivity')[0], 
		   'devsBelow': getattr(nc, 'Lower_Sensitivity')[0],
		   'padLevel': getattr(nc, 'Padding_Level')[0], 'reach': getattr(nc, 'Reach')[0],
		   'subClustDepth': getattr(nc, 'Subcluster_Depth')[0], 'scantime': getattr(nc, 'time')[0],
		   'dataSource': getattr(nc, 'data_source')}
    
    nc.close();
    
    print 'Clust file loaded'
    return (clustParams, clusters)


def GetClustDataSource(clustFilename) :
    nc = NetCDFFile(clustFilename, 'r')
    filename = getattr(nc, 'data_source')
    nc.close()
    return filename


def GetClusterSizeInfo(clusters):

    clustCnt = max(clusters['clusterIndicies']) + 1
    clustSizes = numpy.array([0] * clustCnt)
    for clustIndx in clusters['clusterIndicies']:
	clustSizes[clustIndx] += 1

    # .argsort() sorts in ascending order, hence [::-1] to reverse it
    sortedIndicies = numpy.argsort(clustSizes)[::-1]

    return(clustCnt, clustSizes, sortedIndicies)

