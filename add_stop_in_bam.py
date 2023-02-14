#!/usr/bin/env python




import os
import sys
import getopt
import pysam 
import math
import threading
import random 

# ~ import matplotlib.pyplot as plt

currentThread = 0
nbThread = 1
downSamplingRate = 0
inputFile = ""
logFile = ""
percent = 0
bannedReads = []

opts, args = getopt.getopt(sys.argv[1:], 'i:p:o:')  
for opt, arg in opts:
	if opt in ("-i"):
		inputFile = arg
	if opt in ("-p"):
		percent = int(arg)
	if opt in ("-o"):
		outputFile = arg
	

def isStop( incCodon ):
	stopList = [ "TAG" , "TAA" , "TGA" ]
	if incCodon in stopList :
		return True 
	else:
		return False



sys.stderr.write( "Parsing bam file : %s ..." % ( inputFile ) )
bamIterRef = pysam.AlignmentFile( inputFile , "r" )
bamOutStream = pysam.AlignmentFile(outputFile, "wb" , template=bamIterRef )

bamCodonReference = {}

n = 0 
m = 0
x = 0 
# samStream = open( samFile , "r" )
for line in bamIterRef:
	x += 1
	#logging.info('########\nNew read to parse : ' + str(line) )
	if line.query_name in bannedReads:
		bamOutStream.write( line )
		continue
	
	
	
	# pass bad alignements
	if (line.is_unmapped == True ) or (line.is_secondary == True ) or (line.is_supplementary == True) or (int(line.mapping_quality) < 30) :
		#~ logging.info('Passing sequence : bad quality ' )
		bamOutStream.write( line )
		continue
	# test CIGAR string : if insertion or deletion, we skip the read
	cigar = line.cigarstring
	if "I" in cigar or "H" in cigar or "S" in cigar or "D" in cigar:
		bamOutStream.write( line )
		continue
	
	ref = line.reference_name
	position = int( line.reference_start) + 1
	sequence = line.query_sequence
	
	currentPosition = position
	# extract codon sequences
	i = 1 
		
	while i < len(sequence) :
		if i + 3 > len( sequence ):
			break
		if currentPosition % 3 == 0 or currentPosition == 1:
			codon = sequence[i:i + 3]
			codon = codon.upper()
			if isStop( codon ):
				takeSequence = False
				bannedReads.append( line.query_name )
				bamOutStream.write( line )
				break
			i += 3
			currentPosition += 3 
		else:
			i += 1
			currentPosition += 1 
	
	if line.query_name in bannedReads:
		continue
	
	# add a stop or not
	n += 1
	if random.randint( 0 , 100 ) <= percent :
		m += 1
		currentPosition = position
		i = 1 
		w = 0
		while i < len(sequence) :
			if i + 3 > len( sequence ):
				break
			if currentPosition % 3 == 0 or currentPosition == 1:
				w += 1
				codon = sequence[i:i + 3]
				codon = codon.upper()
				
				if w >= 2:
					s = list( sequence )
					s[i] = "T" 
					s[i+1] = "A" 
					s[i+2] = "G" 
					sequence  = "".join(s)

					break
				
			else:
				i += 1
				currentPosition += 1 

		line.query_sequence = sequence
		bamOutStream.write( line )
		
	else:
		bamOutStream.write( line )

	
	
	
	
sys.stderr.write( "%s / %s on %s\n" % ( m , n , x ))	
	
	
bamIterRef.close()
bamOutStream.close()


