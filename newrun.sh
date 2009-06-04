#!/bin/sh

for RunName in $@
do
	mkdir "clustInfo/$RunName"
	mkdir "PPI/$RunName"
	mkdir "ClustHisto/$RunName"
done

