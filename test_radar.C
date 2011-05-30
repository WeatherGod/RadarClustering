using namespace std;

#include <iostream>
#include <fstream>
#include <string>
#include <vector>

#include <cstdlib>		// for atof(), atoi(), EXIT_SUCCESS, EXIT_FAILURE

#include <unistd.h>             // for optarg, opterr, optopt
#include <getopt.h>             // for getopt_long()

#include "StrongPointAnalysis.h"
#include "Cluster.h"

#include <netcdfcpp.h>


// g++ -g test_radar.C -o test_radar -I /usr/include/netcdf-3 -L ./ -lSPAnalysis -L /usr/lib/netcdf-3 -l netcdf_c++ -l netcdf -lm

// g++ -g test_radar.C -o test_radar -I /usr/include/BUtils -L ./ -lSPAnalysis -l BUtils -lm

struct ClustParams_t
{
	float upperSensitivity;
	float lowerSensitivity;
	float paddingLevel;
	float reach;
	int subClustDepth;
};

struct RadarData_t
{
	string inputFilename;

	double* dataVals;
	string var_LongName;
	string var_Units;

	long* dataEdges;

	double* latVals;
	string latUnits;
	double latSpacing;

	double* lonVals;
	string lonUnits;
	double lonSpacing;

	time_t scanTime;
	string timeUnits;

	string fileTitle;
};

string GrabAttribute(const NcVar* dataVar, const int attIndex);
bool OutputClusters(const string &filename, const vector<Cluster> &theClusters,
        	    const RadarData_t &radarInfo, const ClustParams_t &clustParam);

RadarData_t ReadRadarFile(const string &filename,
                          const float latmin, const float latmax,
                          const float lonmin, const float lonmax);


void PrintHelp()
{
	cerr << "test_radar -i INPUT_FILE -o OUTPUT_FILE\n"
	     << "           -u UPPER_SENSITIVITY -l LOWER_SENSITIVITY\n"
	     << "           -p PADDING_LEVEL -r REACH -s SUBCLUST\n"
             << "               [-x LAT_MIN] [-y LAT_MAX] [-m LON_MIN] [-n LON_MAX]\n"
	     << "           [-h | --help]\n\n";
}


