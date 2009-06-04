import scipy

def GetClusterSizeInfo(clusters):

    clustCnt = max(clusters['clusterIndicies']) + 1
    clustSizes = scipy.array([0] * clustCnt)
    for clustIndx in clusters['clusterIndicies']:
	clustSizes[clustIndx] += 1

    # .argsort() sorts in ascending order, hence [::-1] to reverse it
    sortedIndicies = scipy.argsort(clustSizes)[::-1]

    return(clustCnt, clustSizes, sortedIndicies)

