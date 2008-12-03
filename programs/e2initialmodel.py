#!/usr/bin/env python

#
# Author: Steven Ludtke, 11/30/2008 (ludtke@bcm.edu)
# Copyright (c) 2000-2007 Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#


from EMAN2 import *
from optparse import OptionParser
import random
from math import *
import os
import sys
from e2simmx import cmponetomany
from e2make3d import fourier_reconstruction

class silly:
	"""This class exists so we can pass an object in to fourier_reconstruction"""
	pass

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """%prog [options] 
	Initial model generator"""
	parser = OptionParser(usage=usage,version=EMANVERSION)

	parser.add_option("--input", dest="input", default=None,type="string", help="The name of the image containing the particle data")
	parser.add_option("--iter", type = "int", default=8, help = "The total number of refinement iterations to perform")
	parser.add_option("--tries", type="int", default=1, help="The number of different initial models to generate in search of a good one")
	parser.add_option("--sym", dest = "sym", help = "Specify symmetry - choices are: c<n>, d<n>, h<n>, tet, oct, icos",default="c1")
	parser.add_option("--verbose","-v", type="int", default=0,help="Verbosity of output (1-9)",default=0)

	(options, args) = parser.parse_args()
	verbose=options.verbose

	ptcls=EMData.read_images(options.input)
	if not ptcls or len(ptcls)==0 : parser.error("Bad input file")
	boxsize=ptcls[0].get_xsize()
	if verbose : print "%d particles %dx%d"%(len(ptcls),boxsize,boxsize)

	# angles to use for refinement
	sym_object = parsesym(options.sym)
#	orts = sym_object.gen_orientations("eman",{"delta":7.5})
	orts = sym_object.gen_orientations("eman",{"delta":9.0})

	logid=E2init(sys.argv)
	results=[]
	results_name=numbered_bdb("bdb:initial_models#initial_model")

	# We make one new reconstruction for each loop of t 
	for t in range(options.tries):
		if verbose: print "Try %d"%t
		threed=[make_random_map(boxsize)]		# initial model
		apply_sym(threed[0],options.sym)		# with the correct symmetry
		
		# This is the refinement loop
		for it in range(options.iter):
			E2progress(logid,it*t/float(options.tries*options.iter))
			if verbose : print "Iteration %d"%it
			projs=[threed[it].project("standard",ort) for ort in orts]		# projections
			if verbose>2: print "%d projections"%len(projs)
			
			bss=0.0
			bslst=[]
			for i in range(len(ptcls)):
				sim=cmponetomany(projs,ptcls[i],align=("rotate_translate_flip",{}),alicmp=("frc",{}))
				bs=min(sim)
				#print bs[0]
				bss+=bs[0]
				bslst.append((bs[0],i))
				if verbose>2 : print "align %d \t(%1.3f)\t%1.3g"%(i,bs[0],bss)
				n=sim.index(bs)
				ptcls[i]["match_n"]=n
				ptcls[i]["match_qual"]=bs[0]
				ptcls[i]["xform.projection"]=orts[n]	# best orientation set in the original particle
			
			bslst.sort()					# sorted list of all particle qualities
			bslst.reverse()
			aptcls=[]
			for i in range(len(ptcls)*3/4):
				aptcls.append(ptcls[bslst[i][1]].align("rotate_translate_flip",projs[n],{},"frc",{}))
				if it<2 : aptcls[-1].process_inplace("xform.centerofmass",{})
			
			bss/=len(ptcls)
			if verbose>1 : print "Iter %d \t%1.4g"%(it,bss)

			# Somehow this isn't working  :^(
			#if verbose>1 : print "reconstruct"
			#opt=silly()
			#opt.images=aptcls
			#opt.recon_type="fourier"
			#pad=(boxsize*3/2)
			#pad-=pad%8
			#opt.pad=str(pad)
			#opt.iter=3
			#opt.lowmem=0
			#opt.no_wt=1
			#opt.keepsig=0
			#opt.sym=options.sym
			#opt.keep=0.8
			#opt.ndim=2
			#if verbose>2 : opt.verbose=verbose-2
			#else : opt.verbose=0
			#threed.append(fourier_reconstruction(opt))
			#threed[-1]=threed[-1].get_clip(Region((pad-boxsize)/2,(pad-boxsize)/2,(pad-boxsize)/2,boxsize,boxsize,boxsize))

			pad=(boxsize*3/2)
			pad-=pad%8
			recon=Reconstructors.get("fourier", {"quiet":True,"sym":options.sym,"x_in":pad,"y_in":pad})
			recon.setup()
			for ri in range(3):
				if ri>0 :
					for p in aptcls:
						p2=p.get_clip(Region(-(pad-boxsize)/2,-(pad-boxsize)/2,pad,pad))
						recon.determine_slice_agreement(p2,p["xform.projection"],1)
			
				for p in aptcls:
					p2=p.get_clip(Region(-(pad-boxsize)/2,-(pad-boxsize)/2,pad,pad))
					recon.insert_slice(p2,p["xform.projection"])
			threed.append(recon.finish())
			threed[-1]=threed[-1].get_clip(Region((pad-boxsize)/2,(pad-boxsize)/2,(pad-boxsize)/2,boxsize,boxsize,boxsize))
			threed[-1].process_inplace("normalize.edgemean")
			threed[-1].process_inplace("mask.gaussian",{"inner_radius":boxsize/3.0,"outer_radius":boxsize/12.0})
			threed[-1]["quality"]=bss
#			threed[-1]["quality_projmatch"]=
#			display(threed[0])
#			display(threed[-1])
		#debugging output
			#for i in range(len(aptcls)):
				#projs[aptcls[i]["match_n"]].write_image("x.hed",i*2) 
				#aptcls[i].write_image("x.hed",i*2+1)
		#display(threed[-1])
		#threed[-1].write_image("x.mrc")
		if verbose : print "Model %d complete. Quality = %f"%(t,bss)

		results.append((bss,threed[-1]))
		results.sort()
		
		dct=db_open_dict(results_name)
		for i,j in enumerate(results): dct[i]=j[1]
		dct.close()
		
#		threed[-1].write_image("x.%d.mrc"%t)
		
#		display(aptcls)
			
			
	E2end(logid)


def make_random_map(boxsize):
	"""This will make a map consisting of random noise, low-pass filtered and center-weighted for use
	as a random starting model in initial model generation. Note that the mask is eliptical and has random aspect."""
	
	ret=EMData(boxsize,boxsize,boxsize)
	ret.process_inplace("testimage.noise.gauss",{"mean":0.02,"sigma":1.0})
	ret.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.05})
	ret.process_inplace("xform.centerofmass",{})
#	ret.process_inplace("mask.gaussian",{"inner_radius":boxsize/3.0,"outer_radius":boxsize/12.0})
	ret.process_inplace("mask.gaussian.nonuniform",{"radius_x":boxsize/random.uniform(2.0,5.0),"radius_y":boxsize/random.uniform(2.0,5.0),"radius_z":boxsize/random.uniform(2.0,5.0)})
	
	return ret
	
def apply_sym(data,sym):
	"""applies a symmetry to a 3-D volume in-place"""
	xf = Transform()
	xf.to_identity()
	nsym=xf.get_nsym(sym)
	ref=data.copy()
	for i in range(1,nsym):
		dc=ref.copy()
		dc.transform(xf.get_sym(sym,i))
		data.add(dc)
	data.mult(1.0/nsym)	
	

if __name__ == "__main__":
    main()

