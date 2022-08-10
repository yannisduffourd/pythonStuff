#!/usr/bin/env python



# this script annotate variants with gene4denovo database.
# variant input is 1 variant / line formated like :
# chr:pos	ref/alt
# i.e. chr2:4567890	A/T

# output the same line + the gene4denovo annotaiton



import os
import sys
import getopt
import logging
import json
import simplejson

inputFile = ""
outputFile = ""
gendenovoFile = ""

opts, args = getopt.getopt(sys.argv[1:], 'i:o:g:')
for opt, arg in opts:
	if opt in ("-i"):
		inputFile = arg
	elif opt in ("-g"):
		gendenovoFile = arg
	elif opt in ("-o"):
		outputFile = arg

def display_sample( incElt ) :
	sys.stderr.write( "%s\n" % json.dumps(incElt, sort_keys=True, indent=4, separators=(',', ': ') , ensure_ascii=False   ) )


def create_index( incChr , incPos , incRef , incAlt ):
	return (incChr + ":" + str( incPos ) + incRef + ">" + incAlt )



annotation = {}
# make a dict from gene4denovo

for line in open( gendenovoFile ,'r' ) :
	if line.startswith( "Chr" ) :
		continue

	line = line.strip()
	chrom = line.split( "\t" )[0]
	pos = line.split( "\t" )[1]
	ref = line.split( "\t" )[3]
	alt = line.split( "\t" )[4]



	index = create_index( chrom , pos , ref , alt )

	annotation[index] = line.split( "\t" )[6]
	# ~ sys.stderr.write( "Adding : %s : %s\n" % ( index , line.split( "\t" )[6] ) )

outStream = open( outputFile , "w" )
for line in open( inputFile , 'r' ):
	line = line.strip()
	if line.startswith( "#" ) :
		outStream.write( "%s\tgene4denovo\n" % line )
		continue

	# ~ sys.stderr.write( "testing %s\n" % line.split( "/" )[6] )
	chrom = (line.split( "\t" )[0]).split( ":" )[0]
	pos = (line.split( "\t" )[0]).split( ":" )[1]
	ref = (line.split( "\t" )[1]).split( "/" )[0]

	altTable = ((line.split( "\t" )[1]).split( "/" )[1]).split( "," )

	res = []
	for alt in altTable :

		if ((len( alt ) > 1) and ( len(ref) == 1 )) :
			post = int(pos) + 1
			post = str( post )
			reft  = "-"
			altt = alt[1:]
		elif ( 	(len( alt ) == 1) and ( len(ref) > 1 )) :
			post = int(pos) + 1
			post = str( post )
			reft  = ref[1:]
			altt = "-"
		elif ( 	(len( alt ) > 1) and ( len(ref) > 1 )) :
			if len( alt ) < len( ref ) :
				altt = "-"
				reft = ref[len( alt ):]
				post = int(pos) + len( alt )
				post = str( post )
			if 	len( alt ) > len( ref ) :
				reft = "-"
				altt = alt[len(ref):]
				post = int(pos) + len( ref )
				post = str( post )
		else :
			post = pos
			altt = alt
			reft = ref



		index = create_index( chrom , post , reft , altt )
		# ~ sys.stderr.write( "\tindex : %s\n" % index )

		if annotation.has_key( index ):
			res.append( annotation[index] )
			sys.stderr.write( "Found a match for : %s : %s \n" % (index , annotation[index] ) )

	disp = "."
	if len(res) == 0:
		disp = "."
	else:
		disp = ",".join( res )

	# ~ sys.stderr.write( "%s\n" % disp )

	outStream.write( "%s\t%s\n" % ( line , disp ) )

outStream.close()
