#!/usr/bin/env python
#
#  06/01/2015
#  New version.  
#  Data is shrank in few major steps and processed by ali3d_base in small resolution steps.
#
#


from __future__ import print_function
from EMAN2 import *
from sparx import *
from logger import Logger, BaseLogger_Files
import global_def

from mpi   import  *
from math  import  *


import os
import sys
import subprocess
import time
import string
from   sys import exit
from   time import localtime, strftime

def Tracker_print_mrk01(string, myid=0):
	if myid == 0:
		print("I am supposed to be track")
	return

def subdict(d,u):
	# substitute values in dictionary d by those given by dictionary u
	for q in u:  d[q] = u[q]


"""
def cmdexecute(cmd):
	from   time import localtime, strftime
	import subprocess
	outcome = subprocess.call(cmd, shell=True)
	line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
	if(outcome == 1):
		print(  line,"ERROR!!   Command failed:  ", cmd)
		exit()
	else:  print(line,"Executed successfully: ",cmd)
"""

# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def volshiftali(vv, mask3d=None):
	nv = len(vv)
	ni = vv[0].get_xsize()
	if(mask3d == None):
		mask3d = model_circle(ni//2-2, ni, ni, ni)

	for i in xrange(nv):
		Util.mul_img(vv[i], mask3d)
		fftip(vv[i])

	del mask3d
	ps = [[0.,0.,0.] for i in xrange(nv)]
	changed = True
	while(changed):
		a = EMData(ni, ni, ni, False)
		for i in vv:
			Util.add_img(a,i)

		changed = False
		for i in xrange(nv):
			pp = peak_search(ccf(vv[i],a), 1)
			for j in xrange(3):
				if(pp[0][5+j] != ps[i][j]):
					ps[i][j] = pp[0][5+j]
					changed = True

	return ps


def fuselowf(vs, fq):
	n = len(vs)
	for i in xrange(n): fftip(vs[i])
	a = vs[0].copy()
	for i in xrange(1,n):
		Util.add_img(a, vs[i])
	Util.mul_scalar(a, 1.0/float(n))
	a = filt_tophatl(a, fq)
	for i in xrange(n):
		vs[i] = fft(Util.addn_img(a, filt_tophath(vs[i], fq)))
	return


global passlastring, mempernode


# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def hlfmem(x):
	return (len(even_angles(x))*4.*passlastring**2*4./ mempernode - 0.5)**2


def get_pixercutoff(radius, delta = 2.0, dsx = 0.5):
	#  Estimate tolerable error based on current delta and shrink.
	#  Current radius (radi*shrink)
	#  delta - current angular step
	#  dsx   - expected pixel error (generally, for polar searches it is 0.5, for gridding 0.1.
	t1 = Transform({"type":"spider","phi":0.0,"theta":0.0,"psi":0.0})
	t1.set_trans(Vec2f(0.0, 0.0))
	t2 = Transform({"type":"spider","phi":0.0,"theta":delta,"psi":delta})
	t2.set_trans(Vec2f(dsx, dsx))
	return max_3D_pixel_error(t1, t2, radius)


# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def comparetwoalis(params1, params2, thresherr=1.0, radius = 1.0):
	#  Find errors per image
	nn = len(params1)
	perr = 0
	for k in xrange(nn):
		if(max_3D_pixel_error(params1[k], params2[k], r=radius) < thresherr):
			perr += 1
	return perr/float(nn)*100.0


def checkstep(item, keepchecking, myid, main_node):
	if(myid == main_node):
		if keepchecking:
			if(os.path.exists(item)):
				doit = 0
			else:
				doit = 1
				keepchecking = False
		else:
			doit = 1
	else:
		doit = 1
	doit = bcast_number_to_all(doit, source_node = main_node)
	return doit, keepchecking


# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def doXfiles(path, source = "chunk", inparams = "params", params = "params", dest = "X"):
	#  will produce X*.txt and paramsX*.txt
	#  Generate six Xfiles from four chunks and export parameters.  This is hardwired as it is always done in the same way
	#  AB
	#     indices
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"0.txt")))+map(int, read_text_file(os.path.join(path,source+"1.txt"))),   \
		os.path.join(path,dest+"0.txt"))
	#  params
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"00.txt"))+read_text_row(os.path.join(path,inparams+"10.txt")), \
		os.path.join(path,params+dest+"0.txt"))
	#  AC
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"0.txt")))+map(int, read_text_file(os.path.join(path,source+"2.txt"))),   \
		os.path.join(path,dest+"1.txt"))
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"01.txt"))+read_text_row(os.path.join(path,inparams+"20.txt")), \
		os.path.join(path,params+dest+"1.txt"))
	#  AD
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"0.txt")))+map(int, read_text_file(os.path.join(path,source+"3.txt"))),   \
		os.path.join(path,dest+"2.txt"))
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"02.txt"))+read_text_row(os.path.join(path,inparams+"30.txt")), \
		os.path.join(path,params+dest+"2.txt"))
	#  BC
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"1.txt")))+map(int, read_text_file(os.path.join(path,source+"2.txt"))),   \
		os.path.join(path,dest+"3.txt"))
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"11.txt"))+read_text_row(os.path.join(path,inparams+"21.txt")), \
		os.path.join(path,params+dest+"3.txt"))
	#  BD
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"1.txt")))+map(int, read_text_file(os.path.join(path,source+"3.txt"))),   \
		os.path.join(path,dest+"4.txt"))
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"12.txt"))+read_text_row(os.path.join(path,inparams+"31.txt")), \
		os.path.join(path,params+dest+"4.txt"))
	#  CD
	write_text_file( \
		map(int, read_text_file(os.path.join(path,source+"2.txt")))+map(int, read_text_file(os.path.join(path,source+"3.txt"))),   \
		os.path.join(path,dest+"5.txt"))
	write_text_row( \
		read_text_row(os.path.join(path,inparams+"22.txt"))+read_text_row(os.path.join(path,inparams+"32.txt")), \
		os.path.join(path,params+dest+"5.txt"))
	return


# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def	mergeparfiles(i1,i2,io,p1,p2,po):
	#  1 - rescued
	#  2 - good old
	l1 = map(int, read_text_file( i1 ))
	l2 = map(int, read_text_file( i2 ))
	if(l1[0] == 0):
			write_text_file( l2, io)
			for ll in xrange(3):
				p = read_text_row(p2+"%01d.txt"%ll)
				write_text_row(2, po+"%01d.txt"%ll)
	else:
		t = l1 +l2
		for i in xrange(len(t)):
			t[i] = [t[i],i]
		t.sort()
		write_text_file( [t[i][0] for i in xrange(len(t))], io)
		for ll in xrange(3):
			p = read_text_row(p1+"%01d.txt"%ll) + read_text_row(p2+"%01d.txt"%ll)
			write_text_row([p[t[i][1]] for i in xrange(len(t))], po+"%01d.txt"%ll)
	return


def read_fsc(fsclocation, lc, myid, main_node, comm = -1):
	# read fsc and fill it with zeroes pass lc location
	from utilities import bcast_list_to_all, read_text_file
	if comm == -1 or comm == None: comm = MPI_COMM_WORLD
	if(myid == main_node):
		f = read_text_file(fsclocation,1)
		n = len(f)
		if(n > lc+1 ):  f = f[:lc+1] +[0.0 for i in xrange(lc+1,n)]
	else: f = 0.0
	mpi_barrier(comm)
	f = bcast_list_to_all(f, myid, main_node)
	return f


# NOTE: 2015/06/11 Toshio Moriya
# This function seems to be not used
def get_resolution_mrk01(vol, radi, nnxo, fscoutputdir, mask_option):
	# this function is single processor
	#  Get updated FSC curves, user can also provide a mask using radi variable
	import types
	if(type(radi) == int):
		if(mask_option is None):  mask = model_circle(radi,nnxo,nnxo,nnxo)
		else:                           mask = get_im(mask_option)
	else:  mask = radi
	nfsc = fsc(vol[0]*mask,vol[1]*mask, 1.0,os.path.join(fscoutputdir,"fsc.txt") )
	currentres = -1.0
	ns = len(nfsc[1])
	#  This is actual resolution, as computed by 2*f/(1+f)
	for i in xrange(1,ns-1):
		if ( nfsc[1][i] < 0.333333333333333333333333):
			currentres = nfsc[0][i-1]
			break
	if(currentres < 0.0):
		print("  Something wrong with the resolution, cannot continue")
		mpi_finalize()
		exit()
	"""
	lowpass = 0.5
	ns = len(nfsc[1])
	#  This is resolution used to filter half-volumes
	for i in xrange(1,ns-1):
		if ( nfsc[1][i] < 0.5 ):
			lowpass = nfsc[0][i-1]
			break
	"""
	lowpass, falloff = fit_tanh1(nfsc, 0.01)

	return  round(lowpass,4), round(falloff,4), round(currentres,2)


def get_pixel_resolution_mrk01(vol, radi, nnxo, fscoutputdir, mask_option):
	# this function is single processor
	#  Get updated FSC curves, user can also provide a mask using radi variable
	import types
	if(type(radi) == int):
		if(mask_option is None):  mask = model_circle(radi,nnxo,nnxo,nnxo)
		else:                       mask = get_im(mask_option)
	else:  mask = radi
	nx = vol[0].get_xsize()
	if( nx != nnxo ):
		mask = Util.window(rot_shift3D(mask,scale=float(nx)/float(nnxo)),nx,nx,nx)
	nfsc = fsc(vol[0]*mask,vol[1]*mask, 1.0 )
	if(nx<nnxo):
		for i in xrange(3):
			for k in xrange(nx,nnxo/2+1):
				nfsc[i][k].append(0.0)
		for i in xrange(nnxo/2+1):
			nfsc[0][i] = float(i)/nnxo
	write_text_file( nfsc, os.path.join(fscoutputdir,"fsc.txt") )
	ns = len(nfsc[1])
	currentres = -1
	'''
	#  This is actual resolution, as computed by 2*f/(1+f)
	for i in xrange(1,ns-1):
		if ( nfsc[1][i] < 0.333333333333333333333333):
			currentres = nfsc[0][i-1]
			break
	'''
	#  0.5 cut-off
	for i in xrange(1,ns-1):
		if ( nfsc[1][i] < 0.5):
			currentres = i
			break
	if(currentres < 0):
		print("  Something wrong with the resolution, cannot continue")
		mpi_finalize()
		exit()
	"""
	lowpass = 0.5
	ns = len(nfsc[1])
	#  This is resolution used to filter half-volumes
	for i in xrange(1,ns-1):
		if ( nfsc[1][i] < 0.5 ):
			lowpass = nfsc[0][i-1]
			break
	"""
	#lowpass, falloff = fit_tanh1(nfsc, 0.01)
	lowpass = nfsc[0][currentres]
	falloff = 0.2

	return  round(lowpass,4), round(falloff,4), currentres


