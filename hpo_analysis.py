#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import logging
import json
import simplejson
import unicodedata

outFile = "" 
jsonFile = "" 
pedFile = ""
hpoFile = ""
global d 
d = {}
global HPO 
HPO = {}
global parents 
parents = {}
global ped 
ped = []



stop_terms = { 
"HP:0001507" : "Growth abnormality" ,
"HP:0004322" : "Short stature",
"HP:0000098" : "Tall stature",
"HP:0004325" : "Decreased body weight" ,
"HP:0004324" : "Increased body weight",
"HP:0000252" : "Microcephaly",
"HP:0000256" : "Macrocephaly",
"HP:0000271" : "Abnormality of the face",
"HP:0001999" : "Abnormal facial shape",
"HP:0000478" : "Abnormality of the eye",
"HP:0000598" : "Abnormality of the ear",
"HP:0002086" : "Abnormality of the respiratory system",
"HP:0002643" : "Neonatal respiratory distress",
"HP:0003011" : "Abnormality of the musculature",
"HP:0011398" : "Central hypotonia",
"HP:0025031": "Abnormality of the digestive system" , 
"HP:0000119" : "Abnormality of the genitourinary system",
"HP:0001263" : "Global developmental delay",
"HP:0000707" : "Abnormality of the nervous system", 
"HP:0012638" : "Abnormality of nervous system physiology", 
"HP:0012639" : "Abnormality of nervous system morphology",
"HP:0002342" : "Intellectual disability, moderate",
"HP:0001249" : "Intellectual disability",
"HP:0010864" : "Intellectual disability, severe", 
"HP:0006889" : "Intellectual disability, borderline",
"HP:0001256" : "Intellectual disability, mild", 
"HP:0002187" : "Intellectual disability, profound" , 
"HP:0000708" : "Behavioral abnormality" ,
"HP:0000717" : "Autism" , 
"HP:0002011" : "Morphological abnormality of the central nervous system",
"HP:0001298" : "Encephalopathy",
"HP:0001263" : "Global developmental delay",
"HP:0012736" : "Profound global developmental delay",
"HP:0011344" : "Severe global developmental delay" , 
"HP:0011343" : "Moderate global developmental delay" , 
"HP:0011342" : "Mild global developmental delay" , 
"HP:0001250" : "Seizures", 
"HP:0001257" : "Spasticity", 
"HP:0001251" : "Ataxia",
"HP:0001332" : "Dystonia", 
"HP:0100022" : "Abnormality of movement" , 
"HP:0001197" : "Abnormality of prenatal development or birth",
"HP:0001622" : "Premature birth" , 
"HP:0001871" : "Abnormality of blood and blood-forming tissues", 
"HP:0001873" : "Thrombocytopenia", 
"HP:0001939" : "Abnormality of metabolism/homeostasis",
"HP:0003549" : "Abnormality of connective tissue", 
"HP:0000951" : "Abnormality of the skin", 
"HP:0001626" : "Abnormality of the cardiovascular system",
"HP:0002715" : "Abnormality of the immune system",
"HP:0000818" : "Abnormality of the endocrine system",
"HP:0000769" : "Abnormality of the breast", 
"HP:0001608" : "Abnormality of the voice" }




opts, args = getopt.getopt(sys.argv[1:], "j:p:h:o:", [ "json" , "ped" , "hpo" , "output" ] )

for o, a in opts:
	if o in ("-h", "--hpo"):
		hpoFile = a
	elif o in ("-p", "--ped"):
		pedFile = a
	elif o in ("-j", "--json"):
		jsonFile = a
	elif o in ("-o", "--output"):
		outFile = a
	else:
		assert False, "unhandled option"





def display_sample( incElt ) :
	sys.stderr.write( "%s\n" % json.dumps(incElt, sort_keys=True, indent=4, separators=(',', ': ') , ensure_ascii=False   ) )



