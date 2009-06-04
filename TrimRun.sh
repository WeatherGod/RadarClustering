#!/bin/csh

set runName = ""
set Usage = "$argv[0] -r=RUNNAME"


# Get the name of the run (-r option)
@ argIndex = 1

while ($argIndex <= $#argv)
   switch ($argv[$argIndex]:q)
      case -r=*:
        set runName = `echo $argv[$argIndex] | sed 's/-r=//'`
        breaksw
      default:
	echo $Usage
        exit 1
   endsw

   @ argIndex++
end

if ($runName == "") then
   echo "ERROR: Missing runname option (-r)"
   exit 1
endif


mogrify -trim +repage PPI/$runName/*_clust.png

exit 0
