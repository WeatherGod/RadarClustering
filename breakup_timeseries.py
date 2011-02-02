import datetime
import glob
import os

dir = "data/PAR_20090514"
threshold = 300

files = glob.glob("%s%sPAR_*_rast.nc" % (dir, os.sep))
files.sort()
times = [datetime.datetime.strptime(name, dir + os.sep + "PAR_%Y%m%d_%H%M%S_rast.nc") for name in files]

newdir_cnt = 0
newdir_startIndex = 0

for index in range(len(files) - 1) :
    if (times[index + 1] - times[index]).seconds > threshold :
        # Time to move these guys to a new directory.
        newdir = "%s_Part%0.2d%s" % (dir, newdir_cnt, os.sep)
        os.mkdir(newdir)
        for aFile in files[newdir_startIndex:index + 1] :
            newname = newdir + os.path.basename(aFile)
            os.symlink(os.path.realpath(aFile), newname)

        newdir_cnt += 1
        newdir_startIndex = index + 1

if newdir_startIndex != len(files) :
    # Time to move these guys to a new directory.
    newdir = "%s_Part%0.2d%s" % (dir, newdir_cnt, os.sep)
    os.mkdir(newdir)
    for aFile in files[newdir_startIndex:] :
        newname = newdir + os.path.basename(aFile)
        os.symlink(os.path.realpath(aFile), newname)
