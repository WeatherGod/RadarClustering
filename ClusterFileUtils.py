import numpy
from scipy.io import netcdf


def LoadClustFile(filename):
    print 'Loading clust file: ' + filename
    
    nc = netcdf.netcdf_file(filename, 'r')

    clusters = {'clusterIndicies': nc.variables['clusterIndex'][:], 
		'members_LonLoc': nc.variables['pixel_xLoc'][:], 
		'members_LatLoc': nc.variables['pixel_yLoc'][:], 
		'latAxis': nc.variables['lat'][:].astype(numpy.float32),
		'lonAxis': nc.variables['lon'][:].astype(numpy.float32)}

    clustParams = {'xSize': len(clusters['lonAxis']), 'ySize': len(clusters['latAxis']), 
		   'devsAbove': nc.Upper_Sensitivity, 
		   'devsBelow': nc.Lower_Sensitivity,
		   'padLevel': nc.Padding_Level, 'reach': nc.Reach,
		   'subClustDepth': nc.Subcluster_Depth, 'scantime': nc.time,
		   'dataSource': nc.data_source}
    
    nc.close()
    
    print 'Clust file loaded'
    return (clustParams, clusters)


def GetClustDataSource(clustFilename) :
    nc = netcdf.netcdf_file(clustFilename, 'r')
    filename = nc.data_source
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

