SHELL = /bin/sh

.SUFFIXES:
.PHONY: all test_random test_radar clean

BINDIR = ..

SPA_INCLUDEDIR = ..
SPA_LIBDIR = ..
SPA_LIB = -L $(SPA_LIBDIR) -l SPAnalysis
SPA_INCLUDE = -I $(SPA_INCLUDEDIR)

NETCDF_INCLUDEDIR = /usr/include/netcdf-3
NETCDF_LIBDIR = /usr/lib/netcdf-3
NETCDF_LIB = -L $(NETCDF_LIBDIR) -l netcdf_c++ -l netcdf
NETCDF_INCLUDE = -I $(NETCDF_INCLUDEDIR)



all: test_random test_radar

test_random : $(BINDIR)/test_random

test_radar : $(BINDIR)/test_radar

$(BINDIR)/test_random : test_random.C $(SPA_INCLUDEDIR)/StrongPointAnalysis.h $(SPA_INCLUDEDIR)/Cluster.h
	$(CXX) $< -o $@ -O3 $(SPA_INCLUDE) $(SPA_LIB) $(NETCDF_INCLUDE) $(NETCDF_LIB) -lm $(CXXFLAGS)

$(BINDIR)/test_radar : test_radar.C $(SPA_INCLUDEDIR)/StrongPointAnalysis.h $(SPA_INCLUDEDIR)/Cluster.h
	$(CXX) $< -o $@ -O3 $(SPA_INCLUDE) $(SPA_LIB) $(NETCDF_INCLUDE) $(NETCDF_LIB) -lm $(CXXFLAGS)

clean:
	-rm -f $(BINDIR)/test_random $(BINDIR)/test_radar


