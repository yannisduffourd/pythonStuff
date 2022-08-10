#!/usr/bin/env python

# just a python script to duplicate all line from a file (line by line)

import os
import sys


for line in open( sys.argv[1] , 'r' ):
	sys.stdout.write( "%s" % line )
	sys.stdout.write( "%s" % line )
