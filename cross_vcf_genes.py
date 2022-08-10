#!/usr/bin/env python

## cross_vcf_genes.py
## Description :    compute occurences of genes from a list of VCF files.
## Usage : python  cross_vcf_genes.py -i </path/to/the/input/list/of/vcf/file>
## Output : TSV format on stdout containing all genes and their frequency in the cohort, and the list of involved samples
## Requirements : python 2.7+ ; getopt package
## Author : Yannis Duffourd
## Creation Date : 2020-08-10
## last revision date : 2022-08-10
## Known bugs : none

"""Usage: python cross_vcf_genes.py -f <list_of_vcf.list> """

import os
import sys
import getopt


allGeneSeen = {}


opts, args = getopt.getopt(sys.argv[1:], 'f:')
for opt, arg in opts:
	if opt in ("-f"):
		fileList = arg

for currentFile in open( fileList , 'r' ):
	currentFile = currentFile.strip()
	currentStream = open( currentFile , 'r' )
	tmp = currentFile
	for line in currentStream :
		splice = 0
		gene = ""
		line = line.strip()
		# pass headers
		if line.startswith( "##" ):
			continue

		# get sample name
		if line.startswith( "#CHROM" ):
			sample = line.split( "\t" )[9]
			continue

		# get gene in info field
		info = line.split( "\t" )[7]
		for elt in info.split( ";" ):
			if elt.startswith( "GL=" ):
				gene = elt.split( "=" )[1]
		# clean gene name
		if gene.find( "/" ):
			for tmp in gene.split( "/" ):
				if allGeneSeen.has_key( tmp ):
					if sample not in allGeneSeen[tmp]:
						allGeneSeen[tmp].append( sample )
				else:
					allGeneSeen[tmp] = []
					allGeneSeen[tmp].append( sample )
		else :
			if allGeneSeen.has_key( gene ):
				if sample not in allGeneSeen[gene]:
					allGeneSeen[gene].append( sample )
			else:
				allGeneSeen[gene] = []
				allGeneSeen[gene].append( sample )
	currentStream.close


for elt in allGeneSeen.keys( ):
	sys.stdout.write( "%s\t%s\t%s\n" % ( elt , len(set( allGeneSeen[elt] ) ) , ",".join( set( allGeneSeen[elt] ) ) ) )
