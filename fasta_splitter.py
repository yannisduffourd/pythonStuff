#!/usr/bin/env python

# this script separate a multifast file into single fasta, one per described contig



import os
import sys
import getopt
import logging


inputFile = ""
logFile = ""

opts, args = getopt.getopt(sys.argv[1:], 'i:e:')
for opt, arg in opts:
	if opt in ("-i"):
		inputFile = arg
	elif opt in ("-e"):
		logFile = arg


def fasta_splitter(incFile):
    fastaInStream = open(incFile, "r")
    fastaOutStream = ""
    isBegining = True
    for line in fastaInStream:
        line = line.strip()
        if line.startswith(">"):
            if not isBegining:
                fastaOutStream.close()
            
            f = line.replace(">" , "")
            f = f.split(" ")[0]
            fastaOutStream = open( f + ".fa" , "w")
            isBegining = False
        fastaOutStream.write("%s\n" % line)
    fastaOutStream.close()










# main
def main():
    fasta_splitter(inputFile)


if __name__ == "__main__":
    main()
