import datetime
import glob
import os


def MoveToNewDir(newdirIndex, dirName, files) :
    newdir = os.path.join("%s_Part%0.2d" % (dirName, newdirIndex), '')
    os.mkdir(newdir)
    for aFile in files :
        newname = newdir + os.path.basename(aFile)
        os.symlink(os.path.realpath(aFile), newname)



if __name__ == '__main__' :
    import argparse
    import os.path

    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs=1,
                        help="Directory containing the timeseries of radar data")
    parser.add_argument("threshold", nargs=1, type=int,
                        help="Threshold number of seconds to allow between frames")

    args = parser.parse_args()

    files = glob.glob(os.path.join(args.dir, "PAR_*_rast.nc"))
    files.sort()
    times = [datetime.datetime.strptime(os.path.basename(name), "PAR_%Y%m%d_%H%M%S_rast.nc") for name in files]

    newdir_cnt = 0
    newdir_startIndex = 0

    for index in range(len(files) - 1) :
        if (times[index + 1] - times[index]).seconds > args.threshold :
            # Time to move these guys to a new directory.
            MoveToNewDir(newdir_cnt, args.dir, files[newdir_startIndex:index + 1])

            newdir_cnt += 1
            newdir_startIndex = index + 1

    if newdir_startIndex != len(files) :
        # Time to move these guys to a new directory.
        MoveToNewDir(newdir_cnt, args.dir, files[newdir_startIndex:])


