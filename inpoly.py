import numpy


def point_inside_polygon(pnts, poly):

    n = len(poly)
    pnts = numpy.array(pnts)
    inside = numpy.zeros(len(pnts), dtype=bool)

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]

        locs = numpy.logical_and(numpy.logical_and(numpy.logical_and(
				 pnts[:, 1] > min(p1y,p2y), 
				 pnts[:, 1] <= max(p1y, p2y)),
				 pnts[:, 0] <= max(p1x,p2x)),
                                 numpy.logical_or(p1x == p2x, 
						  pnts[:, 0] <= ((pnts[:, 1] - p1y)*(p2x-p1x)/(p2y-p1y)+p1x)))
        inside[locs] = numpy.logical_not(inside[locs])
        p1x,p1y = p2x,p2y

    return inside
