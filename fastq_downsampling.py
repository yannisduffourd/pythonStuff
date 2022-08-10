#!/usr/bin/python

# a fastq downsampler 

import getopt
import sys
import os
import gzip
import random
from GeneralTools import Argms

argm = Argms('p:i:o:')

try:
	inFileR1 = argm["-i"]
except KeyError:
	sys.exit("%s" % ("Error: no input file was given"))


try:
	str_percent = argm["-p"]
except KeyError:
	sys.exit("%s" % ("Error: no downsampling value was given"))

try:
	outFileR1 = argm["-o"]
except KeyError:
	sys.exit("%s" % ("Error: no output file was given"))

percent = float( str_percent )
keepList = {}


# inFileR1 is the path to the R1 file, if a R2 file is in the same dir, it will be taken.
doR2 = 0
inFileR2 = inFileR1.replace( "R1" , "R2" )

sys.stderr.write( "Starting downsampling for incoming file %s with %s percent sequenced kept\n"  % ( inFileR1 , percent ) )
sys.stderr.write( "Output file for R1 : %s\n" % outFileR1 )


if os.path.isfile( inFileR2 ):
    doR2 = 1
    sys.stderr.write( "R2 file found\n" )
    outFileR2 = outFileR1.replace( "R1" , "R2" )
    sys.stderr.write( "R2 incoming file : %s \n" % inFileR2 )
    sys.stderr.write( "R2 output file : %s \n" % outFileR2 )
else:
    sys.stderr.write( "R2 file not found\n" )



# Opening file 1
sys.stderr.write( "Start reading R1 input file\n" )
readStream = gzip.open( inFileR1 , 'rb' )
writeStream = gzip.open( outFileR1, 'w' )


lineNumber = 3
seqFound = 0
seqKept = 0

for line in readStream:
    lineNumber += 1

    if( line.startswith( "@" )) and ( (lineNumber % 4) == 0 ):
        # rng
        seqFound += 1
        if (seqFound % 1000000) == 0:
            calcPercent = ( seqKept * 100 ) / seqFound
            sys.stderr.write( "%s reads treated , %s reads kept : %s percent\n" % ( seqFound , seqKept , calcPercent ) )

        if random.randint( 0 , 100 ) <= percent:
            takeIt = 1
            seqKept += 1
            if doR2 == 1:
                keepList[line.split(" ")[0] ] = 1
                #sys.stderr.write( "Keeping : %s \n" % line.split(" ")[0] )
            writeStream.write( line )
        else:
            takeIt = 0
    else:
        if takeIt == 1:
            writeStream.write( line )

readStream.close()
writeStream.close()
calcPercent = ( seqKept * 100 ) / seqFound
sys.stderr.write( "Read 1 finished with %s total sequences and %s kept %s percent \n" % ( seqFound , seqKept , calcPercent ) )

# manage R2

seqFound = 0
seqKept = 0
lineNumber = 3

if doR2 == 1:
    sys.stderr.write( "Now managing Read 2\n" )
    r2Stream = gzip.open( inFileR2 , 'rb' )
    w2Stream = gzip.open( outFileR2, 'w' )

    for line in r2Stream:
        lineNumber += 1
        if( line.startswith( "@" ) ) and ( (lineNumber % 4) == 0 ):
            seqFound += 1

            if (seqFound % 1000000) == 0:
                calcPercent = ( seqKept * 100 ) / seqFound
                sys.stderr.write( "%s reads treated , %s reads kept : %s percent\n" % ( seqFound , seqKept , calcPercent ) )

            if line.split(" ")[0] in keepList:
                takeIt = 1
                seqKept += 1
                w2Stream.write( line )
            else:
                takeIt = 0
        else:
            if takeIt == 1:
                w2Stream.write( line )

    r2Stream.close()
    w2Stream.close()

    sys.stderr.write( "Read 2 finished\n" )
