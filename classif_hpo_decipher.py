#!/usr/bin/python

# script to cluster patient based on hpo
# using decipher extract as base
# using an extract of phenotips from your patients to cluster with decipher patient and get potential genes
# using an old version of plotly, need an update ... 


import os
import sys
import getopt
import logging
import json



import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import pandas as pd
import getopt
from scipy import stats
from plotly import tools
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout
import numpy as np
import plotly.figure_factory as ff



decipherFile = ""
outFile = ""
jsonFile = ""


opts, args = getopt.getopt(sys.argv[1:], 'd:o:j:')
for opt, arg in opts:
	if opt in ("-d"):
		decipherFile = arg
	elif opt in ("-o"):
		outFile = arg
	elif opt in ("-j"):
		jsonFile = arg


newData = {}
model = {}
allTerms = []

logging.basicConfig(filename = 'log' , filemode = 'w', level = logging.INFO, format = '%(asctime)s %(levelname)s - %(message)s')
logging.info('start')

def parse_decipher( incFile ):
	global model
	global allTerms
	for line in open( incFile , 'r' ):
		if line.startswith( "gene" ):
			continue
		line = line.strip( '\n' )
		gene = line.split( "," )[0]
		hpoList = line.split( "," )[7]
		if hpoList == "":
			continue


		if not model.has_key( gene ):
			model[gene] = {}
			for term in hpoList.split( ";" ):
				if not term.startswith( "HP:" ):
					continue
				model[gene][term] = 1

		else:
			logging.warning('Key gene %s has multiple entries' % gene)


def make_term_list( ):
	global model
	global allterms
	global newData
	for gene in model.keys():
		for term in model[gene].keys():
			if term not in allTerms:
				allTerms.append( term )

	for ped in newData.keys():
		for term in model[gene].keys():
			if term not in allTerms:
				allTerms.append( term )



def write_model():
	outStream = open( outFile , "w" )
	# header
	outStream.write( "#gene" )
	for term in allTerms :
		outStream.write( "\t%s" % term )
	outStream.write( "\n" )

	for gene in model.keys():
		outStream.write( "%s" % gene )
		for term in allTerms :
			if model[gene].has_key( term ):
				outStream.write( "\t%s" % "1" )
			else:
				outStream.write( "\t%s" % "0" )
		outStream.write( "\n" )

	outStream.close()


# parse phenotips JSON.
def parse_phenotips():
	global allTerms
	global model
	global newData
	sys.stderr.write( "Parsing phenotips JSON ..." )

	data = {}
	with open( jsonFile ) as f:
		data = json.load(f)

	sys.stderr.write( "OK\n" )

	sys.stderr.write( "Checking PED... \n" )

	for i in data:
		exclude = False
		PED = i['external_id']
		sys.stderr.write( "Ped : %s\n" % PED )
		hlist = []
		for a in i["features"]:
			if a.has_key( "id" ):
				sys.stderr.write( "HP term %s added dor patient : %s\n" % (a["id"] ,  PED ) )
				if not a["id"].startswith( "HP:" ):
					continue
				else:
					hlist.append( a["id"] )





		#  is it a solved case ?
		if i.has_key( "gene" ):
			gene =i["gene"]
			if model.has_key( gene ) :
				a = 0
				while model.has_key( gene ) :
					gene = gene + "." + str( a )
					a += 1


			model[gene] = {}
			for term in hlist:
				model[gene][term] = 1


		else:
			newData[PED] = {}
			for term in hlist:
				newData[PED][term] = 1


def Clustering( ):
	sys.stderr.write( "Starting Clustering\n" )
	global allTerms
	global newData
	global model

	# dendrogram for clustering sample on HPO Term.

	# get size of array
	x = len( model.keys() ) + len( newData.keys() )
	y = len( allTerms )

	# create numpy array
	X = np.empty( [x,y] )

	x = 0
	# the model
	for gene in model.keys()  :
		#sys.stderr.write( "\gene %s\n" % ( gene ))
		y = 0
		for term in allTerms:
			if model[gene].has_key( term ):
				X[x,y] = 1
			else:
				X[x,y] = 0
			y += 1
		x+= 1

	# the data
	for ped in newData.keys()  :
		#sys.stderr.write( "\gene %s\n" % ( gene ))
		y = 0
		for term in allTerms:
			if newData[ped].has_key( term ):
				X[x,y] = 1
			else:
				X[x,y] = 0
			y += 1
		x+= 1

	lab = model.keys() + newData.keys()

	# draw
	fig = ff.create_dendrogram(X, orientation='left', labels= lab)
	fig['layout'].update({'width':2000, 'height':2000})
	plot(fig, filename='clustering.html', auto_open = False)
	sys.stderr.write( "End of Clustering\n" )



# main
def main():
	parse_decipher( decipherFile )
	parse_phenotips()

	make_term_list()
	write_model()
	Clustering()

if __name__ == "__main__":
	main()