int main(int argc, char* argv[])
{
	ClustParams_t clustParam;
	clustParam.upperSensitivity = NAN;	
	clustParam.lowerSensitivity = NAN;
	clustParam.paddingLevel = NAN;
	clustParam.reach = NAN;
	clustParam.subClustDepth = 0;

        float latmin = NAN;
        float latmax = NAN;
        float lonmin = NAN;
        float lonmax = NAN;

	string inputFilename = "";
	string outputFilename = "";

	int OptionIndex = 0;
	int OptionChar = 0;
	bool OptionError = false;
	opterr = 0;			// don't print out error messages, I will handle that.

	static struct option TheLongOptions[] = {
		{"input", 1, NULL, 'i'},
		{"output", 1, NULL, 'o'},
		{"upper", 1, NULL, 'u'},
		{"lower", 1, NULL, 'l'},
		{"padding", 1, NULL, 'p'},
		{"reach", 1, NULL, 'r'},
		{"subclust", 1, NULL, 's'},
                {"latmin", 1, NULL, 'x'},
                {"latmax", 1, NULL, 'y'},
                {"lonmin", 1, NULL, 'm'},
                {"latmin", 1, NULL, 'n'},
		{"help", 0, NULL, 'h'},
		{0, 0, 0, 0}
	};

	while ((OptionChar = getopt_long(argc, argv, "i:o:u:l:p:r:s:x:y:m:n:h", TheLongOptions, &OptionIndex)) != -1)
	{
		switch (OptionChar)
		{
		case 'i':
			inputFilename = optarg;
			break;
		case 'o':
			outputFilename = optarg;
			break;
		case 'u':
			clustParam.upperSensitivity = atof(optarg);
			break;
		case 'l':
			clustParam.lowerSensitivity = atof(optarg);
			break;
		case 'p':
			clustParam.paddingLevel = atof(optarg);
			break;
		case 'r':
			clustParam.reach = atof(optarg);
			break;
		case 's':
			clustParam.subClustDepth = atoi(optarg);
			break;
                case 'x':
                        latmin = atof(optarg);
                        break;
                case 'y':
                        latmax = atof(optarg);
                        break;
                case 'm':
                        lonmin = atof(optarg);
                        break;
                case 'n':
                        lonmax = atof(optarg);
                        break;
		case 'h':
			PrintHelp();
			return(1);
			break;
		case '?':
			cerr << "ERROR: Unknown argument: -" << (char) optopt << endl;
			OptionError = true;
			break;
		case ':':
			cerr << "ERROR: Missing value for argument: -" << (char) optopt << endl;
			OptionError = true;
			break;
		default:
			cerr << "ERROR: Programming error... Unaccounted option: -" << (char) OptionChar << endl;
			OptionError = true;
			break;
		}
	}

	if (OptionError)
	{
		PrintHelp();
		return(EXIT_FAILURE);
	}

	if  (inputFilename.empty() || outputFilename.empty()
	  || isnan(clustParam.lowerSensitivity) || isnan(clustParam.upperSensitivity)
	  || isnan(clustParam.paddingLevel) || isnan(clustParam.reach))
	{
		cerr << "Missing argument\n";
		PrintHelp();
		return(EXIT_FAILURE);
	}

	RadarData_t radarInfo = ReadRadarFile(inputFilename, latmin, latmax, lonmin, lonmax);

	if (radarInfo.inputFilename.empty())
	{
		cerr << "ERROR: Problem reading the data file: " << inputFilename << endl;
		cerr << "       Quiting without running SPA.\n";
		return(EXIT_FAILURE);
	}

	const size_t gridSize = radarInfo.dataEdges[1] * radarInfo.dataEdges[2];

	vector<size_t> xLocs(0);
	xLocs.reserve(gridSize);

	vector<size_t> yLocs(0);
	yLocs.reserve(gridSize);

	vector<float> values(0);
	values.reserve(gridSize);

	vector< vector<float> > theValues(radarInfo.dataEdges[1], vector<float>(radarInfo.dataEdges[2], NAN));

	size_t dataIndex = 0;
	for (size_t yIndex = 0; yIndex < radarInfo.dataEdges[1]; yIndex++)
	{
		for (size_t xIndex = 0; xIndex < radarInfo.dataEdges[2]; xIndex++, dataIndex++)
		{
			if (isfinite(radarInfo.dataVals[dataIndex]))
			{
				xLocs.push_back(xIndex);
				yLocs.push_back(yIndex);
				values.push_back(radarInfo.dataVals[dataIndex]);
				theValues[yIndex][xIndex] = radarInfo.dataVals[dataIndex];
			}
		}
	}

	delete [] radarInfo.dataVals; radarInfo.dataVals = NULL;


	StrongPointAnalysis theSPA(xLocs, yLocs, values, 
				   radarInfo.dataEdges[2], radarInfo.dataEdges[1], 
				   clustParam.upperSensitivity, clustParam.lowerSensitivity, 
				   clustParam.paddingLevel, clustParam.reach, clustParam.subClustDepth);

	cerr << "Loaded...\n";

	vector<Cluster> theClusters = theSPA.DoCluster();

	cerr << "Cluster Count: " << theClusters.size() << endl;
	
	if (!OutputClusters(outputFilename, theClusters, radarInfo, clustParam))
	{
		cerr << "Problem outputing to file: " << outputFilename << '\n';
		return(EXIT_FAILURE);
	}

	return(EXIT_SUCCESS);
}

/*
struct RadarData_t
{
        string inputFilename;

        double* dataVals;
        string var_LongName;
        string var_Units;

        long* dataEdges;

        double* latVals;
        string latUnits;
        double latSpacing;

        double* lonVals;
        string lonUnits;
        double lonSpacing;

        time_t scanTime;
        string timeUnits;

        string fileTitle;
};
*/