def compute_resolution_mrk01(stack, outputdir, partids, partstack, radi, nnxo, CTF, mask_option, sym, myid, main_node, nproc):
	import types
	vol = [None]*2
	fsc = [None]*2
	if( type(stack) == list ):
		nx = stack[0].get_xsize()
		nz = stack[0].get_zsize()
	else:
		nz = 1
	if(mask_option is None):  mask = model_circle(radi,nnxo,nnxo,nnxo)
	else:                     mask = get_im(mask_option)


	if myid == main_node :
		print("  compute_resolution    type(stack),outputdir, partids, partstack, radi, nnxo, CTF",type(stack),outputdir, partids, partstack, radi, nnxo, CTF)

		if( type(stack) == list ):
			print("  input is a list ", info(stack[0]) )

	for procid in xrange(2):
		if(type(stack) == str or ( nz == 1 )):
			if(type(stack) == str):
				projdata = getindexdata(stack, partids[procid], partstack[procid], myid, nproc)
			else:
				projdata = stack
			if( procid == 0 ):
				nx = projdata[0].get_xsize()
				if( nx != nnxo):
					mask = Util.window(rot_shift3D(mask,scale=float(nx)/float(nnxo)),nx,nx,nx)

			if CTF:
				from reconstruction import rec3D_MPI
				vol[procid],fsc[procid] = rec3D_MPI(projdata, symmetry = sym, \
					mask3D = mask, fsc_curve = None, \
					myid = myid, main_node = main_node, odd_start = 1, eve_start = 0, finfo = None, npad = 2)
			else:
				from reconstruction import rec3D_MPI_noCTF
				vol[procid],fsc[procid] = rec3D_MPI_noCTF(projdata, symmetry = sym, \
					mask3D = mask, fsc_curve = None, \
					myid = myid, main_node = main_node, odd_start = 1, eve_start = 0, finfo = None, npad = 2)

			if(type(stack) == str):  del projdata
		else:
			#  Volumes
			vol = stack
			nx = vol[0].get_xsize()
			if( nx != nnxo ):
				mask = Util.window(rot_shift3D(mask,scale=float(nx)/float(nnxo)),nx,nx,nx)

		if( myid == main_node):
			vol[procid].write_image(os.path.join(outputdir,"vol%01d.hdf"%procid))
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(  line,"Generated vol #%01d "%procid)

	lowpass    = 0.0
	falloff    = 0.0
	icurrentres = 0

	if(myid == main_node):
		if(type(stack) == str or ( nz == 1 )):
			if(nx<nnxo):
				for procid in xrange(2):
					for i in xrange(3):
						for k in xrange(nx,nnxo/2+1):
							fsc[procid][i].append(0.0)
					for k in xrange(nnxo/2+1):
						fsc[procid][0][k] = float(k)/nnxo
			for procid in xrange(2):
				#  Compute adjusted within-fsc as 2*f/(1+f)
				fsc[procid].append(fsc[procid][1][:])
				for k in xrange(len(fsc[procid][1])):  fsc[procid][-1][k] = 2*fsc[procid][-1][k]/(1.0+fsc[procid][-1][k])
				write_text_file( fsc[procid], os.path.join(outputdir,"within-fsc%01d.txt"%procid) )
		lowpass, falloff, icurrentres = get_pixel_resolution_mrk01(vol, mask, nnxo, outputdir, mask_option)
		line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
		print(  line,"Current resolution  %6.2f (%d), low-pass filter cut-off %6.2f and fall-off %6.2f"%(icurrentres/float(nnxo),icurrentres,lowpass,falloff))
		write_text_row([[lowpass, falloff, icurrentres]],os.path.join(outputdir,"current_resolution.txt"))
	#  Returns: low-pass filter cutoff;  low-pass filter falloff;  current resolution
	icurrentres = bcast_number_to_all(icurrentres, source_node = main_node)
	lowpass    = bcast_number_to_all(lowpass, source_node = main_node)
	falloff    = bcast_number_to_all(falloff, source_node = main_node)
	return round(lowpass,4), round(falloff,4), icurrentres


# NOTE: 2015/06/11 Toshio Moriya
# This function seems to be not used
def compute_fscs_mrk01(stack, outputdir, chunkname, newgoodname, fscoutputdir, CTF, mask_option, sym, doit, keepchecking, nproc, myid, main_node):
	#  Compute reconstructions per group from good particles only to get FSC curves
	#  We will compute two FSC curves - from not averaged parameters and from averaged parameters
	#     So, we have to build two sets:
	#    not averaged  (A2+C3) versus (B0+D5)
	#          averaged  (A0+C1) versus (B3+D4)
	#    This requires pulling good subsets given by goodX*;  I am not sure why good, sxconsistency above produced newgood text files.
	#                                                                 Otherwise, I am not sure what newbad will contain.
	# Input that should vary:  
	#    "bdb:"+os.path.join(outputdir,"chunk%01d%01d"%(procid,i))
	#    os.path.join(outputdir,"newgood%01d.txt"%procid)
	#  Output should be in a separate directory "fscoutputdir"

	if(myid == main_node):
		if keepchecking:
			if(os.path.exists(fscoutputdir)):
				doit = 0
				print("Directory  ",fscoutputdir,"  exists!")
			else:
				doit = 1
				keepchecking = False
		else:
			doit = 1
		if doit:
			cmd = "{} {}".format("mkdir", fscoutputdir)
			cmdexecute(cmd)
	mpi_barrier(MPI_COMM_WORLD)
	
	#  not averaged
	doit, keepchecking = checkstep(os.path.join(fscoutputdir,"volfscn0.hdf"), keepchecking, myid, main_node)
	if doit:
		if(myid == main_node):
			#  A2+C3
			#     indices
			write_text_file( \
				map(int, read_text_file(os.path.join(outputdir,chunkname+"0.txt")))+map(int, read_text_file(os.path.join(outputdir,chunkname+"2.txt"))),   \
				os.path.join(fscoutputdir,"chunkfn0.txt"))
			#  params
			write_text_row( \
				read_text_row(os.path.join(outputdir,newgoodname+"02.txt"))+read_text_row(os.path.join(outputdir,newgoodname+"22.txt")), \
				os.path.join(fscoutputdir,"params-chunkfn0.txt"))

		mpi_barrier(MPI_COMM_WORLD)

		projdata = getindexdata(stack, os.path.join(fscoutputdir,"chunkfn0.txt"), os.path.join(fscoutputdir,"params-chunkfn0.txt"), myid, nproc)
		if CTF:  vol = recons3d_4nn_ctf_MPI(myid, projdata, symmetry=sym, npad = 2)
		else:    vol = recons3d_4nn_MPI    (myid, projdata, symmetry=sym, npad = 2)
		del projdata
		if(myid == main_node):
			vol.write_image(os.path.join(fscoutputdir,"volfscn0.hdf"))
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(line,"Executed successfully: 3D reconstruction of", os.path.join(fscoutputdir,"volfscn0.hdf"))
		del vol


	doit, keepchecking = checkstep(os.path.join(fscoutputdir,"volfscn1.hdf"), keepchecking, myid, main_node)
	if doit:
		if(myid == main_node):
			#  B0+D5
			#     indices
			write_text_file( \
				map(int, read_text_file(os.path.join(outputdir,chunkname+"1.txt")))+map(int, read_text_file(os.path.join(outputdir,chunkname+"3.txt"))),   \
				os.path.join(fscoutputdir,"chunkfn1.txt"))
			#  params
			write_text_row( \
				read_text_row(os.path.join(outputdir,newgoodname+"10.txt"))+read_text_row(os.path.join(outputdir,newgoodname+"32.txt")), \
				os.path.join(fscoutputdir,"params-chunkfn1.txt"))

		mpi_barrier(MPI_COMM_WORLD)

		projdata = getindexdata(stack, os.path.join(fscoutputdir,"chunkfn1.txt"), os.path.join(fscoutputdir,"params-chunkfn1.txt"), myid, nproc)
		if CTF:  vol = recons3d_4nn_ctf_MPI(myid, projdata, symmetry=sym, npad = 2)
		else:    vol = recons3d_4nn_MPI    (myid, projdata, symmetry=sym, npad = 2)
		del projdata
		if(myid == main_node):
			vol.write_image(os.path.join(fscoutputdir,"volfscn1.hdf"))
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(line,"Executed successfully: 3D reconstruction of", os.path.join(fscoutputdir,"volfscn1.hdf"))
		del vol

	#      averaged
	doit, keepchecking = checkstep(os.path.join(fscoutputdir,"volfsca0.hdf"), keepchecking, myid, main_node)
	if doit:
		if(myid == main_node):
			#  A0+C1
			#     indices
			write_text_file( \
				map(int, read_text_file(os.path.join(outputdir,chunkname+"0.txt")))+map(int, read_text_file(os.path.join(outputdir,chunkname+"2.txt"))),   \
				os.path.join(fscoutputdir,"chunkfa0.txt"))
			#  params
			write_text_row( \
				read_text_row(os.path.join(outputdir,newgoodname+"00.txt"))+read_text_row(os.path.join(outputdir,newgoodname+"20.txt")), \
				os.path.join(fscoutputdir,"params-chunkfa0.txt"))
		mpi_barrier(MPI_COMM_WORLD)

		projdata = getindexdata(stack, os.path.join(fscoutputdir,"chunkfa0.txt"), os.path.join(fscoutputdir,"params-chunkfa0.txt"), myid, nproc)
		if CTF:  vol = recons3d_4nn_ctf_MPI(myid, projdata, symmetry=sym, npad = 2)
		else:    vol = recons3d_4nn_MPI    (myid, projdata, symmetry=sym, npad = 2)
		del projdata
		if(myid == main_node):
			vol.write_image(os.path.join(fscoutputdir,"volfsca0.hdf"))
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(line,"Executed successfully: 3D reconstruction of", os.path.join(fscoutputdir,"volfsca0.hdf"))
		del vol


	doit, keepchecking = checkstep(os.path.join(fscoutputdir,"volfsca1.hdf"), keepchecking, myid, main_node)
	if doit:
		if(myid == main_node):
			#  B3+D4
			write_text_file( \
				map(int, read_text_file(os.path.join(outputdir,chunkname+"1.txt")))+map(int, read_text_file(os.path.join(outputdir,chunkname+"3.txt"))),   \
				os.path.join(fscoutputdir,"chunkfa1.txt"))
			#  params
			write_text_row( \
				read_text_row(os.path.join(outputdir,newgoodname+"11.txt"))+read_text_row(os.path.join(outputdir,newgoodname+"31.txt")), \
				os.path.join(fscoutputdir,"params-chunkfa1.txt"))
		mpi_barrier(MPI_COMM_WORLD)

		projdata = getindexdata(stack, os.path.join(fscoutputdir,"chunkfa1.txt"), os.path.join(fscoutputdir,"params-chunkfa1.txt"), myid, nproc)
		if CTF:  vol = recons3d_4nn_ctf_MPI(myid, projdata, symmetry=sym, npad = 2)
		else:    vol = recons3d_4nn_MPI    (myid, projdata, symmetry=sym, npad = 2)
		del projdata
		if(myid == main_node):
			vol.write_image(os.path.join(fscoutputdir,"volfsca1.hdf"))
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(line,"Executed successfully: 3D reconstruction of", os.path.join(fscoutputdir,"volfsca1.hdf"))
		del vol


 
	#  Get updated FSC curves
	if(myid == main_node):
		if(mask_option is None):  mask = model_circle(radi,nnxo,nnxo,nnxo)
		else:
			mask = get_im(mask_option)
		if keepchecking:
			if(os.path.exists(os.path.join(fscoutputdir,"fscn.txt"))):
				doit = 0
			else:
				doit = 1
				keepchecking = False
		else:  doit = 1
		if  doit:  fsc(get_im(os.path.join(fscoutputdir,"volfscn0.hdf"))*mask,\
				get_im(os.path.join(fscoutputdir,"volfscn1.hdf"))*mask,\
				1.0,os.path.join(fscoutputdir,"fscn.txt") )
		if keepchecking:
			if(os.path.exists(os.path.join(fscoutputdir,"fsca.txt"))):
				doit = 0
			else:
				doit = 1
				keepchecking = False
		else:  doit = 1
		if  doit:  fsc(get_im(os.path.join(fscoutputdir,"volfsca0.hdf"))*mask,\
				get_im(os.path.join(fscoutputdir,"volfsca1.hdf"))*mask,\
				1.0,os.path.join(fscoutputdir,"fsca.txt") )

		nfsc = read_text_file(os.path.join(fscoutputdir,"fscn.txt") ,-1)
		currentres = 0.5
		ns = len(nfsc[1])
		for i in xrange(1,ns-1):
			if ( (2*nfsc[1][i]/(1.0+nfsc[1][i]) ) < 0.5):
				currentres = nfsc[0][i-1]
				break
		print("  Current resolution ",i,currentres)
	else:
		currentres = 0.0
	currentres = bcast_number_to_all(currentres, source_node = main_node)
	if(currentres < 0.0):
		if(myid == main_node):
			print("  Something wrong with the resolution, cannot continue")
		mpi_finalize()
		exit()

	mpi_barrier(MPI_COMM_WORLD)
	return  currentres, doit, keepchecking


