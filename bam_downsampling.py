#!/usr/bin/env python

# simple bam downsampling script. 


import os
import sys
import getopt
import pysam
import logging
import math
import threading
import random
# ~ import matplotlib.pyplot as plt

currentThread = 0
nbThread = 1
downSamplingRate = 0
inputFile = ""
logFile = ""


opts, args = getopt.getopt(sys.argv[1:], 'i:o:d:l:')
for opt, arg in opts:
	if opt in ("-i"):
		inputFile = arg
	elif opt in ("-l"):
		ratioThreshold = int(arg)
	elif opt in ("-o"):
		outputFile = arg
	elif opt in ("-d"):
		downSamplingRate = int( arg )
	elif opt in ("-l"):
		logFile = arg
		sys.stderr = open( logFile, 'w')

sys.stderr.write( "Parsing bam file : %s ..." % ( inputFile ) )
bamIterRef = pysam.AlignmentFile( inputFile , "r" )
bamCodonReference = {}
# samStream = open( samFile , "r" )
bamOutStream = pysam.AlignmentFile(outputFile, "wb" , template=bamIterRef )
for line in bamIterRef:
	#logging.info('########\nNew read to parse : ' + str(line) )
	# pass bad alignements
	if (line.is_unmapped == True ) or (line.is_secondary == True ) or (line.is_supplementary == True) :
		#~ logging.info('Passing sequence : bad quality ' )
		continue


	if random.randint( 0 , 100 ) <= downSamplingRate :
		bamOutStream.write( line )

bamIterRef.close()
bamOutStream.close()
