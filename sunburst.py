#! /usr/bin/python

# generate a csv file containing information to be displayed by the js code : sequence.js
# need a json from phenotips containing patient ID and observations
# need an extraction of HPO : hp.obo
# need a list of patient. (could be avoid by bypassing the function call in main (involving a code modification))


import json
import simplejson
import sys
import os
import getopt
from colour import Color



opts, args = getopt.getopt(sys.argv[1:], "j:p:h:o:", [ "json" , "ped" , "hpo" , "output" ] )
logDir = "."
hpoFile = ""
pedFile = ""
jsonFile = ""
outputFile = ""
d = {}
HPO = {}
ped = []
result = {}
parents = {}
colors = {
"HP:0001871" : "red" ,
"HP:0003549" : "blue",
"HP:0001197" : "red",
"HP:0001574" : "green",
"HP:0003011" : "lime green",
"HP:0000598" : "salmon",
"HP:0000707" : "purple",
"HP:0000769" : "orange",
"HP:0045027" : "brown",
"HP:0001507" : "blue violet",
"HP:0001939" : "coral1",
"HP:0002086" : "chartreuse2",
"HP:0000818" : "orchid1",
"HP:0000152" : "pink",
"HP:0002715" : "gold",
"HP:0001608" : "cyan",
"HP:0000119" : "cornsilk2",
"HP:0002664" : "tomato",
"HP:0040064" : "grey",
"HP:0025031" : "forest green",
"HP:0000924" : "yellow" ,
"HP:0025142" : "bisque",
"HP:0001626" : "khaki",
"HP:0000478" : "steel blue",
"HP:0025354" : "linen",
"HP:0500014" : "indian red"
}

#  the list of terms where the tree won't be browse
stop_terms = [ "HP:0001871" , "HP:0003549" , "HP:0001197" , "HP:0001574" , "HP:0003011" , "HP:0000598" , "HP:0000707" , "HP:0000769" , "HP:0045027" , "HP:0001507", "HP:0001939" , "HP:0002086" , "HP:0000818" , "HP:0000152","HP:0002715","HP:0001608","HP:0000119","HP:0002664","HP:0040064","HP:0025031","HP:0000924" ,"HP:0025142" , "HP:0001626" , "HP:0000478" , "HP:0025354" , "HP:0500014" ]



for o, a in opts:
	if o in ("-h", "--hpo"):
		hpoFile = a
	elif o in ("-p", "--ped"):
		pedFile = a
	elif o in ("-j", "--json"):
		jsonFile = a
	elif o in ("-o", "--output"):
		outputFile = a
	else:
		assert False, "unhandled option"

#file = 'phenotips_2016-12-23_05-10.json'
#file2 = 'hp.obo'
#file3 = 'PEDpatients-annee1'



def display_sample( incElt ) :
	sys.stderr.write( "%s\n" % json.dumps(incElt, sort_keys=True, indent=4, separators=(',', ': ') , ensure_ascii=False   ) )



# parse phenotips JSON.
def parse_phenotips():

	sys.stderr.write( "Parsing phenotips JSON ..." )

	data = {}
	with open( jsonFile ,'r' ) as f:
		data = simplejson.load(f)

	sys.stderr.write( "OK\n" )

	sys.stderr.write( "Counting features for each PED..." )

	for i in data:
			id_list = []
			if 'external_id' in i:
					PED = i['external_id']
					if 'features' in i:
							features = i['features']
							for j in features:
									if j['observed'] == 'yes':
											id_list.append(str(j['id']))
							d[PED] = id_list







	sys.stderr.write( "OK\n" )


# parse HPO terms from hpo.obo file
def parse_HPO():
	sys.stderr.write( "Parsing HPO term tree..." )

	for line in open( hpoFile ):
		line = line.strip()
		# ~ sys.stderr.write( "%s\n" % line )
		if not line: continue #Skip empty
		if line.startswith("id"):
			hpo_id = line.split()[1]
			HPO.setdefault(hpo_id, {})
			if hpo_id == "HP:0000001":
				parents[hpo_id] = "root"
		if line.startswith("is_a"):
			is_a = line.split()[1]
			HPO[hpo_id]["is_a"] = is_a
			parents[hpo_id] = is_a


		if line.startswith("name"):
			name = line.split(": ")[1]
			HPO[hpo_id]["name"] = name
		if line.startswith("is_obsolete"):
			obso = line.split(": ")[1]
			HPO[hpo_id]["is_obsolete"] = obso



	sys.stderr.write( "OK\n" )