# parse phenotips JSON.
def parse_phenotips():
	global d 
	global ped 
	sys.stderr.write( "Parsing phenotips JSON ..." )

	data = {}
	with open( jsonFile ,'r' ) as f:
		data = simplejson.load(f)

	sys.stderr.write( "OK\n" )

	sys.stderr.write( "Parsing features for each PED...\n" )

	for i in data:
		id_list = []
		if 'external_id' in i:
			PED = i['external_id']
			PED = unicodedata.normalize('NFKD', PED).encode('ascii','ignore')
			sys.stderr.write( "external id : %s\n" % PED )
			
			if not (PED in ped) :
				sys.stderr.write( "\t%s not found in ped list\n" % PED ) 
				continue
			
			if 'features' in i:
				features = i['features']
				for j in features:
					if j['observed'] == 'yes':
						id_list.append(str(j['id']))
				d[PED]["terms"] = id_list

	sys.stderr.write( "OK\n" )


# parse HPO terms from hpo.obo file
def parse_HPO():
	global HPO
	global parents
	sys.stderr.write( "Parsing HPO term tree..." )

	for line in open( hpoFile ):
		line = line.strip()
		# ~ sys.stderr.write( "%s\n" % line )
		if not line: continue #Skip empty
		if line.startswith("id"):
			hpo_id = line.split()[1]
			HPO.setdefault(hpo_id, {})
			if hpo_id == "HP:0000001":
				parents[hpo_id] = "All"
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


def is_in_parents( term , stopTerm ):
	global HPO
	if not HPO.has_key( term ):
		sys.stderr.write( "%s not found in the tree \n" % term )
		return False
	# ~ sys.stderr.write( "Looking for %s from %s in tree : \n" % ( stopTerm , term ) )
	# ~ sys.stderr.write( "\tpath : %s" % term  )
	
	newTerm = term
	
	while newTerm != stopTerm:
		newTerm = HPO[newTerm]["is_a"]
		# ~ sys.stderr.write( " - %s" % newTerm ) 
		# if we get to the root, term wasn't found
		if newTerm == "HP:0000001" :
			# ~ sys.stderr.write( "\t NOT FOUND\n" )
			
			return False
	
	# if we get out of the while loop : term was found
	# ~ sys.stderr.write( "\t FOUND\n" )
	return True	
		
		


# parse patient list to be selected
def parse_ped_list():
	global ped 
	global d 
	sys.stderr.write( "Parsing selected ped list ..." )
	for line in open( pedFile ):
		line = line.strip()
		ped.append( line )
		sys.stderr.write( "\tAdding ped : %s\n" % line ) 
		d[line] = {}
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
	global d
	global ped 
	sys.stderr.write( "Counts HPO term for each selected patient...\n" )
	for patient in ped:
		sys.stderr.write( "Patient : %s:\n" % patient )
		if not d.has_key( patient ):
			sys.stderr.write( "\tWARNING : patient %s not found in json\n" % patient )
			continue
		
		#  fill the table for all patients 
		for elt in stop_terms.keys() :
			d[patient][elt] = 0
		
		
		for t in d[patient]["terms"] :
			for elt in stop_terms.keys() : 
				if (  is_in_parents( t, elt ) ):
					d[patient][elt] = 1
				
	sys.stderr.write( " ... OK\n" )




# write result in outputfile in a csv format
def print_result():
	global d
	
	ostream = open( outFile , "w" )
	ostream.write( "#patient") 
	for elt in stop_terms.keys() :
		ostream.write( "\t%s" % (elt + ":" + stop_terms[elt] ) )
	ostream.write( "\n")
	
	for p in d.keys():
		ostream.write( "%s" % p )
		for elt in stop_terms.keys() :
			ostream.write( "\t%s" % (d[p][elt]) )
		ostream.write( "\n")
		
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

	parse_HPO()

	parse_ped_list()
	
	parse_phenotips()
	
	summarize_hpo_counts()
	
	print_result()
	




if __name__ == "__main__":
	main()


