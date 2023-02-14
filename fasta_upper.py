#!/usr/bin/env python3

# turn a fasta file into a fasta file with all bases/AA in upper case

import getopt
import os
import sys

outputFile = ""
inputFile = ""


opts, args = getopt.getopt(sys.argv[1:], 'i:o:')
for opt, arg in opts:
    if opt in ("-o"):
        outputFile = arg
    elif opt in ("-i" ):
        inputFile = arg

if outputFile != "":
    sys.stdout = open(outputFile, 'w')



for line in open( inputFile , "r"):
    line = line.strip()
    if line.startswith(">"):
        sys.stdout.write("%s\n" % line)
    else:
        sys.stdout.write("%s\n" % line.upper())


















#
