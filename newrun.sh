#!/bin/sh

for RunName in $@
do
	mkdir "ClustInfo/$RunName"
	mkdir "PPI/$RunName"
done