"""
in utilities.py
def getindexdata(stack, partids, partstack, myid, nproc):
	# The function will read from stack a subset of images specified in partids
	#   and assign to them parameters from partstack
	# So, the lengths of partids and partstack are the same.
	#  The read data is properly distributed among MPI threads.
"""

# NOTE: 2015/06/12 Toshio Moriya
# This function seems to be not used
def getalldata(stack, myid, nproc):
	if(myid == 0):  ndata = EMUtil.get_image_count(stack)
	else:           ndata = 0
	ndata = bcast_number_to_all(ndata)	
	if( ndata < nproc):
		if(myid<ndata):
			image_start = myid
			image_end   = myid+1
		else:
			image_start = 0
			image_end   = 1			
	else:
		image_start, image_end = MPI_start_end(ndata, nproc, myid)
	data = EMData.read_images(stack, range(image_start, image_end))
	return data



def get_shrink_data(onx, nx, stack, partids, partstack, myid, main_node, nproc, CTF = False, applyctf = True, preshift = False, radi = -1):
	# The function will read from stack a subset of images specified in partids
	#   and assign to them parameters from partstack with optional CTF application and shifting of the data.
	# So, the lengths of partids and partstack are the same.
	#  The read data is properly distributed among MPI threads.
	if( myid == main_node ):
		print("    ")
		print("  get_shrink_data  ")
		print("  onx, nx, stack, partids, partstack, CTF, applyctf, preshift, radi  ",onx, nx, stack, partids, partstack, CTF, applyctf, preshift, radi)
	if( myid == main_node ): lpartids = read_text_file(partids)
	else:  lpartids = 0
	lpartids = wrap_mpi_bcast(lpartids, main_node)
	ndata = len(lpartids)
	if( myid == main_node ):  partstack = read_text_row(partstack)
	else:  partstack = 0
	partstack = wrap_mpi_bcast(partstack, main_node)
	if( ndata < nproc):
		if(myid<ndata):
			image_start = myid
			image_end   = myid+1
		else:
			image_start = 0
			image_end   = 1
	else:
		image_start, image_end = MPI_start_end(ndata, nproc, myid)
	lpartids  = lpartids[image_start:image_end]
	partstack = partstack[image_start:image_end]
	#  Preprocess the data
	if radi < 0:	radi = onx//2 - 2
	mask2D  = model_circle(radi,onx,onx)
	nima = image_end - image_start
	oldshifts = [[0.0,0.0]]*nima
	data = [None]*nima
	shrinkage = float(nx)/float(onx)
	for im in xrange(nima):
		data[im] = get_im(stack, lpartids[im])
		phi,theta,psi,sx,sy = partstack[im][0], partstack[im][1], partstack[im][2], partstack[im][3], partstack[im][4]
		if preshift:
			data[im] = fshift(data[im], sx, sy)
			set_params_proj(data[im],[phi,theta,psi,0.0,0.0])
			oldshifts[im] = [sx,sy]
		else:
			set_params_proj(data[im],[phi,theta,psi,sx,sy])
		#  For local SHC set anchor
		#if(nsoft == 1 and an[0] > -1):
		#  We will always set it to simplify the code
		set_params_proj(data[im],[phi,theta,psi,0.0,0.0], "xform.anchor")
		if CTF and applyctf:
			ctf_params = data[im].get_attr("ctf")
			st = Util.infomask(data[im], mask2D, False)
			data[im] -= st[0]
			data[im] = filt_ctf(data[im], ctf_params)
			data[im].set_attr('ctf_applied', 1)
		if(shrinkage < 1.0):
			#  resample will properly adjusts shifts and pixel size in ctf
			data[im] = resample(data[im], shrinkage)
	assert( nx == data[0].get_xsize() )  #  Just to make sure.
	oldshifts = wrap_mpi_gatherv(oldshifts, main_node, MPI_COMM_WORLD)
	return data, oldshifts


# NOTE: 2015/06/10 Toshio Moriya
# This is the same function as metamove() in sxmeridien.py
# However, it uses dictionary object (Tracker) instead of class ali3d_options
#
def metamove_mrk01(projdata, oldshifts, Tracker, partids, partstack, outputdir, procid, myid, main_node, nproc):

	# Check the required keys exist in parameter dictionary
	assert(Tracker.has_key("refvol"))       
	assert(Tracker.has_key("nxinit"))
	assert(Tracker.has_key("delpreviousmax"))
	# assert(Tracker.has_key("lowpass"))
	# assert(Tracker.has_key("initialfl"))
	assert(Tracker.has_key("PWadjustment")) 
	assert(Tracker.has_key("local"))
	assert(Tracker.has_key("saturatecrit"))
	assert(Tracker.has_key("pixercutoff"))
	assert(Tracker.has_key("nsoft"))

	#  Takes preshrunk data and does the refinement as specified in Tracker
	#
	#  Will create outputdir
	#  Will write to outputdir output parameters: params-chunk0.txt and params-chunk1.txt
	if(myid == main_node):
		#  Create output directory
		log = Logger(BaseLogger_Files())
		log.prefix = os.path.join(outputdir)
		cmd = "mkdir "+log.prefix
		cmdexecute(cmd)
		log.prefix += "/"
		ref_vol = get_im(Tracker["refvol"])
		nnn = ref_vol.get_xsize()
		shrinkage = float(Tracker["nxinit"])/float(nnn)
		if(Tracker["nxinit"] != nnn ):
			from fundamentals import resample
			ref_vol = resample(ref_vol, shrinkage)
	else:
		log = None
		ref_vol = model_blank(Tracker["nxinit"], Tracker["nxinit"], Tracker["nxinit"])
	mpi_barrier(MPI_COMM_WORLD)
	bcast_EMData_to_all(ref_vol, myid, main_node)

	if(Tracker["delpreviousmax"]):
		for i in xrange(len(projdata)):
			try:  projdata[i].del_attr("previousmax")
			except:  pass
	if(myid == main_node):
		print_dict(Tracker,"METAMOVE parameters")
		#print("                    =>  actual lowpass      :  ",Tracker["lowpass"])
		#print("                    =>  actual init lowpass :  ",Tracker["initialfl"])
		if(len(Tracker["PWadjustment"])>0): \
		print("                    =>  PW adjustment       :  ",Tracker["PWadjustment"])
		print("                    =>  partids             :  ",partids)
		print("                    =>  partstack           :  ",partstack)

	#if(Tracker["lowpass"] > 0.48):  ERROR("Low pass filter in metamove > 0.48 on the scale of shrank data","sxmeridien",1,myid)

	#  Run alignment command
	if(Tracker["local"]):
		params = slocal_ali3d_base_MPI_mrk01(projdata, get_im(Tracker["refvol"]), \
						Tracker, mpi_comm = MPI_COMM_WORLD, log = log, \
		    			chunk = 0.25, \
		    			saturatecrit = Tracker["saturatecrit"], pixercutoff =  Tracker["pixercutoff"])
	else: params = sali3d_base_mrk01(projdata, ref_vol, \
						Tracker, mpi_comm = MPI_COMM_WORLD, log = log, \
						nsoft = Tracker["nsoft"], \
						saturatecrit = Tracker["saturatecrit"],  pixercutoff =  Tracker["pixercutoff"] )

	#  We could calculate here a 3D to get the within group resolution and return it as a result to eventually get crossresolution
	del log
	#  store params
	if(myid == main_node):
		line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
		print(line,"Executed successfully: ","sali3d_base_MPI, nsoft = %d"%Tracker["nsoft"],"  number of images:%7d"%len(params))
		for i in xrange(len(params)):
			params[i][3] = params[i][3]/shrinkage + oldshifts[i][0]
			params[i][4] = params[i][4]/shrinkage + oldshifts[i][1]
		write_text_row(params, os.path.join(outputdir,"params-chunk%01d.txt"%procid) )