long lower_bound(const double* vals, const float minVal, const long valCnt)
{
        if (!isnan(minVal))
        {
                long index = 0;
                while (index < valCnt && vals[index] < minVal)
                {
                        index++;
                }
                return index;
        }
        else
        {
                return 0;
        }
}

long upper_bound(const double* vals, const float maxVal, const long valCnt)
{
        if (!isnan(maxVal))
        {
                long index = valCnt - 1;
                while (index > 0 && vals[index] > maxVal)
                {
                        index--;
                }
                return index;
        }
        else
        {
                return valCnt - 1;
        }
}

RadarData_t ReadRadarFile(const string &filename,
                          const float latmin, const float latmax,
                          const float lonmin, const float lonmax)
{
	RadarData_t inputData;

	NcFile radarFile(filename.c_str());

	if (!radarFile.is_valid())
	{
		cerr << "ERROR: Could not open radar file: " << filename << " for reading.\n";

		// Error is indicated by the lack of initialization of
		// the filename member of the struct.
		return(inputData);
	}

	NcVar* latVar = radarFile.get_var("lat");

	if (NULL == latVar)
	{
		cerr << "ERROR: invalid data file.  No variable called 'lat'!\n";
		radarFile.close();
		return(inputData);
	}

        long latCnt = latVar->num_vals();
        double* latVals = new double[latCnt];
	latVar->get(latVals, latCnt);
	inputData.latUnits = GrabAttribute(latVar, 0);
	inputData.latSpacing = strtod(GrabAttribute(latVar, 1).c_str(), NULL);

        const long minLatIndex = lower_bound(latVals, latmin, latCnt);
        const long maxLatIndex = upper_bound(latVals, latmax, latCnt);

        delete latVals;
        latCnt = (maxLatIndex - minLatIndex) + 1;
        latVar->set_cur(minLatIndex);
        inputData.latVals = new double[latCnt];
        latVar->get(inputData.latVals, latCnt);


	NcVar* lonVar = radarFile.get_var("lon");

	if (NULL == lonVar)
	{
		cerr << "ERROR: invalid data file.  No variable called 'lon'!\n";
		radarFile.close();
		return(inputData);
	}

        long lonCnt = lonVar->num_vals();
        double* lonVals = new double[lonCnt];
        latVar->get(lonVals, lonCnt);
        inputData.lonUnits = GrabAttribute(lonVar, 0);
        inputData.lonSpacing = strtod(GrabAttribute(lonVar, 1).c_str(), NULL);

        const long minLonIndex = lower_bound(lonVals, lonmin, lonCnt);
        const long maxLonIndex = upper_bound(lonVals, lonmax, lonCnt);

        delete lonVals;
        lonCnt = (maxLonIndex - minLonIndex) + 1;
        lonVar->set_cur(minLonIndex);
        inputData.lonVals = new double[lonCnt];
        lonVar->get(inputData.lonVals, lonCnt);

	
	NcVar* reflectVar = radarFile.get_var("value");

	if (reflectVar == NULL)
	{
		cerr << "ERROR: invalid data file.  No variable called 'value'!\n";
		radarFile.close();
		return(inputData);
	}
		

	inputData.dataEdges = reflectVar->edges();	// [0] - time, [1] - lat, [2] - lon
	inputData.dataEdges[1] = latCnt;
	inputData.dataEdges[2] = lonCnt;
	inputData.dataVals = new double[inputData.dataEdges[0] * inputData.dataEdges[1] * inputData.dataEdges[2]];
	reflectVar->set_cur(0, minLatIndex, minLonIndex);
	reflectVar->get(inputData.dataVals, inputData.dataEdges);

	inputData.var_LongName = GrabAttribute(reflectVar, 0);
	inputData.var_Units = "dBZ";//GrabAttribute(reflectVar, 1);


	NcVar* timeVar = radarFile.get_var("time");
	
	if (NULL == timeVar)
	{
		cerr << "ERROR: invalid data file.  No variable called 'time'!\n";
		radarFile.close();
		return(inputData);
	}

	inputData.scanTime = timeVar->as_long(0);
	inputData.timeUnits = GrabAttribute(timeVar, 0);

	NcAtt* titleAttrib = radarFile.get_att("title");

	inputData.fileTitle = (NULL == titleAttrib ? "" : titleAttrib->as_string(0));

	delete titleAttrib;

	radarFile.close();

	// Success!
	inputData.inputFilename = filename;


	return(inputData);
}


