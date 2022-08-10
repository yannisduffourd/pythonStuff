#!/usr/bin/env python
# -*- coding: utf-8 -*-

# script to unannot a VCF file
# annotations which are deleted are not exhaustive...
# you can add more in the tagToEliminate variable by editing the script


import os
import sys
import getopt
import logging
import glob
import re

logging.basicConfig(filename =  "unannot_vcf.log", filemode = 'w', level = logging.INFO, format = '%(asctime)s %(levelname)s - %(message)s')
logging.info('start')

vcfFile = ""
path = ""
outFile = ""

opts, args = getopt.getopt(sys.argv[1:], 'i:p:o:')
for opt, arg in opts:
    if opt in ("-i"):
		vcfFile = arg
    elif opt in ("-o"):
		outFile = arg
		sys.stdout = open( outFile , 'w')
from plotly import tools
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout

incStream  = open( vcfFile , 'r' )


tagToEliminate = [ "DENOVODB" , "CNVLIST" , "GENELISTS" , "GS" , "PLI" , "MISZ" , "ACMG" , "OMIM" , "COSMIC" , "HGMDPHEN" , "HGMDCLASS" , "CLNSIG" , "INTERACTION" , "NEXTPROT" , "PPOS" , "CDSPOS" , "CDNAPOS" , "HGVSP" , "HGVSC" , "RANK" , "BIOTYPE" , "GM" , "TYPE" , "GID" , "GL" , "IMPACT" , "EFFECT" , "ALLELE", "ANN" , "LOF" , "NMD" , "ExAC_AN_Adj" , "ExAC_AC_Adj" , "ExAC_ESP_AC" , "ExAC_ESP_AF_GLOBAL" , "gnomADex_AC" , "gnomADex_AN" , "gnomADge_AC" , "gnomADge_AN" , "dbNSFP_CADD" , "dbNSFP_GERP___RS" , "dbNSFP_Polyphen2_HDIV_score" ]


for line in incStream:
	line = line.strip();

	# headers
	if line.startswith( "##" ):
		if line.find( "SnpSift" ) != -1:
			continue
		if line.find( "SnpEff" ) != -1:
			continue

		for elt in tagToEliminate:
			if line.find( elt ) != -1:
				continue
		sys.stdout.write( "%s\n" % line )
		continue

	if line.startswith( "#CHROM" ):
		sys.stdout.write( "%s\n" % line )
		continue



	sys.stdout.write( "%s\t" % "\t".join( line.split("\t")[:7] ) )

	# info
	info = line.split("\t")[7]
	infotoRewrite = []
	for elt in info.split( ";" ) :

		tag = ""
		if elt.find( "=" ) != -1:
			tag = elt.split( "=" )[0]
		else:
			tag = elt

		if tag in tagToEliminate:
			continue
		else:
			infotoRewrite.append( elt )

	sys.stdout.write( "%s\t" % ";".join( infotoRewrite ) )


	sys.stdout.write( "%s\n" % "\t".join( line.split("\t")[8:] ) )



incStream.close()