def print_dict(dict,theme):
	line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
	print(line,theme)
	spaces = "                    "
	for q in dict:  print("                    => ",q+spaces[len(q):],":  ",dict[q])


# NOTE: 2015/06/11 Toshio Moriya
# DESIGNE
# - "options" object 
#   It keeps the original input option values specified by user.
#   This object must be constant. That is, you should not assign any parameter values 
#   to this after the initialization.
# 
# - "Tracker" (dictionary) object
#   Keeps the current state of option settings and dataset 
#   (i.e. particle stack, reference volume, reconstructed volume, and etc)
#   Each iteration is allowed to add new fields/keys
#   if necessary. This happes especially when type of 3D Refinement or metamove changes.
#   Conceptually, each iteration will be associated to a specific Tracker state.
#   Therefore, the list of Tracker state represents the history of process.
#   (history is doing this now)
#   This can be used to restart process from an arbitrary iteration.
#   The program will store the history in the form of file.
#   
# NOTE: 2015/06/11 Toshio Moriya
# MODIFICATION
# - merge ali3d_options to Tracker (dictionary)
# - make paramsdict to be Tracker (dictionary) 
#   paramsdict was earlier version of Tracker (Pawel)...
#
def main_mrk01():

	from utilities import write_text_row, drop_image, model_gauss_noise, get_im, set_params_proj, wrap_mpi_bcast, model_circle
	import user_functions
	from applications import MPI_start_end
	from optparse import OptionParser
	from global_def import SPARXVERSION
	from EMAN2 import EMData
	from multi_shc import multi_shc, do_volume
	from logger import Logger, BaseLogger_Files
	import sys
	import os
	import time
	import socket
	
	# ------------------------------------------------------------------------------------
	# PARSE COMMAND OPTIONS
	progname = os.path.basename(sys.argv[0])
	usage = progname + " stack  [output_directory]  initial_volume  --ir=inner_radius --ou=outer_radius --rs=ring_step --xr=x_range --yr=y_range  --ts=translational_search_step  --delta=angular_step --an=an  --center=center_type --fl --aa --ref_a=S --sym=c1"
	parser = OptionParser(usage,version=SPARXVERSION)
	parser.add_option("--ir",      		type= "int",   default= 1,			help="inner radius for rotational correlation > 0 (set to 1)")
	parser.add_option("--ou",      		type= "int",   default= -1,			help="outer radius for rotational correlation < int(nx/2)-1 (set to the radius of the particle)")
	##parser.add_option("--rs",      		type= "int",   default= 1,			help="step between rings in rotational correlation >0  (set to 1)" ) 
	#parser.add_option("--xr",      		type="string", default= "-1",		help="range for translation search in x direction, search is +/xr (default 0)")
	#parser.add_option("--yr",      		type="string", default= "-1",		help="range for translation search in y direction, search is +/yr (default = same as xr)")
	#parser.add_option("--ts",      		type="string", default= "1",		help="step size of the translation search in both directions, search is -xr, -xr+ts, 0, xr-ts, xr, can be fractional")
	#parser.add_option("--delta",   		type="string", default= "-1",		help="angular step of reference projections during initialization step (default automatically selected based on radius of the structure.)")
	parser.add_option("--an",      		type="string", default= "-1",		help="angular neighborhood for local searches (phi and theta) (Default exhaustive searches)")
	parser.add_option("--center",  		type="float",  default= -1,			help="-1: average shift method; 0: no centering; 1: center of gravity (default=-1)")
	#parser.add_option("--maxit",   		type="int",  	default= 400,		help="maximum number of iterations performed for the GA part (set to 400) ")
	parser.add_option("--outlier_percentile",type="float",    default= 95,	help="percentile above which outliers are removed every iteration")
	parser.add_option("--iteration_start",type="int",    default= 0,		help="starting iteration for rviper, 0 means go to the most recent one (default).")
	parser.add_option("--CTF",     		action="store_true", default=False,	help="Use CTF (Default no CTF correction)")
	#parser.add_option("--snr",     		type="float",  default= 1.0,		help="Signal-to-Noise Ratio of the data (default 1.0)")
	parser.add_option("--ref_a",   		type="string", default= "S",		help="method for generating the quasi-uniformly distributed projection directions (default S)")
	parser.add_option("--sym",     		type="string", default= "c1",		help="symmetry of the refined structure")
	#parser.add_option("--npad",    		type="int",    default= 2,			help="padding size for 3D reconstruction (default=2)")
	parser.add_option("--nsoft",    	type="int",    default= 1,			help="Use SHC in first phase of refinement iteration (default=1, to turn it off set to 0)")
	parser.add_option("--startangles",  action="store_true", default=False,	help="Use orientation parameters in the input file header to jumpstart the procedure")

	#options introduced for the do_volume function
	#parser.add_option("--fl",			type="float",	default=0.12,		help="cut-off frequency of hyperbolic tangent low-pass Fourier filter (default 0.12)")
	#parser.add_option("--aa",			type="float",	default=0.1,		help="fall-off of hyperbolic tangent low-pass Fourier filter (default 0.1)")
	parser.add_option("--inires",		type="float",	default=25.,		help="Resolution of the initial_volume volume (default 25A)")
	parser.add_option("--pwreference",	type="string",	default="",			help="text file with a reference power spectrum (default no power spectrum adjustment)")
	parser.add_option("--mask3D",		type="string",	default=None,		help="3D mask file (default a sphere  WHAT RADIUS??)")


	(options, args) = parser.parse_args(sys.argv[1:])

	#print( "  args  ",args)
	if( len(args) == 3):
		volinit = args[2]
		masterdir = args[1]
	elif(len(args) == 2):
		volinit = args[1]
		masterdir = ""
	else:
		print( "usage: " + usage)
		print( "Please run '" + progname + " -h' for detailed options")
		return 1

	orgstack = args[0]
	#print(  orgstack,masterdir,volinit )
	# ------------------------------------------------------------------------------------
	# Initialize MPI related variables
	mpi_init(0, [])

	nproc     = mpi_comm_size(MPI_COMM_WORLD)
	myid      = mpi_comm_rank(MPI_COMM_WORLD)
	main_node = 0

	# ------------------------------------------------------------------------------------
	#  INPUT PARAMETERS
	radi  = options.ou
	global_def.BATCH = True
	
	# Create and initialize Tracker Dictionary with input options
	Tracker					= {}
	Tracker["stack"]        = args[0]
	Tracker["ir"]           = options.ir
	Tracker["rs"]           = 1
	Tracker["maxit"]        = 1
	Tracker["radi"]         = options.ou #  radius provided by the user, do not change!
	Tracker["xr"]           = ""
	Tracker["yr"]           = ""
	Tracker["ts"]           = 1
	Tracker["an"]           = options.an
	Tracker["sym"]          = options.sym
	Tracker["delta"]        = "2.0"
	Tracker["npad"]         = 2
	Tracker["center"]       = options.center
	Tracker["zoom"]         = True
	Tracker["nsoft"]        = options.nsoft
	Tracker["local"]        = False
	Tracker["CTF"]          = options.CTF
	Tracker["ref_a"]        = options.ref_a
	Tracker["snr"]          = options.snr
	Tracker["mask3D"]       = options.mask3D
	Tracker["PWadjustment"] = ""
	Tracker["pwreference"]  = options.pwreference
	Tracker["applyctf"]     = True  #  Should the data be premultiplied by the CTF.  Set to False for local continues.
	
	#  The program will use three different meanings of x-size
	#  nnxo         - original nx of the data, will not be changed
	#  nxinit       - window size used by the program during given iteration, 
	#                 will be increased in steps of 32 with the resolution
	#  nxresolution - resolution window size in Fourier pixels within nxinit.
	#                 The fl within the reduced data is nxresolution/nxinit/2.0
	#                 The absolute fl is nxresolution/nnxo/2.0
	#
	#  nxstep       - step by wich window size increases
	#
	Tracker["nnxo"]         = -1
	Tracker["nxinit"]       = 64
	Tracker["nxresolution"] = -1
	Tracker["nxstep"]       = 32
	Tracker["icurrentres"]  = -1
	Tracker["fl"]           = 0.4
	Tracker["initialfl"]    = 0.4
	Tracker["aa"]           = 0.1
	Tracker["pixel_size"]   = 1.0
	Tracker["inires"]       = options.inires  # Now in A, convert to absolute before using
	Tracker["fuse_freq"]    = 50  # Now in A, convert to absolute before using
	Tracker["delpreviousmax"] = True
	Tracker["saturatecrit"]  = 1.0
	Tracker["pixercutoff"]   = 2.0
	Tracker["refvol"]        = volinit
	Tracker["masterdir"]     = masterdir
	Tracker["previousoutputdir"] = ""
	Tracker["movedup"]       = False
	Tracker["eliminated-outliers"] = False
	Tracker["mainteration"]  = 0

	# ------------------------------------------------------------------------------------
	#  PARAMETERS OF THE PROCEDURE 
	#  threshold error
	thresherr = 0
	cushion  = 8  #  the window size has to be at least 8 pixels larger than what would follow from resolution
	mempernode = 4.0e9
	if(Tracker["radi"]  < 1):  Tracker["radi"]  = nnxo//2-2
	elif((2*Tracker["radi"] +2)>nnxo):  ERROR("Particle radius set too large!","sxmeridien",1,myid)

	# Get the pixel size; if none, set to 1.0, and the original image size
	if(myid == main_node):
		a = get_im(orgstack)
		nnxo = a.get_xsize()
		if( nnxo%2 == 1 ):
			ERROR("Only even-dimensioned data allowed","sxmeridien",1)  #  This will have to be eliminated as we will move only in even dimensioned windowed.
			nnxo = -1
		elif( Tracker["nxinit"] > nnxo ):
			ERROR("Image size less than minimum permitted $d"%Tracker["nxinit"],"sxmeridien",1)
			nnxo = -1
		else:
			if Tracker["CTF"]:
				i = a.get_attr('ctf')
				pixel_size = i.apix
				fq = pixel_size/Tracker["fuse_freq"]
			else:
				pixel_size = 1.0
				#  No pixel size, fusing computed as 5 Fourier pixels
				fq = 5.0/nnxo
			del a
	else:
		nnxo = 0
		pixel_size = 1.0
	nnxo = bcast_number_to_all(nnxo, source_node = main_node)
	if( nnxo < 0 ):
		mpi_finalize()
		exit()
	pixel_size = bcast_number_to_all(pixel_size, source_node = main_node)
	fq         = bcast_number_to_all(fq, source_node = main_node)
	Tracker["nnxo"]         = nnxo
	Tracker["pixel_size"]   = pixel_size
	Tracker["fuse_freq"]    = fq

	# ------------------------------------------------------------------------------------
	#  MASTER DIRECTORY
	if(myid == main_node):
		print( "   masterdir   ",masterdir)
		if( masterdir == ""):
			timestring = strftime("_%d_%b_%Y_%H_%M_%S", localtime())
			masterdir = "master"+timestring
			li = len(masterdir)
			cmd = "{} {}".format("mkdir", masterdir)
			cmdexecute(cmd)
			keepchecking = 0
		else:
			li = 0
			keepchecking = 1
	else:
		li = 0
		keepchecking = 1

	li = mpi_bcast(li,1,MPI_INT,main_node,MPI_COMM_WORLD)[0]

	if( li > 0 ):
		masterdir = mpi_bcast(masterdir,li,MPI_CHAR,main_node,MPI_COMM_WORLD)
		masterdir = string.join(masterdir,"")

	#  create a vstack from input stack to the local stack in masterdir
	#  Stack name set to default
	stack = "bdb:"+masterdir+"/rdata"
	# Initialization of stacks
	if(myid == main_node):
		if keepchecking:
			if(os.path.exists(os.path.join(masterdir,"EMAN2DB/rdata.bdb"))):  doit = False
			else:  doit = True
		else:  doit = True
		if  doit:
			if(orgstack[:4] == "bdb:"):	cmd = "{} {} {}".format("e2bdb.py", orgstack,"--makevstack="+stack)
			else:  cmd = "{} {} {}".format("sxcpy.py", orgstack, stack)
			cmdexecute(cmd)
			cmd = "{} {}".format("sxheader.py  --consecutive  --params=originalid", stack)
			cmdexecute(cmd)
			keepchecking = False
		total_stack = EMUtil.get_image_count(stack)
	else:
		total_stack = 0

	total_stack = bcast_number_to_all(total_stack, source_node = main_node)

	# ------------------------------------------------------------------------------------
	#  INITIALIZATION
	initdir = os.path.join(masterdir,"main000")


	# Create first fake directory main000 with parameters filled with zeroes or copied from headers.  Copy initial volume in.
	doit, keepchecking = checkstep(initdir, keepchecking, myid, main_node)
	if  doit:
		partids = os.path.join(masterdir, "ids.txt")

		if(options.startangles):

			if( myid == main_node ):
				cmd = "mkdir "+initdir
				cmdexecute(cmd)
				line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
				print(line,"INITIALIZATION")
				cmd = "{} {}".format("sxheader.py --params=xform.projection  --export="+os.path.join(initdir,"params-chunk0.txt"), stack)
				cmdexecute(cmd)
				print(line,"Executed successfully: ","Imported initial parameters from the input stack")
		else:
			if( myid == main_node ):
				cmd = "mkdir "+initdir
				cmdexecute(cmd)
				line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
				print(line,"INITIALIZATION 3D")
				write_text_file(range(total_stack), partids)
			mpi_barrier(MPI_COMM_WORLD)


			if(myid == main_node):
				print(line,"Executed successfully: ","initialization ali3d_base_MPI")


		#  store params
		partids = [None]*2
		for procid in xrange(2):  partids[procid] = os.path.join(initdir,"chunk%01d.txt"%procid)
		partstack = [None]*2
		for procid in xrange(2):  partstack[procid] = os.path.join(initdir,"params-chunk%01d.txt"%procid)
		from random import shuffle
		if(myid == main_node):
			#  split randomly
			ll = range(total_stack)
			shuffle(ll)
			l1 = ll[:total_stack//2]
			l2 = ll[total_stack//2:]
			del ll
			l1.sort()
			l2.sort()
			write_text_file(l1,partids[0])
			write_text_file(l2,partids[1])
			write_text_row([[0,0,0,0,0] for i in xrange(len(l1))], partstack[0])
			write_text_row([[0,0,0,0,0] for i in xrange(len(l2))], partstack[1])
			del l1, l2
			
			# Create independent reference models for each particle group
			# make sure the initial volume is not set to zero outside of a mask, as if it is it will crash the program
			for procid in xrange(2):
				# make a copy of original reference model for this particle group (procid)
				file_path_viv = os.path.join(initdir,"vol%01d.hdf"%procid)
				cmd = "{} {} {}".format("cp -p", volinit, file_path_viv)
				cmdexecute(cmd)
			    # add small noise to the reference model
				viv = get_im(file_path_viv)
				if(options.mask3D == None):  mask33d = model_circle(radi,nnxo,nnxo,nnxo)
				else:                        mask33d = get_im(options.mask3D)
				st = Util.infomask(viv, mask33d, False)
				if( st[0] == 0.0 ):
					viv += (model_blank(nnxo,nnxo,nnxo,1.0) - mask33d)*model_gauss_noise(st[1]/1000.0,nnxo,nnxo,nnxo)
					viv.write_image(file_path_viv)
				del mask33d, viv
			
		mpi_barrier(MPI_COMM_WORLD)


	#  This is initial setting for the first iteration.
	#   It will be exhaustive search with zoom option to establish good shifts.
	Tracker["inires"] = Tracker["pixel_size"]/Tracker["inires"]  # This is in full size image units.
	i = int(Tracker["nnxo"]*Tracker["inires"]+0.5)*2 + cushion
	if(i > Tracker["nnxo"] ):  ERROR("Resolution of initial volume at the range of Nyquist frequency for given window and pixel sizes","sxmeridien",1, myid)
	Tracker[""] = 
	
	delta = int(options.delta)
	if(delta <= 0.0):
		delta = "%f"%round(degrees(atan(1.0/float(radi))), 2)
	inifil = float(nxinit)/2.0/nnxo
	inifil = 0.4
	
	# Set reasonable values for the following parameters
	lowpass     = 0.25
	falloff     = 0.2
	icurrentres = 32

	# set for the first iteration
	nxresolution = icurrentres*2 +2
	assert( nxresolution +cushion <= nnxo )
	nxinit = 60
	nxresolution = nxinit - cushion -1
	while( nxresolution + cushion > nxinit ): nxinit += 32
	nxinit = min(nxinit,nnxo)
	nsoft = options.nsoft
	lowpass = 0.25
	test_outliers = True
	mainiteration = 0
	keepgoing = 1
	Tracker["xr"] = "9  6  3"
	Tracker["ts"] = "3  2  1"

	# Update Tracker
	subdict( Tracker, {	"stack":stack, "delta":"2.0", "ts":ts, "xr":"%f"%xr, "an":Tracker["an"], \
						"center":options.center, "maxit":1, "local":False, \
						"lowpass":inifil, "initialfl":inifil, "falloff":0.2, "radius":radi, \
						"icurrentres":nxinit//2, "nxinit":nnxo, "nxresolution":nnxo, \
						"nsoft":0, "delpreviousmax":True, "saturatecrit":1.0, "pixercutoff":2.0, \
						"refvol":volinit, "mask3D":options.mask3D } )
	subdict( Tracker, {	"stack":stack, "delta":"2.0", "ts":ts, "xr":"%f"%xr, "an":Tracker["an"], \
						"center":options.center, "maxit":1, "local":False, \
						"lowpass":inifil, "initialfl":inifil, "falloff":0.2, "radius":radi, \
						"icurrentres":nxinit//2, "nxinit":nnxo, "nxresolution":nnxo, \
						"nsoft":0, "delpreviousmax":True, "saturatecrit":1.0, "pixercutoff":2.0, \
						"refvol":volinit, "mask3D":options.mask3D } )
	subdict( Tracker, { "resolution":icurrentres/float(nnxo), "lowpass":lowpass, "initialfl":lowpass,  \
						"movedup":False, "eliminated-outliers":False, "applyctf":True, "PWadjustment":"", "local":False, "nsoft":nsoft, \
						"nnxo":nnxo, "icurrentres":icurrentres, "nxinit":nxinit, "nxresolution":nxresolution, "extension":0.0, \
						"directory":"none"} )
	history = [Tracker.copy()]
	previousoutputdir = initdir
	#  remove projdata, if it existed, initialize to nonsense
	projdata = [[model_blank(1,1)], [model_blank(1,1)]]
	oldshifts = [[],[]]
	
	# ------------------------------------------------------------------------------------
	#  MAIN ITERATION

	while(keepgoing):
		mainiteration += 1

		#  prepare output directory
		history[-1]["directory"] = "main%03d"%mainiteration
		mainoutputdir = os.path.join(masterdir,history[-1]["directory"])

		if(myid == main_node):
			line = strftime("%Y-%m-%d_%H:%M:%S", localtime()) + " =>"
			print(line,"MAIN ITERATION  #%2d     nxinit, nxresolution, icurrentres, resolution, lowpass, falloff "%\
				mainiteration, nxinit,  nxresolution, icurrentres, icurrentres/float(nnxo), lowpass, falloff)
			print(line,"  mainoutputdir  previousoutputdir  ",mainoutputdir,previousoutputdir)
			Tracker_print_mrk01(history[-1],"TRACKER")

			if keepchecking:
				if(os.path.exists(mainoutputdir)):
					doit = 0
					print("Directory  ",mainoutputdir,"  exists!")
				else:
					doit = 1
					keepchecking = False
			else:
				doit = 1

			if doit:
				cmd = "{} {}".format("mkdir", mainoutputdir)
				cmdexecute(cmd)

		# prepare names of input file names, they are in main directory,
		#   log subdirectories contain outputs from specific refinements
		partids = [None]*2
		for procid in xrange(2):  partids[procid] = os.path.join(previousoutputdir,"chunk%01d.txt"%procid)
		partstack = [None]*2
		for procid in xrange(2):  partstack[procid] = os.path.join(previousoutputdir,"params-chunk%01d.txt"%procid)

		mpi_barrier(MPI_COMM_WORLD)
		doit = bcast_number_to_all(doit, source_node = main_node)


		#mpi_finalize()
		#exit()

		#print("RACING  A ",myid)
		outvol = [os.path.join(previousoutputdir,"vol%01d.hdf"%procid) for procid in xrange(2)]

		if(myid == main_node):
			if  doit:
				vol = [ get_im(outvol[procid]) for procid in xrange(2) ]
				fuselowf(vol, fq)
				for procid in xrange(2):  vol[procid].write_image(os.path.join(mainoutputdir,"fusevol%01d.hdf"%procid) )
				del vol

		mpi_barrier(MPI_COMM_WORLD)

		#  Refine two groups at a current resolution
		lastring = int(radi*float(Tracker["nxinit"])/float(nnxo)+0.5)
		if(lastring < 2):
			ERROR( "ERROR!!   lastring too small  %f    %f   %d"%(radi, lastring), "sxmeridien",1, myid)

		delta = round(degrees(atan(1.0/lastring)), 2)
		"""
		# subdict( paramsdict, { "delta":"%f"%delta , "an":Tracker["an"], "local":Tracker["local"], \
		# 				"lowpass":Tracker["lowpass"], "initialfl":Tracker["initialfl"], "resolution":Tracker["resolution"], \
		# 				"icurrentres":Tracker["icurrentres"], \
		# 				"nnxo":Tracker["nnxo"], "nxinit":Tracker["nxinit"], "nxresolution":Tracker["nxresolution"], \
		# 				"pixercutoff":get_pixercutoff(radi*float(Tracker["nxinit"])/float(nnxo), delta, 0.5), \
		# 				"radius":lastring,"delpreviousmax":True } )
		# Update Tracker
		subdict( Tracker, { "delta":"%f"%delta , "an":Tracker["an"], \
							"pixercutoff":get_pixercutoff(radi*float(Tracker["nxinit"])/float(nnxo), delta, 0.5), \
							"radius":lastring, "delpreviousmax":True } )
		"""
		# subdict( paramsdict, { "delta":"%f  %f  %f"%(delta, delta, delta) , "an":Tracker["an"], "local":Tracker["local"], \
		# 				"lowpass":Tracker["lowpass"], "initialfl":Tracker["initialfl"], "resolution":Tracker["resolution"], \
		#				"icurrentres":Tracker["icurrentres"], \
		# 				"nnxo":Tracker["nnxo"], "nxinit":Tracker["nxinit"], "nxresolution":Tracker["nxresolution"], \
		# 				"pixercutoff":get_pixercutoff(radi*float(Tracker["nxinit"])/float(nnxo), delta, 0.5), \
		# 				"radius":lastring,"delpreviousmax":True } )

		# Update Tracker
		subdict( Tracker, { "delta":"%f  %f  %f"%(delta, delta, delta), "an":Tracker["an"], \
							"pixercutoff":get_pixercutoff(radi*float(Tracker["nxinit"])/float(nnxo), delta, 0.5), \
							"radius":lastring, "delpreviousmax":True } )

		#  REFINEMENT
		#  Part "a"  SHC         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		nsoft = Tracker["nsoft"]
		for procid in xrange(2):
			coutdir = os.path.join(mainoutputdir,"loga%01d"%procid)
			doit, keepchecking = checkstep(coutdir, keepchecking, myid, main_node)
			#  here ts has different meaning for standard and continuous
			subdict( Tracker, { "nsoft":nsoft, "refvol":os.path.join(mainoutputdir,"fusevol%01d.hdf"%procid) } )
			#if(len(history)>1):  old_nx = history[-2]["nx"]
			#else:    old_nx = Tracker["nx"]
			#Tracker["xr"] = "3.0"#"%s"%max(3,int(1.5*Tracker["nx"]/float(old_nx) +0.5))
			if( nsoft > 0 ):
				if( float(Tracker["an"]) == -1.0 ):
					Tracker["saturatecrit"] = 0.75
				else:
					Tracker["saturatecrit"] = 0.90  # Shake and bake for local
				Tracker["maxit"] = 1500
			else:
				if(Tracker["local"]):
					Tracker["saturatecrit"] = 0.95
					#Tracker["pixercutoff"]  = 0.5
					Tracker["xr"] = "2.0"
					Tracker["maxit"] = 5 #  ?? Lucky guess
				else:
					Tracker["saturatecrit"] = 0.95
					Tracker["pixercutoff"]  = 0.5
					Tracker["maxit"] = 50 #  ?? Lucky guess

			if  doit:
				mpi_barrier(MPI_COMM_WORLD)
				if( Tracker["nxinit"] != projdata[procid][0].get_xsize() ):  \
					projdata[procid], oldshifts[procid] = get_shrink_data(nnxo, Tracker["nxinit"], \
						stack, partids[procid], partstack[procid], myid, main_node, nproc, \
						Tracker["CTF"], Tracker["applyctf"], preshift = False, radi = radi)
				metamove_mrk01(projdata[procid], oldshifts[procid], Tracker, partids[procid], partstack[procid], coutdir, procid, myid, main_node, nproc)

		partstack = [None]*2
		for procid in xrange(2):  partstack[procid] = os.path.join(mainoutputdir, "loga%01d"%procid, "params-chunk%01d.txt"%procid)

		#  check it for the first, if it does not exist, run the program
		outvol = os.path.join(mainoutputdir,"loga0","vol0.hdf")
		doit, keepchecking = checkstep(outvol, keepchecking, myid, main_node)

		if  doit:
			xlowpass, xfalloff, xcurrentres = compute_resolution_mrk01(stack, mainoutputdir, partids, partstack, \
													radi, nnxo, Tracker["CTF"], Tracker["mask3D"], Tracker["sym"], myid, main_node, nproc)
			del xlowpass, xfalloff, xcurrentres
			if( myid == main_node):
				# Move output to proper directories
				for procid in xrange(2):
					cmd = "{} {} {}".format("mv", os.path.join(mainoutputdir,"vol%01d.hdf"%procid), os.path.join(mainoutputdir,"loga%01d"%procid) )
					cmdexecute(cmd)
					cmd = "{} {} {}".format("mv", os.path.join(mainoutputdir,"within-fsc%01d.txt"%procid), os.path.join(mainoutputdir,"loga%01d"%procid) )
					cmdexecute(cmd)
				cmd = "{} {} {}".format("mv", os.path.join(mainoutputdir,"fsc.txt") , os.path.join(mainoutputdir,"afsc.txt"))
				cmdexecute(cmd)
				cmd = "{} {} {}".format("mv", os.path.join(mainoutputdir,"current_resolution.txt") , os.path.join(mainoutputdir,"acurrent_resolution.txt"))
				cmdexecute(cmd)
				
		#  fuse shc volumes to serve as starting point for the next, deterministic part.
		if(myid == main_node):
			if keepchecking:
				procid = 1
				if(os.path.join(mainoutputdir,"loga%01d"%procid,"fusevol%01d.hdf"%procid) ):
					doit = 0
				else:
					doit = 1
					keepchecking = False
			else:
				doit = 1
			if doit and nsoft>0:
				vol = []
				for procid in xrange(2):  vol.append(get_im(os.path.join(mainoutputdir,"loga%01d"%procid,"vol%01d.hdf"%procid) ))
				fuselowf(vol, fq)
				for procid in xrange(2):  vol[procid].write_image( os.path.join(mainoutputdir,"loga%01d"%procid,"fusevol%01d.hdf"%procid) )
				del vol
		else:  doit = 0
		mpi_barrier(MPI_COMM_WORLD)
		doit = bcast_number_to_all(doit, source_node = main_node)

		#  Part "b"  deterministic   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		partstack = [None]*2
		for procid in xrange(2):  partstack[procid] = os.path.join(mainoutputdir,"loga%01d"%procid,"params-chunk%01d.txt"%procid)

		for procid in xrange(2):
			coutdir = os.path.join(mainoutputdir,"logb%01d"%procid)
			doit, keepchecking = checkstep(coutdir, keepchecking, myid, main_node)
			if( nsoft > 0 and doit):  #  Only do finishing up when the previous step was SHC
				#  Run hard to finish up matching
				subdict(Tracker, \
				{ "maxit":10, "nsoft":0, "saturatecrit":0.95, "pixercutoff":0.5,"delpreviousmax":True, \
				"refvol":os.path.join(mainoutputdir,"loga%01d"%procid,"fusevol%01d.hdf"%procid)} )

				if  doit:
					if( Tracker["nxinit"] != projdata[procid][0].get_xsize() ):
						projdata[procid], oldshifts[procid] = get_shrink_data(nnxo, Tracker["nxinit"], \
											stack, partids[procid], partstack[procid], myid, main_node, nproc, \
											Tracker["CTF"], Tracker["applyctf"], preshift = False, radi = radi)
					metamove_mrk01(projdata[procid], oldshifts[procid], Tracker, partids[procid], partstack[procid], \
									coutdir, procid, myid, main_node, nproc)
			else:
				if( myid == main_node and doit):
					#  Simply copy from loga to logb the necessary stuff
					cmd = "{} {}".format("mkdir",coutdir)
					cmdexecute(cmd)
					cmd = "{} {} {}".format("cp -p", os.path.join(mainoutputdir,"loga%01d"%procid,"params-chunk%01d.txt"%procid) , os.path.join(coutdir,"params-chunk%01d.txt"%procid))
					cmdexecute(cmd)

		partstack = [None]*2
		for procid in xrange(2):  partstack[procid] = os.path.join(mainoutputdir,"logb%01d"%procid,"params-chunk%01d.txt"%procid)

		#  Compute current resolution, store result in the main directory
		doit, keepchecking = checkstep(os.path.join(mainoutputdir,"current_resolution.txt"), keepchecking, myid, main_node)
		if doit:
			if( nsoft > 0 ):
				#  There was first soft phase, so the volumes have to be computed
				#  low-pass filter, current resolution
				lowpass, falloff, icurrentres = compute_resolution_mrk01(stack, mainoutputdir, partids, partstack, \
														radi, nnxo, Tracker["CTF"], Tracker["mask3D"], Tracker["sym"], myid, main_node, nproc)
			else:
				# Previous phase was hard, so the resolution exists
				# MRK_NOTE: 2015/06/15: This need to be incorporate...
				if(myid == main_node):
					cmd = "{} {} {}".format("cp", os.path.join(mainoutputdir,"acurrent_resolution.txt") , os.path.join(mainoutputdir,"current_resolution.txt"))
					cmdexecute(cmd)
					cmd = "{} {} {}".format("cp", os.path.join(mainoutputdir,"afsc.txt") , os.path.join(mainoutputdir,"fsc.txt"))
					cmdexecute(cmd)
					for procid in xrange(2):
						cmd = "{} {} {}".format("cp -p", os.path.join(mainoutputdir,"loga%01d"%procid,"vol%01d.hdf"%procid) , os.path.join(mainoutputdir,"vol%01d.hdf"%procid))
						cmdexecute(cmd)
					[newlowpass, newfalloff, icurrentres] = read_text_row( os.path.join(mainoutputdir,"current_resolution.txt") )[0]
				else:
					newlowpass = 0.0
					newfalloff = 0.0
					icurrentres = 0
				newlowpass = bcast_number_to_all(newlowpass, source_node = main_node)
				newlowpass = round(newlowpass,4)
				newfalloff = bcast_number_to_all(newfalloff, source_node = main_node)
				newfalloff = round(newfalloff,4)
				icurrentres = bcast_number_to_all(icurrentres, source_node = main_node)
		else:
			if(myid == main_node):
				[newlowpass, newfalloff, icurrentres] = read_text_row( os.path.join(mainoutputdir,"current_resolution.txt") )[0]
			else:
				newlowpass = 0.0
				newfalloff = 0.0
				icurrentres = 0
			newlowpass = bcast_number_to_all(newlowpass, source_node = main_node)
			newlowpass = round(newlowpass,4)
			newfalloff = bcast_number_to_all(newfalloff, source_node = main_node)
			newfalloff = round(newfalloff,4)
			icurrentres = bcast_number_to_all(icurrentres, source_node = main_node)







		#  Here I have code to generate presentable results.  IDs and params have to be merged and stored and the overall volume computed.
		doit, keepchecking = checkstep(os.path.join(mainoutputdir,"volf.hdf"), keepchecking, myid, main_node)
		if  doit:
			if( myid == main_node ):
				pinids = read_text_file(partids[0]) + read_text_file(partids[1])
				params = read_text_row(partstack[0]) + read_text_row(partstack[1])

				assert(len(pinids) == len(params))

				for i in xrange(len(pinids)):
					pinids[i] = [ pinids[i], params[i] ]
				del params
				pinids.sort()

				write_text_file([pinids[i][0] for i in xrange(len(pinids))], os.path.join(mainoutputdir,"indexes.txt"))
				write_text_row( [pinids[i][1] for i in xrange(len(pinids))], os.path.join(mainoutputdir,"params.txt"))
			mpi_barrier(MPI_COMM_WORLD)
			nfsc = read_fsc(os.path.join(mainoutputdir,"fsc.txt"),nnxo, myid, main_node)
			Tracker["fl"], Tracker["aa"] = fit_tanh1([[float(i)/nnxo for i in xrange(len(nfsc))],nfsc], 0.01)
			del nfsc
			Tracker["ou"] = radi

			#  Here something will have to be done.  The idea is to have a presentable structure at full size.
			#  However, the data is in smaller window.  O possibility would be to compute structure in smaller window and then pad it
			#  in Fourier space with zero to the full size.
			#
			projdata = getindexdata(stack, os.path.join(mainoutputdir,"indexes.txt"), os.path.join(mainoutputdir,"params.txt"), myid, nproc)
			volf = do_volume_mrk01(projdata, Tracker, mainiteration, mpi_comm = MPI_COMM_WORLD)
			projdata = [[model_blank(1,1)],[model_blank(1,1)]]
			if(myid == main_node):
				volf.write_image(os.path.join(mainoutputdir,"volf.hdf"))
				for procid in xrange(2):
					cmd = "{} {} {}".format("cp -p", partids[procid] , os.path.join(mainoutputdir,"chunk%01d.txt"%procid))
					cmdexecute(cmd)
					cmd = "{} {} {}".format("cp -p", partstack[procid], os.path.join(mainoutputdir,"params-chunk%01d.txt"%procid))
					cmdexecute(cmd)


		mpi_barrier(MPI_COMM_WORLD)

		test_outliers = True
		eliminated_outliers = False
		newlowpass = lowpass
		newfalloff = falloff
		
		#  HERE the lowpass has the true meaning
		lowpass = newlowpass
		falloff = newfalloff

		"""
		if(myid == main_node and not eliminated_outliers and doit):  # I had to add here doit, otherwise during the restart it incorrectly copies the files.
			for procid in xrange(2):
				#  This is standard path, copy parameters to be used to the main
				cmd = "{} {} {}".format("cp -p", partids[procid] , os.path.join(mainoutputdir,"chunk%01d.txt"%procid))
				cmdexecute(cmd)
				cmd = "{} {} {}".format("cp -p", partstack[procid], os.path.join(mainoutputdir,"params-chunk%01d.txt"%procid))
				cmdexecute(cmd)
		"""

		keepgoing = 0
		if(Tracker["an"] == "-1" ):
			stepforward = 0.05
			increment   = 0.02
		else:
			stepforward = 0.02
			increment   = 0.01

		if(myid == main_node):
			print(" New resolution %d   Previous resolution %d"%(icurrentres , Tracker["icurrentres"]))
			print(" lowpass ",Tracker["lowpass"],nxinit,nxresolution)

		if(mainiteration >= 10):
			#  Finish up by running continuous at full size
			#  for continuous data cannot be ctf applied.
			projdata = [[model_blank(1,1)],[model_blank(1,1)]]
			Tracker["applyctf"] = False
			Tracker["nsoft"] = 0
			Tracker["local"] = True
			Tracker["nxinit"] = nnxo
			Tracker["nxresolution"] = nnxo - cushion -1

			nxresolution = Tracker["nxresolution"]
			nxinit = Tracker["nxinit"]
			Tracker["lowpass"] = 0.19167+ (mainiteration-10)*0.00417
			Tracker["initialfl"] = Tracker["lowpass"]
			lowpass = Tracker["lowpass"]

		"""
		#if( ( icurrentres > Tracker["icurrentres"] ) or (eliminated_outliers and not Tracker["eliminated-outliers"]) or mainiteration == 1):
		if( Tracker["lowpass"] <= 0.4):
			Tracker["lowpass"] += 0.05
			Tracker["initialfl"] = Tracker["lowpass"]
		else:
			projdata = [[model_blank(1,1)],[model_blank(1,1)]]
			nxinit = Tracker["nxinit"]
			if(myid == main_node): print(" Changing window size ",nxinit,Tracker["nxresolution"],nnxo)
			nxinit *= 2
			if(nxinit > nnxo):  exit()
			Tracker["nxresolution"] = nxinit - cushion -1
			nxresolution = Tracker["nxresolution"]
			Tracker["nxinit"] = nxinit
			Tracker["lowpass"] = 0.25
			Tracker["initialfl"] = Tracker["lowpass"]
		"""
		keepgoing = 1
		"""
			if(myid == main_node):
				if( icurrentres > Tracker["resolution"]):  print("  Resolution improved, full steam ahead!")
				else:  print("  While the resolution did not improve, we eliminated outliers so we follow the _resolution_improved_ path.")
			if(Tracker["icurrentres"] + nxstep//2 >= nnxo ):
				if(myid == main_node): print(" Resolution approached Nyquist limit, program will terminate")
			else:
				# We need separate rules for each case
				if( icurrentres > Tracker["resolution"] ):  Tracker["movedup"] = True
				else:   Tracker["movedup"] = False
				#  increase resolution
				nxresolution = icurrentres*2 +2
				nxinit = Tracker["nxinit"]
				while( nxresolution + cushion > nxinit ): nxinit += 32
				#  Window size changed, reset projdata
				if(nxinit> Tracker["nxinit"]):  projdata = [[model_blank(1,1)],[model_blank(1,1)]]
				nxinit = min(nxinit,nnxo)
				#  Exhaustive searches
				if(Tracker["an"] == "-1" and not Tracker["local"]):
					Tracker["initialfl"] = read_fsc(os.path.join(mainoutputdir,"fsc.txt"),icurrentres, myid, main_node)
					Tracker["lowpass"]   = Tracker["initialfl"]
					Tracker["applyctf"]  = True
					Tracker["nsoft"]     = 0
				#  Local searches
				elif(Tracker["an"] != "-1" and not Tracker["local"]):
					#Tracker["extension"] = min(stepforward, 0.45 - currentres)  # lowpass cannot exceed 0.45
					Tracker["initialfl"]  = read_fsc(os.path.join(mainoutputdir,"fsc.txt"),icurrentres, myid, main_node)
					Tracker["lowpass"]    = Tracker["initialfl"]
					Tracker["applyctf"]   = True
					Tracker["nsoft"]      = 0
				#  Local/gridding  searches, move only as much as the resolution increase allows
				elif(Tracker["local"]):
					#Tracker["extension"]  =    0.0  # lowpass cannot exceed 0.45
					Tracker["initialfl"]   = read_fsc(os.path.join(mainoutputdir,"fsc.txt"),icurrentres, myid, main_node)
					Tracker["lowpass"]     = Tracker["initialfl"]
					Tracker["applyctf"]    = False
					Tracker["nsoft"]       = 0
				else:
					print(" Unknown combination of settings in improved resolution path",Tracker["an"],Tracker["local"])
					exit()  #  This will crash the program, but the situation is unlikely to occure
				Tracker["nxresolution"]        = nxresolution
				Tracker["nxinit"]              = nxinit
				Tracker["icurrentres"]         = icurrentres
				Tracker["eliminated-outliers"] = eliminated_outliers
				bestoutputdir = mainoutputdir
				keepgoing = 1

		elif( icurrentres < Tracker["icurrentres"] ):
			if(myid == main_node):  print("  Cannot improve resolution, the best result is in the directory %s"%bestoutputdir)
			exit()
			#  The resolution decreased.  For exhaustive or local, backoff and switch to the next refinement.  For gridding, terminate
			if(not Tracker["movedup"] and Tracker["extension"] < increment and mainiteration > 1):
				if( Tracker["an"] == "-1" and not Tracker["local"]):
					Tracker["an"] = options.an
					Tracker["extension"] = stepforward + increment # so below it will be set to stepforward
					mainoutputdir = bestoutputdir
					keepgoing = 1
					Tracker["nsoft"] = 0
					if(myid == main_node):  print("  Switching to local searches with an %s"%Tracker["an"])
				elif(Tracker["an"] != "-1" and not Tracker["local"]):
					Tracker["extension"] = stepforward + increment # so below it will be set to stepforward
					mainoutputdir = bestoutputdir
					Tracker["nsoft"] = 0
					keepgoing = 1
					if(myid == main_node):  print("  Switching to local/gridding searches")
				else:
					keepgoing = 0
					if(myid == main_node):  print("  Cannot improve resolution, the best result is in the directory %s"%bestoutputdir)
			else:
				if(not Tracker["movedup"] and Tracker["extension"] > 0.01 and mainiteration > 1):
					if(myid == main_node):  print("  Resolution decreased.  Will decrease target resolution and will fall back on the best so far:  main%03d"%Tracker["bestsolution"])
					bestoutputdir = os.path.join(masterdir,"main%03d"%Tracker["bestsolution"])
				elif( Tracker["movedup"] and Tracker["extension"] > 0.01 and mainiteration > 1):
					if(myid == main_node):  print("  Resolution decreased.  Will decrease target resolution and will try starting from previous stage:  main%03d"%(mainiteration - 1))
					bestoutputdir = os.path.join(masterdir,"main%03d"%(mainiteration-1))
				elif( mainiteration == 1):
					if(myid == main_node):  print("  Resolution decreased in the first iteration.  It is expected, not to worry")
					bestoutputdir = mainoutputdir
					Tracker["extension"] = increment  # so it will become zero
				else:  # missing something here?
					ERROR(" Should not be here, ERROR 175!", "sxmeridien", 1, myid)
				if( bestoutputdir != mainoutputdir ):
					#  This is the key, we just reset the main to previous, so it will be eventually used as a starting in the next iteration
					mainoutputdir = bestoutputdir
					'''
					#  Set data from the main previous best to the current.
					for procid in xrange(2):
						partids[procid]   = os.path.join(bestoutputdir,"chunk%01d.txt"%procid)
						partstack[procid] = os.path.join(bestoutputdir,"params-chunk%01d.txt"%procid)
					'''
				if(myid == main_node):
					lowpass, falloff, currentres = read_text_row( os.path.join(bestoutputdir,"current_resolution.txt") )[0]
				currentres = bcast_number_to_all(currentres, source_node = main_node)
				currentres = round(currentres,2)
				#lowpass = bcast_number_to_all(lowpass, source_node = main_node)
				#lowpass = round(lowpass,4)
				#falloff = bcast_number_to_all(falloff, source_node = main_node)
				#falloff = round(falloff,4)
				Tracker["extension"] -= increment
				lowpass = currentres + Tracker["extension"]
				if(mainiteration > 1):
					#  Here to be consistent I would have to know what shrink was for this run
					k = -1
					for i in xrange(len(history)):
						if(history[i]["directory"] == bestoutputdir[-6:]):
							k = i
							break
					if(k == -1):
						print("  something wrong with bestoutputdir")
						exit()
					shrink                = history[i]["shrink"]
					nxresolution          = history[i]["nxresolution"]
					Tracker["initialfl"]  = history[i]["initialfl"]
					Tracker["falloff"]    = history[i]["falloff"]
					Tracker["initialfl"]  = history[i]["initialfl"]
				Tracker["resolution"]  = currentres
				Tracker["lowpass"]     = lowpass
				Tracker["eliminated-outliers"] = eliminated_outliers
				Tracker["movedup"] = False
				keepgoing = 1

		elif( icurrentres == Tracker["icurrentres"] ):
			# We need separate rules for each case
			if(myid == main_node):
				print("  Resolution did not improve, swith to the next move", Tracker["an"], Tracker["local"],icurrentres,lowpass)
			#  Exhaustive searches
			if(Tracker["an"] == "-1" and not Tracker["local"]):
				if(myid == main_node):
					print("  Switching to local searches with an  %s"%options.an)
				Tracker["applyctf"] = True
				falloff = 0.2
				Tracker["local"] = False
				#  keep the same resolution
				icurrentres = Tracker["icurrentres"]
				Tracker["an"] = options.an
				Tracker["nsoft"] = 0
				keepgoing = 1
				if(myid == main_node):
					print("  Switching to local searches with an %s"%Tracker["an"])
					if(Tracker["PWadjustment"] != ""):
						print("  Turning on power spectrum adjustment %s"%Tracker["PWadjustment"])
			#  Local continuous searches
			elif(Tracker["an"] != "-1" and not Tracker["local"]):
				if(myid == main_node):
					print("  Switching to local continuous")
				projdata = [[model_blank(1,1)],[model_blank(1,1)]]
				Tracker["applyctf"] = False
				#  keep the same resolution
				icurrentres = Tracker["icurrentres"]
				Tracker["local"] = True
				#Tracker["an"] = options.an
				Tracker["nsoft"] = 0
				keepgoing = 1
				if(myid == main_node):
					print("  Switching to local searches with an %s"%Tracker["an"])
					if(Tracker["PWadjustment"] != ""):
						print("  Turning on power spectrum adjustment %s"%Tracker["PWadjustment"])
			#  Local/continuous  searches, finishing up
			elif(Tracker["local"]):
				#  Finish up by running continuous at full size
				#  for continuous data cannot be ctf applied.
				projdata = [[model_blank(1,1)],[model_blank(1,1)]]
				Tracker["applyctf"] = False
				Tracker["nsoft"] = 0
				Tracker["local"] = True
				lowpass = currentres + Tracker["extension"]
				nxresolution = 2*(nnxo**2)
				nxinit = nxresolution
				Tracker["nxresolution"]        = nxresolution
				Tracker["nxinit"]              = nxinit
			else:
				print(" Unknown combination of settings in improved resolution path",Tracker["an"],Tracker["local"])
				exit()  #  This will crash the program, but the situation is unlikely to occur
			Tracker["eliminated-outliers"] = eliminated_outliers
			bestoutputdir = mainoutputdir
			keepgoing = 1

			if( Tracker["movedup"] ):
				if(myid == main_node):  print("The resolution did not improve. This is look ahead move.  Let's try to relax slightly and hope for the best")
				Tracker["extension"]    = min(stepforward,0.45-currentres)
				Tracker["movedup"]      = False
				Tracker["initialfl"]    = lowpass
				Tracker["falloff"]      = falloff
				lowpass = currentres + Tracker["extension"]
				shrink  = max(min(2*lowpass + Tracker["falloff"], 1.0), minshrink)
				nxresolution = min(int(nnxo*shrink + 0.5) + Tracker["extension"],nnxo)
				nxresolution += nxresolution%2
				shrink = float(nxresolution)/nnxo
				if( Tracker["nx"] == nnxo):
					keepgoing = 0
				else:
					Tracker["resolution"] = currentres
					Tracker["lowpass"]    = lowpass
					Tracker["falloff"]    = falloff
					Tracker["eliminated-outliers"] = eliminated_outliers
					keepgoing = 1
			else:
				#  The resolution is not moving up.  Check whether this is exhaustive search,
				#    if yes switch to local searches by activating an, tun on PW adjustment, if given.
				#
				if( Tracker["an"] == "-1" ):
					Tracker["an"] = options.an
					Tracker["movedup"] = True
					nsoft = 0
					Tracker["nsoft"] = 0
					paramsdoct["nsoft"] = 0
					if(myid == main_node):  print("  Switching to local searches with an %s and turning off SHC"%Tracker["an"])
					keepgoing = 1
				elif(Tracker["an"] > 0.0 ):
					if( not Tracker["local"] ):
						Tracker["local"]     = True
						Tracker["ts"]        = "2.0"
						Tracker["falloff"]   = falloff
						Tracker["movedup"]   = False
						Tracker["initialfl"] = lowpass
						lowpass = currentres + Tracker["extension"]
						shrink  = max(min(2*lowpass + Tracker["falloff"], 1.0), minshrink)
						nxresolution = min(int(nnxo*shrink + 0.5) + Tracker["extension"],nnxo)
						nxresolution += nxresolution%2
						shrink = float(nxresolution)/nnxo
						if( Tracker["nx"] == nnxo):
							if(myid == main_node):  print("The resolution did not improve and image we reached the full image size.")
							keepgoing = 0
						else:
							Tracker["resolution"] = currentres
							Tracker["lowpass"]    = lowpass
							Tracker["falloff"]    = falloff
							Tracker["eliminated-outliers"] = eliminated_outliers
							Tracker["movedup"] = False
							if(myid == main_node):  print("  Switching to local searches")
							#  We have to decrease angular error as these are "continuous" searches
							Tracker["pixercutoff"] = get_pixercutoff(radi*shrink, degrees(atan(1.0/float(radi*shrink)))/4.0, 0.1)
							keepgoing = 1
					else:
						#  If the resolution did not improve for local, keep current parameters, but increase the image size to full.
						Tracker["ts"]        = "2.0"
						Tracker["falloff"]   = falloff
						Tracker["local"]     = True
						Tracker["movedup"]   = False
						Tracker["initialfl"] = lowpass
						nxresolution = nnxo
						shrink = float(nxresolution)/nnxo
						if( Tracker["nx"] == nnxo):
							if(myid == main_node):  print("The resolution did not improve and image we reached the full image size.")
							keepgoing = 0
						else:
							Tracker["resolution"] = currentres
							Tracker["lowpass"]    = lowpass
							Tracker["falloff"]    = falloff
							Tracker["eliminated-outliers"] = eliminated_outliers
							Tracker["movedup"] = False
							if(myid == main_node):  print("  Resolution id not improve, do local searches at full size")
							#  We have to decrease angular error as these are "continuous" searches
							Tracker["pixercutoff"] = get_pixercutoff(radi*shrink, degrees(atan(1.0/float(radi*shrink)))/4.0, 0.1)
							keepgoing = 1
				"""
#			else:
#				if(myid == main_node):  print("The resolution did not improve.")
#				keepgoing = 0

		if( keepgoing == 1 ):
			nsoft = 0
			if(myid == main_node):
				print("  New shrink and image dimension :",nxresolution, nxinit)
				"""
				#  It does not look like it is necessary, we just have to point to the directory as the files should be there.
				#  Will continue, so update the params files
				for procid in xrange(2):
					#  partids ads partstack contain parameters to be used as starting in the next iteration
					if(not os.path.exists(os.path.join(mainoutputdir,"chunk%01d.txt"%procid))):
						cmd = "{} {} {}".format("cp -p", partids[procid] , os.path.join(mainoutputdir,"chunk%01d.txt"%procid))
						cmdexecute(cmd)
					if(not os.path.exists(os.path.join(mainoutputdir,"params-chunk%01d.txt"%procid))):
						cmd = "{} {} {}".format("cp -p", partstack[procid], os.path.join(mainoutputdir,"params-chunk%01d.txt"%procid))
						cmdexecute(cmd)
				"""
			previousoutputdir = mainoutputdir
			#  maybe resolution should be kept in abs freq units?
			Tracker["resolution"] = Tracker["icurrentres"]
			history.append(Tracker.copy())

		else:
			if(myid == main_node):
				print("  Terminating, the best solution is in the directory main%03d" % Tracker["bestsolution"])
		mpi_barrier(MPI_COMM_WORLD)

	mpi_finalize()


if __name__=="__main__":
	main_mrk01()