string GrabAttribute(const NcVar* dataVar, const int attIndex)
{
	if (NULL == dataVar)
	{
		cerr << "ERROR: Invalid NcVar!\n";
		return("");
	}

	NcAtt* dataAttrib = dataVar->get_att(attIndex);

	if (NULL == dataAttrib)
	{
		cerr << "ERROR: Could not obtain data attribute: index #" << attIndex << endl;
		return("");
	}

	const string returnVal = dataAttrib->as_string(0);

	delete dataAttrib;

	return(returnVal);
}





bool OutputClusters(const string &filename, const vector<Cluster> &theClusters,
                    const RadarData_t &radarInfo, const ClustParams_t &clustParam)
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
	NcDim* latDim = clusterFile.add_dim("lat", radarInfo.dataEdges[1]);
	NcDim* lonDim = clusterFile.add_dim("lon", radarInfo.dataEdges[2]);

	NcVar* clustMember = clusterFile.add_var("clusterIndex", ncInt, pixelDim);
	clustMember->add_att("Description", "pixel cluster membership");
	NcVar* xLoc = clusterFile.add_var("pixel_xLoc", ncInt, pixelDim);
	xLoc->add_att("Description", "x-index of pixel in domain (lat,lon)");
	NcVar* yLoc = clusterFile.add_var("pixel_yLoc", ncInt, pixelDim);
	yLoc->add_att("Description", "y-index of pixel in domain (lat,lon)");


	NcVar* lats = clusterFile.add_var("lat", ncDouble, latDim);
	lats->add_att("units", radarInfo.latUnits.c_str());
	lats->add_att("spacing", radarInfo.latSpacing);

	NcVar* lons = clusterFile.add_var("lon", ncDouble, lonDim);
	lons->add_att("units", radarInfo.lonUnits.c_str());
	lons->add_att("spacing", radarInfo.lonSpacing);

	clusterFile.add_att("title", "SPA Cluster Results of Radar Reflectivities");
	clusterFile.add_att("data_source", radarInfo.inputFilename.c_str());
	clusterFile.add_att("time", radarInfo.scanTime);

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

	lats->put(radarInfo.latVals, radarInfo.dataEdges[1]);
	lons->put(radarInfo.lonVals, radarInfo.dataEdges[2]);

	clusterFile.close();

	delete [] clustIndicies;
	delete [] xPixels;
	delete [] yPixels;

	return(true);
}


/*
	outFile << xSize << ' ' << ySize << ' ' << upperSensitivity << ' ' << lowerSensitivity << ' ' 
		<< paddingLevel << ' ' << reach << ' ' << subClustDepth << '\n';
*/
/*
	for (size_t yIndex = 0; yIndex < ySize; yIndex++)
	{
		outFile << dataVals[yIndex][0];
		for (size_t xIndex = 1; xIndex < xSize; xIndex++)
		{
			outFile << ' ' << dataVals[yIndex][xIndex];
		}
		outFile << '\n';
	}
*/
/*
	outFile << theClusters.size() << '\n';

	for (vector<Cluster>::const_iterator aClust = theClusters.begin();
	     aClust != theClusters.end();
	     aClust++)
	{
		outFile << aClust->size() << '\n';

		for (Cluster::const_iterator aMember = aClust->begin();
		     aMember != aClust->end();
		     aMember++)
		{
			outFile << aMember->XLoc + 1 << ' ' << aMember->YLoc + 1 << ' ' << aMember->memberVal << '\n';
		}
	}

	outFile.close();
*/

