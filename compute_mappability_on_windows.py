#!/usr/bin/env python

# script to calculate mappability on windows
# need a mappability file (-m) and an bed file (-i) as input

import sys
import getopt
import os
from GeneralTools import Argms

# -i interval
# -m mappability

argm = Argms('i:m:')

intervalFile = argm["-i"]
mappabilityFile = argm["-m"]

# get the mappability in memory
mappAll = {}
mapStream = open( mappabilityFile, 'r' )
sys.stderr.write( "Starting parsing of mappability file : %s ..." % mappabilityFile )
for line in mapStream:
    tempDict = {}
    if not line.startswith( "#" ):
        allField = line.strip( ).split( '\t' )
        #sys.stderr.write( "%s\t=>\t%s\t%s\t%s\t%s\n" % ( line.strip() , allField[0] , allField[1] , allField[2] , allField[3] )  )
        if allField[0] not in mappAll.keys():
            mappAll[ allField[0] ] = {}

        for pos in range( int( allField[1] ) , int( allField[2] ) ):
            mappAll[ allField[0] ][pos] = allField[3]

mapStream.close()
sys.stderr.write( " done with %s entries\n" % ( len(  mapAll.keys() ) ) )
# parse our intervals
intervalStream = open( intervalFile , 'r' )

sys.stderr.write( "Starting parsing of interval file : %s ..." % intervalFile )

sys.stdout.write( "#chr\tstart\tend\treadcount\tmappability\n" )

for line in intervalStream:
    valueOne = 0
    valueTwo = 0
    valueMean = 0
    if not line.startswith( "#" ):
        #sys.stderr.write( "# New line\n" )
        chrom = line.split('\t')[0]
        start = int( line.split('\t')[1] )
        end = int( line.split('\t')[2] )
        nbPos = 0;
        for pos in range( start , end ):
            valueMean += mappAll[ allField[0] ][pos]
            nbPos += 1

        valueMean /= nbPos



        #sys.stderr.write( "value One : %s - value Two : %s\n" % ( valueOne , valueTwo ) )
        sys.stdout.write( "%s\t%s\n" % ( line.strip() , valueMean ) )




sys.stderr.write( " done\n" )
