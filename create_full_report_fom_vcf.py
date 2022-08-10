#!/usr/bin/python

# take a VCF and turn it into a clean tsv file


import os
import sys
import getopt
import logging



inFile = ""
outFile = ""
samples = []

opts, args = getopt.getopt(sys.argv[1:], 'i:o:')
for opt, arg in opts:
	if opt in ("-i"):
		inFile = arg
	elif opt in ("-o"):
		outFile = arg

infoDict = {}
formatDict = {}
result = []

for line in open(inFile):
	sys.stderr.write( "%s" % line )
	if line.startswith('##'):
		line = line.replace( "##" , "" )
		if line.startswith( "INFO" ):
			line = line.replace( "INFO=<" , "" )
			line = line.replace( ">", "" )
			tab = line.split( "," )
			for elt in tab:
				if elt.startswith( "ID=" ):
					ID = elt.split( "=" )[1]
				if elt.startswith( "Description=" ):
					Desc = elt.split( "=" )[1]
			infoDict[ID] = Desc

		if line.startswith( "FORMAT" ):
			line = line.replace( "FORMAT=<" , "" )
			line = line.replace( ">", "" )
			tab = line.split( "," )
			for elt in tab:
				if elt.startswith( "ID=" ):
					ID = elt.split( "=" )[1]
				if elt.startswith( "Description=" ):
					Desc = elt.split( "=" )[1]
			formatDict[ID] = Desc
	elif line.startswith('#'):
		tab = line.split( "\t" )
		for elt in tab[9:]:
			samples.append( elt.strip() )
	else:
		temp = {}
		for k in infoDict.keys():
			temp[k] = "."
		for k in formatDict.keys():
			for i in samples:
				temp[i + "_" + k] = "."


		temp["chr"] = line.split( "\t" )[0]
		temp["position"] = line.split( "\t" )[1]
		temp["ref"] = line.split( "\t" )[3]
		temp["alt"] = line.split( "\t" )[4]

		infoTmp = line.split( "\t" )[7]
		tab = infoTmp.split( ";" )
		for elt in tab :
			t = elt.split( "=" )[0]
			if elt.find( "=" ) != -1:
				temp[t] = elt.split( "=" )[1]
			else:
				temp[t] = "1"


		formatTmp = line.split( "\t" )[8]
		formatPos = {}
		tab = formatTmp.split( ":" )
		pos = 0
		for elt in tab :
			formatPos[pos] = elt
			pos += 1

		pos = 9
		for e in line.split( "\t" )[9:]:
			samp = samples[ pos - 9 ]
			rpos = 0
			for c in e.split( ":" ):
				fi = formatPos[rpos]
				temp[samp + "_" + fi] = c.strip()
				rpos += 1
			pos += 1


		result.append( temp )



# output
outStream = open(outFile , "w" )
outStream.write( "#Chrom\tPos\tRef\tAlt" )
for elt in infoDict.keys():
	outStream.write( "\t%s" % elt )
for elt in formatDict.keys():
	for i in samples:
		outStream.write( "\t%s" % (i + "_" + elt) )

outStream.write( "\n" )

for elt in result:
	outStream.write( "%s\t%s\t%s\t%s" % ( elt["chr"] , elt["position"] , elt["ref"] , elt["alt"] ) )

	for i in infoDict.keys():
		outStream.write( "\t%s" % elt[i] )

	for a in formatDict.keys():
		for i in samples:
			outStream.write( "\t%s" % (elt[i + "_" + a]) )
	outStream.write( "\n" )


outStream.close()
