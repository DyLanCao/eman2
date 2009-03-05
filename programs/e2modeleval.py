#!/usr/bin/env python

from EMAN2 import *
from optparse import OptionParser
from math import *
import time
import os
import sys
from pprint import pprint
import numpy

resDefs={'ALA':2.0, 'ARG':7.0, 'ASN':4.0, 'ASP':4.0, 'CYS':3.0, 'GLU':5.0, 'GLN':5.0, 'GLY':1.0, 'HIS':5.0, 'ILE':4.0, 'LEU':4.0, 'LYS':6.0, 'MET':5.0, 'PHE':6.0, 'PRO':2.0, 'SER':3.0, 'THR':3.0, 'TRP':6.0, 'TYR':7.0, 'VAL':3.0}


def main():
	progname = os.path.basename(sys.argv[0])
	usage = """%prog [options] input.pdb input.mrc apix threshold
	
Evaluates density at C-alpha positions from a model"""

	parser = OptionParser(usage=usage,version=EMANVERSION)

	(options, args) = parser.parse_args()
	if len(args)!=4 : parser.error("Input MRC, Input PDB, apix and threshold required")

	print args
	try : inMRC=open(args[0],"r")
	except : parser.error("Cannot open mrc file")
	
	try : inPDB=open(args[1],"r")
	except : parser.error("Cannot open PDB file")

	try : apix=float(args[2])
	except : parser.error("no valid a/pix")
	
	try : thresh=float(args[3])
	except : parser.error("no valid threshold")	
	
	inputmrc=EMData()
	inputmrc.read_image(args[0])
	inputmrc.process("threshold.binary", {'value':thresh})
	outfile=open("modeleval.pdb","w")
	
	# parse the pdb file 
	x=[]
	y=[]
	z=[]
	resID=[]

	print "reading pdb"
	lines=[]
	for line in inPDB:
		if line[:4]=='ATOM':
			if line[11:15].strip() =="CA":
				lines.append(line)
				x.append((float(line[30:38].strip())-inputmrc["origin_row"])/apix)
				y.append((float(line[38:46].strip())-inputmrc["origin_col"])/apix)
				z.append((float(line[46:54].strip())-inputmrc["origin_sec"])/apix)
				resID.append(line[17:20].strip())
	#do watershed where seeds are x,y,z
	print "doing watershed"
	watershed = inputmrc.process("watershed",{"xpoints":x,"ypoints":y,"zpoints":z,"minval":thresh})
	print "done watershed"
	watershed.write_image("watershed.mrc")

	#calculate 2nd moments of density segment

	index = 0
	while index < len(resID):
		v = Vec3i(int(x[index]),int(y[index]),int(z[index]))
		pixels=watershed.mask_contig_region(index+1,v)
		max_length = 0
		for i in range(len(pixels)):
			for j in range(i+1,len(pixels)):
				length = (pixels[i]-pixels[j]).length()
				if length > max_length: max_length = length
		
		#print resID[index], index+1, max_length, max_length/resDefs[resID[index]]
		score=max_length/resDefs[resID[index]]
		outfile.write(lines[index][:60]+"%6.2f"%(score)+"\n")
		
		index=index+1
		
	outfile.close()

	
	

				
if __name__ == "__main__":
    main()