# return a path in the tree from the provided tree to a stop term
def browse_hpo_tree( term ):
	temp = []
	temp.append( term )
	while term not in stop_terms:
		if not HPO.has_key( term ):
			sys.stderr.write( "%s not found in the tree \n" % term )
			break

		if not HPO[term].has_key( "is_a" ) :
			sys.stderr.write( "%s hasn't any is_a key : isolated tree part\n" % term )
			break

		term = HPO[term]["is_a"]
		temp.append(term)


	return "-".join( reversed(temp) )

# second method of tree browsing : allow the path to be always the same (including several parents for a child)
def browse_hpo_parents( term ):
	temp = []
	temp.append( term )
	while term not in stop_terms:
		if not parents.has_key( term ):
			sys.stderr.write( "%s not found in the parents \n" % term )
			break

		if parents[term] == "root" :
			sys.stderr.write( "Root reached\n" )
			break

		term = parents[term]
		temp.append(term)


	return "-".join( reversed(temp) )


# parse patient list to be selected
def parse_ped_list():
	sys.stderr.write( "Parsing selected ped list ..." )
	for line in open( pedFile ):
		line = line.strip()
		ped.append( line )
	sys.stderr.write( " OK\n" )


### NYI ####
#  write the results of the patients in a json format.
def write_result_as_json():
	sys.stderr.write( "Writing result as a JSON ..." )
	ostream = open( "result.json" , "w" )

	jsonFormated = { "name":"root" , "children" : [] }

	ostream.close()


# counts the terms (leaf) on all selected patients
def summarize_hpo_counts():
	sys.stderr.write( "Counts HPO term for each selected patient...\n" )
	for patient in ped:
		if not d.has_key( patient ):
			sys.stderr.write( "WARNING : patient %s not found in json\n" % patient )
			continue

		for term in d[patient] :
			if not result.has_key( term ):
				result[term] = {}
				result[term]["count"] = 0
				result[term]["path"] = ""
			result[term]["count"] += 1
	sys.stderr.write( " ... OK\n" )


def summarize_patient_counts():
	




# write result in outputfile in a csv format
def print_result():
	ostream = open( outputFile , "w" )
	for elt in result.keys():
		ostream.write( "%s,%s\n" % ( result[elt]["path"] , result[elt]["count"] ) )

	ostream.close()

# write a list of HPO terms used in the analysis.
def write_hpo_terms():
	ostream = open( "hpo.terms.list" , "w" )
	for elt in result.keys():
		for t in result[elt]["path"].split( "-" ):
			ostream.write( "%s\n" % t )
	ostream.close()

# write the HP.explain.js file needed by the index.html
# this file contains the term associated to its description
def write_HPO_explain():
	 ostream = open( "HP.explain.js" , "w" )
	 ostream.write( "var explain = {\n"  )

	 for elt in HPO.keys():
		 ostream.write( "\"%s\" : \"%s\",\n" % ( elt , HPO[elt]["name"] ) )
	 ostream.write( "};"  )
	 ostream.close()

# compute colors from basic colors by generating them to a light gray (at the extremity)
def write_colors():
	ostream = open( "couleur.js" , "w" )
	ostream.write( "var couleurs = {\n"  )


	allcolors = {}
	for i in colors.keys():
		allcolors[i] = []


	for elt in result.keys():
		p = result[elt]["path"]
		pList = p.split( "-" )
		b = pList[0]
		for e in pList:
			if e not in allcolors[b]:
				allcolors[b].append( e )


	for elt in allcolors.keys():
		c = Color( colors[elt] )
		col = list(c.range_to( Color("light gray"), len(allcolors[elt] )))

		for e, f in zip(allcolors[elt], col):
			colors[e] = col




	for elt in colors.keys():
		ostream.write( "\"%s\" : \"%s\",\n" % ( elt , colors[elt] ) )
	ostream.write( "};"  )
	ostream.close()



# main
def main():
	parse_phenotips()
	# display_sample( d )
	parse_HPO()
	# ~ display_sample( HPO )
	parse_ped_list()
	summarize_hpo_counts()
	summarize_patient_counts()

	for elt in result.keys():
		result[elt]["path"] = browse_hpo_parents( elt )
	# ~ display_sample( result )
	print_result()
	write_hpo_terms()
	# ~ write_colors()
	# write the files needed to display the html
	write_HPO_explain()




if __name__ == "__main__":
	main()
