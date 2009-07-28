SHELL = /bin/sh

.SUFFIXES:
.PHONY: all clean install remove

BINDIR = $(HOME)/bin

SPA_DEVDIR = $(HOME)/include
SPA_LIBDIR = $(HOME)/lib
SPA_LIB = -L $(SPA_LIBDIR) -l SPAnalysis
SPA_INCLUDE = -I $(SPA_DEVDIR)

NETCDF_DEVDIR = /usr/include/netcdf
NETCDF_LIBDIR = /usr/lib/
NETCDF_LIB = -L $(NETCDF_LIBDIR) -l netcdf_c++ -l netcdf
NETCDF_INCLUDE = -I $(NETCDF_DEVDIR)



all: test_random test_radar

test_random : test_random.C $(SPA_DEVDIR)/StrongPointAnalysis.h $(SPA_DEVDIR)/Cluster.h
	$(CXX) $< -o $@ -O3 $(SPA_INCLUDE) $(SPA_LIB) $(NETCDF_INCLUDE) $(NETCDF_LIB) -lm $(CXXFLAGS)

test_radar : test_radar.C $(SPA_DEVDIR)/StrongPointAnalysis.h $(SPA_DEVDIR)/Cluster.h
	$(CXX) $< -o $@ -O3 $(SPA_INCLUDE) $(SPA_LIB) $(NETCDF_INCLUDE) $(NETCDF_LIB) -lm $(CXXFLAGS)

install : $(BINDIR)/test_random $(BINDIR)/test_radar

$(BINDIR)/test_random : test_random
	install -t $(BINDIR) test_random

$(BINDIR)/test_radar : test_radar
	install -t $(BINDIR) test_radar

clean :
	-rm -f test_random test_radar

remove :
	-rm -f $(BINDIR)/test_random $(BINDIR)/test_radar


