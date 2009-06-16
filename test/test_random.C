using namespace std;

#include <cstdlib>		// for rand()
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

#include "StrongPointAnalysis.h"
#include "Cluster.h"

#include <netcdfcpp.h>

// g++ -g test.C -o test -L ./ -lSPAnalysis -lm

struct ClustParams_t
{
        float upperSensitivity;
        float lowerSensitivity;
        float paddingLevel;
        float reach;
        int subClustDepth;
};


bool OutputClusters(const string &filename, const vector<Cluster> &theClusters,
                    const size_t xLen, const size_t yLen, const ClustParams_t &clustParam);



int main()
{
        ClustParams_t clustParam;
        clustParam.upperSensitivity = 1.5;
        clustParam.lowerSensitivity = -0.5;
        clustParam.paddingLevel = 2.0;
        clustParam.reach = 2.5;
        clustParam.subClustDepth = 0;

	const size_t dataCount = 100000;
	const size_t xSize = 100;
	const size_t ySize = 150;
	const float thePower = 0.25;

	const size_t focusPoints = 45;
	const float maxRadius = 35.0;

	vector<float> xCenters(focusPoints);
	vector<float> yCenters(focusPoints);

	for (size_t index = 0; index < focusPoints; index++)
	{
		xCenters[index] = (((double) rand() / (double) RAND_MAX) * (xSize - (2.0 * maxRadius) - 1.0)) + maxRadius;
		yCenters[index] = (((double) rand() / (double) RAND_MAX) * (ySize - (2.0 * maxRadius) - 1.0)) + maxRadius;
	}

	vector<size_t> xLocs(dataCount);
	vector<size_t> yLocs(dataCount);
	vector<float> values(dataCount);

	vector< vector<float> > dataVals(ySize, vector<float>(xSize, NAN));

	for (size_t index = 0; index < dataCount; index++)
	{
		const float randAngle = (((double) rand() / (double) RAND_MAX) * 2.0 * M_PI);
		const float randDist = (((double) rand() / (double) RAND_MAX) * maxRadius);
		const size_t randFocus = (size_t) (((double) rand() / (double) RAND_MAX) * (focusPoints - 1));

		xLocs[index] = (size_t) (xCenters[randFocus] + (randDist * cosf(randAngle)));
		yLocs[index] = (size_t) (yCenters[randFocus] + (randDist * sinf(randAngle)));
		values[index] = (float) (((double) rand() / (double) RAND_MAX) * thePower);

		if (!isnan(dataVals[yLocs[index]][xLocs[index]]))
		{
			dataVals[yLocs[index]][xLocs[index]] += values[index];
		}
		else
		{
			dataVals[yLocs[index]][xLocs[index]] = values[index];
		}
	}

	StrongPointAnalysis theSPA(xLocs, yLocs, values, xSize, ySize, clustParam.upperSensitivity, clustParam.lowerSensitivity, 
								       clustParam.paddingLevel, clustParam.reach, clustParam.subClustDepth);

	cerr << "Loaded...\n";

	vector<Cluster> theClusters = theSPA.DoCluster();

	cerr << "Cluster Count: " << theClusters.size() << endl;
	

	if (!OutputClusters("output.txt", theClusters, xSize, ySize, clustParam))
	{
		cerr << "Problem output to file...\n";
		return(1);
	}

	return(0);
}


bool OutputClusters(const string &filename, const vector<Cluster> &theClusters,
		    const size_t xLen, const size_t yLen, const ClustParams_t &clustParam)
{

        NcFile clusterFile(filename.c_str(), NcFile::Replace);

        if (!clusterFile.is_valid())
        {
                cerr << "Could not create file: " << filename << "\n";
                return(false);
        }

        size_t pixelCnt = 0;
        for (vector<Cluster>::const_iterator aClust = theClusters.begin();
             aClust != theClusters.end();
             aClust++)
        {
                pixelCnt += aClust->size();
        }

        NcDim* pixelDim = clusterFile.add_dim("pixel_index", pixelCnt);
        NcDim* yDim = clusterFile.add_dim("lat", yLen);
        NcDim* xDim = clusterFile.add_dim("lon", xLen);

        NcVar* clustMember = clusterFile.add_var("clusterIndex", ncInt, pixelDim);
        clustMember->add_att("Description", "pixel cluster membership");
        NcVar* xLoc = clusterFile.add_var("pixel_xLoc", ncInt, pixelDim);
        xLoc->add_att("Description", "x-index of pixel in domain (lat,lon)");
        NcVar* yLoc = clusterFile.add_var("pixel_yLoc", ncInt, pixelDim);
        yLoc->add_att("Description", "y-index of pixel in domain (lat,lon)");


        NcVar* lats = clusterFile.add_var("lat", ncInt, yDim);
        lats->add_att("units", "unit");
        lats->add_att("spacing", 1);

        NcVar* lons = clusterFile.add_var("lon", ncInt, xDim);
        lons->add_att("units", "unit");
        lons->add_att("spacing", 1);

        clusterFile.add_att("title", "SPA Cluster Results of Random Generation");
        clusterFile.add_att("data_source", "");
        clusterFile.add_att("time", -1);

        // Need to do type-casting to double because the netcdf libraries can't seem to properly save a float.
        // Also, the truncf() is used to -- somewhat -- handle mantisa issues.
	clusterFile.add_att("Upper_Sensitivity", (double) (truncf(100.0 * clustParam.upperSensitivity)/100.0));
        clusterFile.add_att("Lower_Sensitivity", (double) (truncf(100.0 * clustParam.lowerSensitivity)/100.0));
        clusterFile.add_att("Padding_Level", (double) (truncf(100.0 * clustParam.paddingLevel)/100.0));
        clusterFile.add_att("Reach", (double) (truncf(100.0 * clustParam.reach)/100.0));
        clusterFile.add_att("Subcluster_Depth", clustParam.subClustDepth);
        int* clustIndicies = new int[pixelCnt];
        int* xPixels = new int[pixelCnt];
        int* yPixels = new int[pixelCnt];
        size_t pixelIndex = 0;
        for (size_t clustIndex = 0; clustIndex < theClusters.size(); clustIndex++)
        {
        	for (Cluster::const_iterator aMember = theClusters[clustIndex].begin();
                     aMember != theClusters[clustIndex].end();
                     aMember++, pixelIndex++)
                {
                        clustIndicies[pixelIndex] = clustIndex;
                        xPixels[pixelIndex] = aMember->XLoc;
                        yPixels[pixelIndex] = aMember->YLoc;
                }
        }

        clustMember->put(clustIndicies, pixelCnt);
        xLoc->put(xPixels, pixelCnt);
        yLoc->put(yPixels, pixelCnt);

	int *latVals = new int[yLen];
	for (size_t index = 0; index < yLen; index++)
	{
		latVals[index] = index;
	}

	int *lonVals = new int[xLen];
	for (size_t index = 0; index < xLen; index++)
	{
		lonVals[index] = index;
	}

        lats->put(latVals, yLen);
        lons->put(lonVals, xLen);

        clusterFile.close();

        delete [] clustIndicies;
        delete [] xPixels;
        delete [] yPixels;
	delete [] latVals;
	delete [] lonVals;

        return(true);
}

