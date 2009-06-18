#!/bin/csh

set inputFilenames = ""

set runName = ""
set Usage = "$argv[0] -r=RUNNAME INPUTFILE_1 [INPUTFILE_2 ...]"


# Get the name of the run (-r option)
@ argIndex = 1

while ($argIndex <= $#argv)
   switch ($argv[$argIndex]:q)
      case -r=*:
        set runName = `echo $argv[$argIndex] | sed 's/-r=//'`
        breaksw
      default:
        set inputFilenames = ($inputFilenames $argv[$argIndex])
        breaksw
   endsw

   @ argIndex++
end

if ($runName == "") then
   echo "ERROR: Missing runname option (-r)"
   exit 1
endif

if ($#inputFilenames == 0) then
   echo "ERROR: No input file to process.  Run directories not made."
   exit 1
endif

#echo "RunName: $runName"
#echo "InputFiles: $inputFilenames[*]"
#echo "FileCnt: $#inputFilenames"

./newrun.sh $runName:q

set Upper = 0.5
set Lower = 0.9
set Padding = 3
set Reach = 1.5
set SubClust = 1

rm -f runLog.txt

foreach filename ($inputFilenames)
   set outName = `echo $filename:q | sed "s/data.*\//ClustInfo\/$runName\//" | sed 's/.nc$/_clust.nc/' | awk '{ print $1 }'`
   ./test_radar -i $filename:q -o $outName:q -u $Upper -l $Lower -p $Padding -r $Reach -s $SubClust >> runLog.txt
end

