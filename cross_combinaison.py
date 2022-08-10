#!/usr/bin/python
# -*- coding: utf-8 -*-

## cross_combination.py
## Description :    compute all combination of 2 genes from a list of VCF files.
##                          used for digenism detection
## Usage : python cross_combination.py -i </path/to/the/input/list/of/vcf/file> -o </path/to/the/output/file>
## Output : TSV file containing all combination and their frequency in the cohort, and the list of involved samples
## Requirements : python 2.7+ ; itertools, getopt packages
## Author : Yannis Duffourd
## Creation Date : 2020-08-10
## last revision date : 2022-08-10
## Known bugs : none


import os
import sys
import getopt
import itertools

inputFile = ""
outputFile = ""
n = 2


opts, args = getopt.getopt(sys.argv[1:], 'i:o:n:')
for opt, arg in opts:
    if opt in ("-i"):
        inputFile = arg
    elif opt in ("-o"):
        outputFile = arg
    elif opt in ("-n"):
        n = int(arg)

data = {}

# compute all combination
count = 0
for f in open(inputFile , "r"):
    tmp = []
    dijex = ""
    f = f.strip()
    dijex = f.split(".")[0]
    count += 1
    sys.stderr.write("Computing file N° %s \n" % count)
    # parse and store all genes from vcf file
    for line in open(f ,"r"):
        line = line.strip()
        if line.startswith("#"):
            continue
        info = line.split("\t")[7]
        for elt in info.split(";"):
            if elt.startswith("GL="):
                genes = elt.split("=")[1]
                for i in genes.split(","):
                    for j in i.split("/"):
                        tmp.append(j)

    tmp = sorted(list(set(tmp)))

    # compute all combination and store it in data
    c = 0
    cn = 0
    for combination in itertools.combinations(tmp, n):
        c += 1
        combi = ",".join(combination)
        if not data.has_key(combi):
            data[combi] = []
            cn += 1
        data[combi].append(dijex)
        # sys.stderr.write("\tadding %s for %s\n" % (combi,dijex))
    sys.stderr.write("\tAdded %s combinations, including %s new combinations\n" % (c,cn))


#output
o = open( outputFile , "w")
sys.stderr.write("Now writing ...\n")
for k in data.keys():
    # sys.stderr.write("\t%s : %s\n" % (k,data[k]))
    if len(data[k]) > 2:
        o.write("%s\t%s\t%s\n" % (k, len(data[k]), ",".join(data[k])))
o.close()


























#
