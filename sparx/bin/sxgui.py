#!/usr/bin/env python

#
# Author: Pawel A.Penczek, 09/09/2006 (Pawel.A.Penczek@uth.tmc.edu)
# Copyright (c) 2000-2006 The University of Texas - Houston Medical School
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#

import global_def
from global_def import *
import sys
from PyQt4.Qt import *
from PyQt4 import QtGui
from PyQt4 import QtCore
import os
import subprocess
from subprocess import *
from EMAN2 import *
from sparx import *
from EMAN2_cppwrap import *

#Layout of the Pop Up window infosparx; started by the function info of the main window
class infosparx(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        #Here we just set the window title and  3 different labels, with their positions in the window
	self.setWindowTitle('Sparx GUI Info page')
        title1=QtGui.QLabel('<b>Sparx GUI beta version</b>', self)
	title1.move(10,10)
        title2=QtGui.QLabel('<b>Authors:</b> ', self)
	title2.move(10,40)
        title3=QtGui.QLabel('For more information visit:\nhttp://sparx-em.org/sparxwiki ', self)
	title3.move(10,70)

#helical_start
class PopupHelicalRefinement(QWidget):
    def __init__(self):
        QWidget.__init__(self)
	
	
	# populate with default values
	self.savedparmsdict ={'stackname':'NONE','initialprojectionparameter':'NONE','referencevolume':'NONE','foldername':'NONE','outradius':'-1','xrange':'1.0','xtrans':'1.0','ynumber':"2",'nriter':'3','nproc':'3','dp':'NONE','dphi':'NONE','rmax':'NONE','maskname':'',"delta":"1.0","ringstep":"1","innerradius":"1","ctf":"False","snr":"1.0","initial_theta":"90.0", "delta_theta":"1.0","nise":"2","nise":"2","rmin":"0.0","fract":"0.7","dp_step":"0.1","ndp":"12","dphi_step":"0.1","ndphi":"12","psi_max":"15","an":"-1", "npad":"2", "chunk":"-1.0", "sym":"c1","datasym":"symdoc.dat","usrfunc":"helical","usrfuncfile":""}
	
	
	self.setadv=False
	self.cmd = ""
	x1 = 10
	x2 = x1 + 150
	x3 = x2 + 145
	x4 = x3 + 100
	x5 = 230 # run button
	#Here we just set the window title
	self.setWindowTitle('sxihrsr')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sihrsr</b> - performs helical refinement', self)
	y = 10
	title1.move(10,y)
	
	
	y = y +30
	self.repopbtn = QPushButton("Repopulate With Previously Saved Parameters", self)
        self.repopbtn.move(x1-5,y)
        #sets an infotip for this Pushbutton
        self.repopbtn.setToolTip('Repopulate With Saved Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.repopbtn, SIGNAL("clicked()"), self.repoparms)

	
        #Here we create a Button(file_button with title run open .hdf) and its position in the window
	
	y = y +30	
	self.file_button = QtGui.QPushButton("Open .hdf", self)
	self.file_button.move(x3, y)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button, QtCore.SIGNAL("clicked()"), self.choose_file)
        #exactly the same as above, but for subfunction choose_file1
	self.file_button1 = QtGui.QPushButton("Open .bdb", self)
	self.file_button1.move(x4,y)
	QtCore.QObject.connect(self.file_button1, QtCore.SIGNAL("clicked()"), self.choose_file1)
	#Example for User input stack name
        #First create the label and define its position
	stackname= QtGui.QLabel('Name of input stack', self)
	stackname.move(x1,y)
        #Now add a line edit and define its position
	self.stacknameedit=QtGui.QLineEdit(self)
        self.stacknameedit.move(x2,y)
        #Adds a default value for the line edit
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	
	# file_button2 for input parameters
	
	y = y +30	
	self.file_button2 = QtGui.QPushButton("Open .txt", self)
	self.file_button2.move(x3, y)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button2, QtCore.SIGNAL("clicked()"), self.choose_file2)
	parameterfile= QtGui.QLabel('Projection params file', self)
	parameterfile.move(x1,y)
        #Now add a line edit and define its position
	self.initialprojectionparameteredit=QtGui.QLineEdit(self)
        self.initialprojectionparameteredit.move(x2,y)
        #Adds a default value for the line edit
	self.initialprojectionparameteredit.setText(self.savedparmsdict['initialprojectionparameter'])
	
	# file_button3 for referencevolume
	y = y +30	
	self.file_button3 = QtGui.QPushButton("Open .hdf", self)
	self.file_button3.move(x3, y)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button3, QtCore.SIGNAL("clicked()"), self.choose_file3)
	volumefile= QtGui.QLabel('Initial volume', self)
	volumefile.move(x1,y)
        #Now add a line edit and define its position
	self.referencevolumeedit=QtGui.QLineEdit(self)
        self.referencevolumeedit.move(x2,y)
        #Adds a default value for the line edit
	self.referencevolumeedit.setText(self.savedparmsdict['referencevolume'])
	

	#The same as above, but many line edits include Infotips
	y = y +30	
	foldername= QtGui.QLabel('Output folder', self)
	foldername.move(x1,y)
	self.foldernameedit=QtGui.QLineEdit(self)
	self.foldernameedit.move(x2,y)
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	
	
	y = y +30
	outradius= QtGui.QLabel('Particle outer radius', self)
	outradius.move(x1, y )
	self.outradiusedit=QtGui.QLineEdit(self)
	self.outradiusedit.move(x2,y)
	self.outradiusedit.setText(self.savedparmsdict['outradius'])
	self.outradiusedit.setToolTip('Parameter ou: Outer radius for rotational correlation \nshould be set to particle radius\nif not sure, set to boxsize/2-2 ')
	
	y = y +30	
	xrange= QtGui.QLabel('X search range', self)
	xrange.move(x1,y)
	self.xrangeedit=QtGui.QLineEdit(self)
	self.xrangeedit.move(x2,y)
	self.xrangeedit.setText(self.savedparmsdict['xrange'])
	self.xrangeedit.setToolTip('Range for translational search in x\nif set to 0 no x directional alignment will be performed')
	y = y +30
	xtrans= QtGui.QLabel('Step of x', self)
	xtrans.move(x1,y)
	self.xtransedit=QtGui.QLineEdit(self)
	self.xtransedit.move(x2,y)
	self.xtransedit.setText(self.savedparmsdict['xtrans'])
	self.xtransedit.setToolTip('Step of translational search in x direction\nlarger values increase the speed but decrease the accuracy')
	
	y = y +30	
	ynumber= QtGui.QLabel('Number of y search', self)
	ynumber.move(x1,y)
	self.ynumberedit=QtGui.QLineEdit(self)
	self.ynumberedit.move(x2,y)
	self.ynumberedit.setText(self.savedparmsdict['ynumber'])
	self.ynumberedit.setToolTip('number of steps in y direction\n ystep will be dp/ynumber')
		
	y = y +30	
	dp= QtGui.QLabel('Helical rise (angstrom)', self)
	dp.move(x1,y)
	self.dpedit=QtGui.QLineEdit(self)
	self.dpedit.move(x2,y)
	self.dpedit.setText(self.savedparmsdict['dp'])
	self.dpedit.setToolTip('helical rise in angstrom')
	
	y = y +30	
	dphi= QtGui.QLabel('Helical angle', self)
	dphi.move(x1,y)
	self.dphiedit=QtGui.QLineEdit(self)
	self.dphiedit.move(x2,y)
	self.dphiedit.setText(self.savedparmsdict['dp'])
	self.dphiedit.setToolTip('helical angle in degree')	
	
	y = y +30	
	rmax= QtGui.QLabel('Helical out radius', self)
	rmax.move(x1,y)
	self.rmaxedit=QtGui.QLineEdit(self)
	self.rmaxedit.move(x2,y)
	self.rmaxedit.setText(self.savedparmsdict['rmax'])
	self.rmaxedit.setToolTip('helical out radious')	
	
	y = y +30	
	self.CTF_radio_button=QtGui.QRadioButton('CTF on', self)
	self.CTF_radio_button.move(x1,y)
	self.CTF_radio_button.setChecked(True)
		
	y = y +30
	nriter= QtGui.QLabel('Number of iterations', self)
	nriter.move(x1,y)
	self.nriteredit=QtGui.QLineEdit(self)
	self.nriteredit.move(x2,y)
	self.nriteredit.setText(self.savedparmsdict['nriter'])
	self.nriteredit.setToolTip('Maximum number of iterations the program will perform\n ')
	
	y = y +30
	nproc= QtGui.QLabel('Number of CPUs (>1)', self)
	nproc.move(x1,y)
	self.nprocedit=QtGui.QLineEdit(self)
	self.nprocedit.move(x2,y)
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	self.nprocedit.setToolTip('The number of processors to use, need to be >=2 since we only surrport MPI version')
	
      
	y = y +30
	header=QtGui.QLabel('Active parameters and xform.projection must be set in the input stack', self)
	header.move(x1,y)
	
	#not linked to a function yet
	
	y = y +30
        self.activeheader_button = QtGui.QPushButton("Activate all images", self)
	self.activeheader_button.move(x1-5, y)
	self.connect(self.activeheader_button, SIGNAL("clicked()"), self.setactiveheader)
	self.projectionheader_button = QtGui.QPushButton("Set xform.projection", self)
	self.projectionheader_button.move(x1+180, y)
	self.projectionheader_button.setToolTip('Depending whether the projection parameters given or not, set xform projection to zero or specific vlues ')
	self.connect(self.projectionheader_button, SIGNAL("clicked()"), self.setprojectionheader)
	
	
	y = y +30
	self.advbtn = QPushButton("Advanced Parameters", self)
        self.advbtn.move(x1-5, y)
        #sets an infotip for this Pushbutton
        self.advbtn.setToolTip('Set Advanced Parameters for helical refinement such as center and CTF')
        #when this button is clicked, this action starts the subfunction advanced params
        self.connect(self.advbtn, SIGNAL("clicked()"), self.advparams)
		
	y = y +30
	self.savepbtn = QPushButton("Save Input Parameters", self)
        self.savepbtn.move(x1-5, y)
        #sets an infotip for this Pushbutton
        self.savepbtn.setToolTip('Save Input Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.savepbtn, SIGNAL("clicked()"), self.saveparms)
	
	y = y +30
	self.cmdlinebtn = QPushButton("Generate command line from input parameters", self)
        self.cmdlinebtn.move(x1-5, y)
        #sets an infotip for this Pushbutton
        self.cmdlinebtn.setToolTip('Generate command line using input parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.cmdlinebtn, SIGNAL("clicked()"), self.gencmdline)

	 #Here we create a Button(Run_button with title run sxali2d) and its position in the window
	
	y = y +30
	self.RUN_button = QtGui.QPushButton('Run sxihrsr', self)
	# make 3D textured push button look
	s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
	
	self.RUN_button.setStyleSheet(s)


	self.RUN_button.move(x5, y)
        #Here we define, that when this button is clicked, it starts subfunction runsxali2d
        self.connect(self.RUN_button, SIGNAL("clicked()"), self.runsxihrsr)
        #Labels and Line Edits for User Input
	y = y +30
	outinfo= QtGui.QLabel('Output files (logfile, projection parameter files and pix error files)\nvol--reconstructed volume, volf--reconstructed volume after helicising and user function \n xform.projection was stored in each image header. ', self)
	outinfo.move(x1,y)

	


	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
   
    def gencmdline(self,writefile=True):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
   	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	
        projectionparameters = self.initialprojectionparameteredit.text()
	print "Input parameter files="+ projectionparameters
	referencevolume = self.referencevolumeedit.text()
	print "Initial volume="+ referencevolume
		
	output=self.foldernameedit.text()
	print "output folder="+ output
	ou=self.outradiusedit.text()
	print "Outer radius="+ ou
	xr=self.xrangeedit.text()
	print "xr=" +xr
	ynumber=self.ynumberedit.text()
	print "ynumber=" +ynumber	
	tx=self.xtransedit.text()
	print "tx=" +tx
	dp=self.dpedit.text()
	print "dp=" +dp
	dphi=self.dphiedit.text()
	print "dp=" +dphi
	rmax=self.rmaxedit.text()
	print "rmax==",rmax
	maxit=self.nriteredit.text()
	print "maxit="+maxit
	
	cmd1 = " sxihrsr.py "+str(stack) +" "+str(referencevolume)+" " + str(output)
	
	args = " --ou="+ str(ou)+ " --xr="+str(xr)+" "+ " --ynumber="+str(ynumber)+" "+ " --txs="+str(tx)+" " + " --dp="+str(dp)+" " + " --dphi="+str(dphi)+" "+ " --rmax="+str(rmax)+" " + " --maxit="+ str(maxit) 
	if (self.CTF_radio_button.isChecked() ):
		args = args +" --CTF"
		CTF = "True"
	else:
		CTF = "False"
	
	mask=self.savedparmsdict['maskname']
	delta=self.savedparmsdict['delta']
	ringstep=self.savedparmsdict['ringstep']
	inrad=self.savedparmsdict['innerradius']
	snr=self.savedparmsdict['snr']
	initial_theta=self.savedparmsdict['initial_theta']
	delta_theta=self.savedparmsdict['delta_theta']
	nise=self.savedparmsdict['nise']
	rmin = self.savedparmsdict['rmin']
	fract = self.savedparmsdict['fract']
	dp_step = self.savedparmsdict['dp_step']
	ndp = self.savedparmsdict['ndp']
	dphi_step = self.savedparmsdict['dphi_step']
	ndphi = self.savedparmsdict['ndphi']
	psi_max = self.savedparmsdict['psi_max']
	an = self.savedparmsdict['an']
	npad = self.savedparmsdict['npad']
	chunk = self.savedparmsdict['chunk']
	sym =self.savedparmsdict['sym']
	datasym =self.savedparmsdict['datasym']
	
	userf=''
	userfile=''
	
	if self.setadv:
		mask = self.w.masknameedit.text()
		if len(str(mask))> 1:
			cmd1 = cmd1+" "+str(mask) 
	cmd1 = cmd1 + args
	
	if self.setadv:	
		delta=self.w.deltaedit.text()
		cmd1 = cmd1+" --delta=" +str(delta)
		
		ringstep = self.w.ringstepedit.text()
		cmd1 = cmd1+" --rs="+str(ringstep)
		
		inrad = self.w.innerradiusedit.text()
		cmd1 = cmd1 + " --ir=" + str(inrad)
		
				
		snr = self.w.snredit.text()
		cmd1 = cmd1 + " --snr=" + str(snr)
		
		initial_theta = self.w.initial_thetaedit.text()
		cmd1 = cmd1 + " --initial_theta=" + str(initial_theta)
			
		delta_theta = self.w.delta_thetaedit.text()
		cmd1 = cmd1 + " --delta_theta=" + str(delta_theta)
		
		nise = self.w.niseedit.text()
		cmd1 = cmd1 + " --nise=" + str(nise)
		
		rmin = self.w.rminedit.text()
		cmd1 = cmd1 + " --rmin=" + str(rmin)
		
		fract = self.w.fractedit.text()
		cmd1 = cmd1 + " --fract=" + str(fract)
		
		dp_step = self.w.dp_stepedit.text()
		cmd1 = cmd1 + " --dp_step=" + str(dp_step)
		
		ndp = self.w.ndpedit.text()
		cmd1 = cmd1 + " --ndp=" + str(ndp)
		
		dphi_step = self.w.dphi_stepedit.text()
		cmd1 = cmd1 + " --dphi_step=" + str(dphi_step)
		
		ndphi = self.w.ndphiedit.text()
		cmd1 = cmd1 + " --ndphi=" + str(ndphi)
		
		psi_max = self.w.psi_maxedit.text()
		cmd1 = cmd1 + " --psi_max=" + str(psi_max)
		
		an = self.w.anedit.text()
		cmd1 = cmd1 + " --an=" + str(an)
		
		npad = self.w.npadedit.text()
		cmd1 = cmd1 + " --npad=" + str(npad)
		
		chunk = self.w.chunkedit.text()
		cmd1 = cmd1 + " --chunk=" + str(chunk)
		
		sym = self.w.symedit.text()
		cmd1 = cmd1 + " --sym=" + str(sym)
		datasym = self.w.datasymedit.text()
		cmd1 = cmd1 + " --datasym=" + str(datasym)
		
		userf = self.w.usrfuncedit.text()
		
		userfile = self.w.usrfuncfileedit.text()
		
		if len(userfile) <= 1:
			cmd1 = cmd1 + " --function="+str(userf)
		else:
			userfile = self.w.usrfuncfileedit.text()
			userfile = str(userfile)
			if len(userfile) > 1:
				# break it down into file name and directory path
				rind = userfile.rfind('/')
				fname = userfile[rind+1:]
				fname, ext = os.path.splitext(fname)
				fdir = userfile[0:rind]
				cmd1 = cmd1 + " --function=\"[" +fdir+","+fname+","+str(userf)+"]\""
	
	np = self.nprocedit.text()
	
	self.savedparmsdict = {'stackname':str(stack),'initialprojectionparameter':str(projectionparameters),'referencevolume':str(referencevolume),'foldername':str(output),'outradius':str(ou),'xrange':str(xr),'xtrans':str(tx),'ynumber':str(ynumber),'dp':str(dp),'dphi':str(dphi),'rmax':str(rmax),'nriter':str(maxit),'nproc':str(np),'maskname':str(mask),'delta':str(delta),"ringstep":str(ringstep),"innerradius":str(inrad),"ctf":str(CTF),"snr":str(snr),"initial_theta":str(initial_theta), "delta_theta":str(delta_theta),"nise":str(nise),"rmin":str(rmin),"fract":str(fract),"dp_step":str(dp_step),"ndp":str(ndp),"dphi_step":str(dphi_step),"ndphi":str(ndphi),"psi_max":str(psi_max),"an":str(an), "npad":str(npad), "chunk":str(chunk),"sym":str(sym),"datasym":str(datasym),"usrfunc":str(userf), "usrfuncfile":str(userfile)}
	
	
	
	
	
	if self.setadv:
		self.w.savedparmsdict=self.savedparmsdict
	
	if int(str(np)) > 1:
		cmd1="mpirun -np "+ str(np) + " "+ cmd1+" --MPI" 
	
	if writefile:	
		from time import localtime
		a=time.localtime()
		fname = 'ihrsrcmd_%02d_%02d_%04d_%02d_%02d_%02d.txt'%(a.tm_mday,a.tm_mon, a.tm_year,a.tm_hour, a.tm_min, a.tm_sec)
		f = open(fname,'a')
		f.write(cmd1)
		f.write('\n')
		f.close()
	
	print cmd1
	self.cmd = cmd1
	
    def runsxihrsr(self):
	self.gencmdline(writefile=False)
	outfolder=self.savedparmsdict['foldername']
	if os.path.exists(outfolder):
		print "output folder "+outfolder+" already exists!"
		return
	process = subprocess.Popen(self.cmd,shell=True)
	self.emit(QtCore.SIGNAL("process_started"),process.pid)
	
    def saveparms(self):	
	# save all the parms in a text file so we can repopulate if user requests
	import pickle
	parameter_name = QtGui.QFileDialog.getSaveFileName(self, "Save Parameter File", "", "pkl files (*.pkl)")
        #after the user selected a file, we obtain this filename as a Qstring
	parameter_name=QtCore.QString(parameter_name)
	output=open(parameter_name,'wb')
	self.gencmdline(writefile=False)
	pickle.dump(self.savedparmsdict,output)
	output.close()

    def repoparms(self):
    
  	
	# repopulate with saved parms
	import pickle
	parameter_name = QtGui.QFileDialog.getOpenFileName(self, "Open Parameter File", "", "pkl files (*.pkl)")
        #after the user selected a file, we obtain this filename as a Qstring
	parameter_name=QtCore.QString(parameter_name)
	
	pkl = open(parameter_name,'rb')
	self.savedparmsdict = pickle.load(pkl)
	print self.savedparmsdict
	self.outradiusedit.setText(self.savedparmsdict['outradius'])
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	self.initialprojectionparameteredit.setText(self.savedparmsdict['initialprojectionparameter'])	
	self.referencevolumeedit.setText(self.savedparmsdict['referencevolume'])	
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	self.xrangeedit.setText(self.savedparmsdict['xrange'])
	self.xtransedit.setText(self.savedparmsdict['xtrans'])
	self.ynumberedit.setText(self.savedparmsdict['ynumber'])
	self.dpedit.setText(self.savedparmsdict['dp'])
	self.dphiedit.setText(self.savedparmsdict['dphi'])
	self.rmaxedit.setText(self.savedparmsdict['rmax'])
	self.nriteredit.setText(self.savedparmsdict['nriter'])
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	if( self.savedparmsdict['ctf'] == str("True")):
		self.CTF_radio_button.setChecked(True)
	else:
		self.CTF_radio_button.setChecked(False)
	if self.setadv:
		self.w.masknameedit.setText(self.savedparmsdict['maskname'])
		self.w.deltaedit.setText(self.savedparmsdict['delta'])
		self.w.ringstepedit.setText(self.savedparmsdict['ringstep'])
		self.w.innerradiusedit.setText(self.savedparmsdict['innerradius'])
		self.w.snredit.setText(self.savedparmsdict['snr'])
		self.w.initial_thetaedit.setText(self.savedparmsdict['initial_theta'])
		self.w.delta_thetaedit.setText(self.savedparmsdict['delta_theta'])
		self.w.niseedit.setText(self.savedparmsdict['nise'])
		self.w.symedit.setText(self.savedparmsdict['sym'])
		self.w.datasymedit.setText(self.savedparmsdict['datasym'])
		self.w.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
		self.w.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
		
    def advparams(self):
        print "Opening a new popup window..."
        self.w = Popupadvparams_helical(self.savedparmsdict)
        self.w.resize(500,800)
        self.w.show()
	self.setadv=True
    def setactiveheader(self):
	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	header(str(stack), "active", one=True)
	
    def setprojectionheader(self):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
	stack = self.stacknameedit.text()
	input_file = self.initialprojectionparameteredit.text()
	print "stack defined="+ stack
	if( str(input_file) == "NONE" or len( str(input_file) ) <=1  ):
		header(str(stack),'xform.projection',zero=True)
		print "zero projection"
	else:
        	header(str(stack),'xform.projection',fimport = str(input_file) )
		print "set projection based on input file"	


	
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked
    def choose_file(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.stacknameedit.setText(str(a))
        
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked (same as above but for bdb files(maybe we can combine these two into one function)
    def choose_file1(self):
	file_name1 = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "EMAN2DB/", "BDB FILES (*.bdb)" )
	a=QtCore.QString(file_name1)
	b=os.path.basename(str(a))
	c=os.path.splitext(b)[0]
	d="bdb:"+c
	print d
	self.stacknameedit.setText(d)
    def choose_file2(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.txt)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.initialprojectionparameteredit.setText(str(a))
	
    def choose_file3(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Reference Volume", "", "hdf files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.referencevolumeedit.setText(str(a))

class Popupadvparams_helical(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
        #Here we just set the window title
	self.setWindowTitle('sxihrsr advanced parameter selection')
        #Here we just set a label and its position in the window
	x1 = 10
	x2 = x1 + 150
	x3 = x2 + 145
	x4 = x3 + 100
	y = 10
	title1=QtGui.QLabel('<b>sxihrsr</b> - set advanced params', self)
	title1.move(10,y)
        #Labels and Line Edits for User Input
        #Just a label
	y = y +20
	title2= QtGui.QLabel('<b>Advanced</b> parameters', self)
	title2.move(10,y)

	self.savedparmsdict=savedparms
        #Example for User input stack name
        #First create the label and define its position
	y = y+20
	maskname= QtGui.QLabel('Mask', self)
	maskname.move(x1,y)
        #Now add a line edit and define its position
	self.masknameedit=QtGui.QLineEdit(self)
        self.masknameedit.move(x2,y)
        #Adds a default value for the line edit
	self.masknameedit.setText(self.savedparmsdict['maskname'])
	self.masknameedit.setToolTip("Default is a circle mask with radius equal to the particle radius")
	
	self.mskfile_button = QtGui.QPushButton("Open .hdf", self)
	self.mskfile_button.move(x3, y-2)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.mskfile_button, QtCore.SIGNAL("clicked()"), self.choose_mskfile)
	
	y = y+30
	delta= QtGui.QLabel('Angular step', self)
	delta.move(x1,y)
	self.deltaedit=QtGui.QLineEdit(self)
	self.deltaedit.move(x2,y)
	self.deltaedit.setText(self.savedparmsdict["delta"])
	self.deltaedit.setToolTip("angular step of reference projections\n defualt = 1.0")
	
	y = y + 30
	ringstep= QtGui.QLabel('Ring step', self)
	ringstep.move(x1,y)
	self.ringstepedit=QtGui.QLineEdit(self)
	self.ringstepedit.move(x2,y)
	self.ringstepedit.setText(self.savedparmsdict['ringstep'])
	self.ringstepedit.setToolTip('step between rings in rotational correlation > 0 (set to 1)')

	y = y + 30
	innerradius= QtGui.QLabel('Particle inner radius', self)
	innerradius.move(x1,y)
	self.innerradiusedit=QtGui.QLineEdit(self)
	self.innerradiusedit.move(x2,y)
	self.innerradiusedit.setText(self.savedparmsdict['innerradius'])
	self.innerradiusedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	
	
	y = y +30
	snr= QtGui.QLabel('SNR', self)
	snr.move(x1,y)
	self.snredit=QtGui.QLineEdit(self)
	self.snredit.move(x2,y)
	self.snredit.setText(self.savedparmsdict['snr'])
	self.snredit.setToolTip('signal-to-noise ratio of the data (default SNR=1.0)')	
		
	y = y + 30
	initial_theta= QtGui.QLabel('Initial theta', self)
	initial_theta.move(x1,y)
	self.initial_thetaedit=QtGui.QLineEdit(self)
	self.initial_thetaedit.move(x2,y)
	self.initial_thetaedit.setText(self.savedparmsdict['initial_theta'])
	self.initial_thetaedit.setToolTip('intial theta for reference projection, default 90.0)')
	
	y = y + 30
	delta_theta= QtGui.QLabel('Theta step', self)
	delta_theta.move(x1,y)
	self.delta_thetaedit=QtGui.QLineEdit(self)
	self.delta_thetaedit.move(x2,y)
	self.delta_thetaedit.setText(self.savedparmsdict['delta_theta'])
	self.delta_thetaedit.setToolTip('step of theta for reference projection, default 1.0)')

	y = y + 30
	nise = QtGui.QLabel('Nise', self)
	nise.move(x1,y)
	self.niseedit=QtGui.QLineEdit(self)
	self.niseedit.move(x2,y)
	self.niseedit.setText(self.savedparmsdict['nise'])
	self.niseedit.setToolTip('start symmetrization searching after nise steps')	
	
	y = y + 30
	rmin = QtGui.QLabel('Helical inner radius', self)
	rmin.move(x1,y)
	self.rminedit=QtGui.QLineEdit(self)
	self.rminedit.move(x2,y)
	self.rminedit.setText(self.savedparmsdict['rmin'])
	self.rminedit.setToolTip('Inner radius of the helix')	
	
	y = y + 30
	fract = QtGui.QLabel('Fraction used', self)
	fract.move(x1,y)
	self.fractedit=QtGui.QLineEdit(self)
	self.fractedit.move(x2,y)
	self.fractedit.setText(self.savedparmsdict['fract'])
	self.fractedit.setToolTip('fraction of the volume used for helicising')	
	
	y = y + 30
	dp_step = QtGui.QLabel('Dp step', self)
	dp_step.move(x1,y)
	self.dp_stepedit=QtGui.QLineEdit(self)
	self.dp_stepedit.move(x2,y)
	self.dp_stepedit.setText(self.savedparmsdict['dp_step'])
	self.dp_stepedit.setToolTip('step size of helicise rise search')
	
	y = y + 30
	ndp = QtGui.QLabel('Number of dp search', self)
	ndp.move(x1,y)
	self.ndpedit=QtGui.QLineEdit(self)
	self.ndpedit.move(x2,y)
	self.ndpedit.setText(self.savedparmsdict['ndp'])
	self.ndpedit.setToolTip('In symmetrization search, number of delta z steps equas to 2*ndp+1')	
	
	y = y + 30
	dphi_step = QtGui.QLabel('Dphi step', self)
	dphi_step.move(x1,y)
	self.dphi_stepedit=QtGui.QLineEdit(self)
	self.dphi_stepedit.move(x2,y)
	self.dphi_stepedit.setText(self.savedparmsdict['dphi_step'])
	self.dphi_stepedit.setToolTip('step size of helicise angle search')
	
	y = y + 30
	ndphi = QtGui.QLabel('Number of dphi search', self)
	ndphi.move(x1,y)
	self.ndphiedit=QtGui.QLineEdit(self)
	self.ndphiedit.move(x2,y)
	self.ndphiedit.setText(self.savedparmsdict['ndphi'])
	self.ndphiedit.setToolTip('In symmetrization search, number of angular steps equas to 2*ndphi+1')	
	
	y = y + 30
	psi_max = QtGui.QLabel('Maximum psi', self)
	psi_max.move(x1,y)
	self.psi_maxedit=QtGui.QLineEdit(self)
	self.psi_maxedit.move(x2,y)
	self.psi_maxedit.setText(self.savedparmsdict['psi_max'])
	self.psi_maxedit.setToolTip('maximum psi - how far rotation in plane can can deviate from 90 or 270 degrees')	
	
	y = y + 30
	an = QtGui.QLabel('Angular neighborhood', self)
	an.move(x1,y)
	self.anedit=QtGui.QLineEdit(self)
	self.anedit.move(x2,y)
	self.anedit.setText(self.savedparmsdict['an'])
	self.anedit.setToolTip('angular neighborhood for local searches, defaut -1')	
	
	y = y + 30
	npad = QtGui.QLabel('Npad', self)
	npad.move(x1,y)
	self.npadedit=QtGui.QLineEdit(self)
	self.npadedit.move(x2,y)
	self.npadedit.setText(self.savedparmsdict['npad'])
	self.npadedit.setToolTip('padding size for 3D reconstruction, please use npad = 2')	
	
	y = y + 30
	chunk = QtGui.QLabel('Chunk', self)
	chunk.move(x1,y)
	self.chunkedit=QtGui.QLineEdit(self)
	self.chunkedit.move(x2,y)
	self.chunkedit.setText(self.savedparmsdict['chunk'])
	self.chunkedit.setToolTip('percentage of data used for alignment')	

	y = y + 30
	sym = QtGui.QLabel('Point group symmetry', self)
	sym.move(x1,y)
	self.symedit=QtGui.QLineEdit(self)
	self.symedit.move(x2,y)
	self.symedit.setText(self.savedparmsdict['sym'])
	self.symedit.setToolTip('now support cn and dn group symmetry')
	
	y = y + 30
	datasym = QtGui.QLabel('File to save dp, dphi', self)
	datasym.move(x1,y)
	self.datasymedit=QtGui.QLineEdit(self)
	self.datasymedit.move(x2,y)
	self.datasymedit.setText(self.savedparmsdict['datasym'])
	self.datasymedit.setToolTip('file to save helical parameters of each iteration')	
	
	y = y + 30
	usrfunc= QtGui.QLabel('User Function Name', self)
	usrfunc.move(x1,y)
	self.usrfuncedit=QtGui.QLineEdit(self)
	self.usrfuncedit.move(x2,y)
	self.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
	self.usrfuncedit.setToolTip('name of the user-supplied-function that prepares reference image for each iteration')
	
	y = y +30	
	usrfuncfile= QtGui.QLabel('Enter (full path) name of external file containing user function:', self)
	usrfuncfile.move(x1,y)
	y = y + 30
	usrfuncfile= QtGui.QLabel('(Leave blank if file is not external to Sparx)', self)	
	usrfuncfile.move(x1,y)
	y = y + 30
	self.usrfuncfileedit=QtGui.QLineEdit(self)
	self.usrfuncfileedit.move(x2,y)
	self.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
	self.usrfuncfileedit.setToolTip('name of the external file containing user function')	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    	#Here we define, that when this button is clicked, it starts subfunction choose_file
	self.usrfile_button = QtGui.QPushButton("Select File", self)
	self.usrfile_button.move(x3, y)
	QtCore.QObject.connect(self.usrfile_button, QtCore.SIGNAL("clicked()"), self.choose_usrfile)
	
    def choose_usrfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing User Fuction", "", "py files (*.py)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.usrfuncfileedit.setText(str(a))
	
    def choose_mskfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing Mask", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.masknameedit.setText(str(a))
#helical_end		



#Layout of the Pop Up window Popuptwodali (for sxali2d); started by the function twodali of the main window        
class Popuptwodali(QWidget):
    def __init__(self):
        QWidget.__init__(self)
	
	#######################################################################################
	# class variables
	
	self.cmd = ""
	# populate with default values
	self.savedparmsdict = {'stackname':'NONE','foldername':'NONE','partradius':'-1','xyrange':'4 2 1 1','trans':'2 1 0.5 0.25','nriter':'3','nproc':'1','maskname':'','center':'-1',"ringstep":"1","innerradius":"1","ctf":Qt.Unchecked,"snr":"1.0","fourvar":Qt.Unchecked, "gpnr":"-1","usrfunc":"ref_ali2d","usrfuncfile":""}

	#######################################################################################
	# Layout parameters
	
	self.y1 = 10 # title and Repopulate button
	self.y2 = self.y1 + 78 # Text boxes for inputting parameters
	self.y3 = self.y2 + 222 # activate images button and set xform.align2d button
	self.y4 = self.y3 + 80 # Advanced Parameters, Save Input and Generate command line buttons
	self.y5 = self.y4 + 95 # run button 
	self.yspc = 4
	
	self.x1 = 10 # first column (text box labels)
	self.x2 = self.x1 + 150 # second column (text boxes)
	self.x3 = self.x2+145 # third column (Open .hdf button)
	self.x4 = self.x3+100 # fourth column (Open .bdb button)
	self.x5 = 230 # run button
	#######################################################################################
	
        #Here we just set the window title
	self.setWindowTitle('sxali2d')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxali2d</b> - performs 2D reference free alignment of an image series', self)
	title1.move(self.x1,self.y1)
	self.y1 += 30

	self.repopbtn = QPushButton("Repopulate With Saved Parameters", self)
        self.repopbtn.move(self.x1-5,self.y1)
        #sets an infotip for this Pushbutton
        self.repopbtn.setToolTip('Repopulate With Saved Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.repopbtn, SIGNAL("clicked()"), self.repoparms_ali2d)

	#######################################################################################
        #Here we create a Button(file_button with title run open .hdf) and its position in the window
	self.file_button = QtGui.QPushButton("Open .hdf", self)
	self.file_button.move(self.x3, self.y2-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button, QtCore.SIGNAL("clicked()"), self.choose_file)
        #exactly the same as above, but for subfunction choose_file1
	self.file_button1 = QtGui.QPushButton("Open .bdb", self)
	self.file_button1.move(self.x4,self.y2-self.yspc)
	QtCore.QObject.connect(self.file_button1, QtCore.SIGNAL("clicked()"), self.choose_file1)
	
	stackname= QtGui.QLabel('Name of input stack', self)
	stackname.move(self.x1,self.y2)
	self.stacknameedit=QtGui.QLineEdit(self)
        self.stacknameedit.move(self.x2,self.y2)
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	self.y2 += 30
	
	foldername= QtGui.QLabel('Output folder', self)
	foldername.move(self.x1,self.y2)
	self.foldernameedit=QtGui.QLineEdit(self)
	self.foldernameedit.move(self.x2,self.y2)
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	
	self.outinfobtn = QPushButton("Output Info", self)
        self.outinfobtn.move(self.x3,  self.y2-self.yspc)
        #sets an infotip for this Pushbutton
        self.outinfobtn.setToolTip('Output Info')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.outinfobtn, SIGNAL("clicked()"), self.outputinfo_ali2d)
	self.y2 += 30
	
	partradius= QtGui.QLabel('Particle radius', self)
	partradius.move(self.x1,self.y2)
	self.partradiusedit=QtGui.QLineEdit(self)
	self.partradiusedit.move(self.x2,self.y2)
	self.partradiusedit.setText(self.savedparmsdict['partradius'])
	self.partradiusedit.setToolTip('Parameter ou: Outer radius for rotational correlation \nshould be set to particle radius\nif not sure, set to boxsize/2-2 ')	
	self.y2 += 30

	xyrange= QtGui.QLabel('xy range', self)
	xyrange.move(self.x1,self.y2)
	self.xyrangeedit=QtGui.QLineEdit(self)
	self.xyrangeedit.move(self.x2,self.y2)
	self.xyrangeedit.setText(self.savedparmsdict['xyrange'])
	self.xyrangeedit.setToolTip('Range for translational search in x, y direction\nif set to 0 only rotational alignment will be performed')
	self.y2 += 30
	
	trans= QtGui.QLabel('translational step', self)
	trans.move(self.x1,self.y2)
	self.transedit=QtGui.QLineEdit(self)
	self.transedit.move(self.x2,self.y2)
	self.transedit.setText(self.savedparmsdict['trans'])
	self.transedit.setToolTip('Step of translational search in x, y direction\nlarger values increase the speed but decrease the accuracy')	
	self.y2 += 30
	
	nriter= QtGui.QLabel('Number of Iterations', self)
	nriter.move(self.x1,self.y2)
	self.nriteredit=QtGui.QLineEdit(self)
	self.nriteredit.move(self.x2,self.y2)
	self.nriteredit.setText(self.savedparmsdict['nriter'])
	self.nriteredit.setToolTip('Maximum number of iterations the program will perform\n Using the default values the program will run 3 rounds with xy-range 4 and translational step 1, 3 rounds with xyrange 2 and translational step 1 and so on..\nif set to 0 maximum iteration number will be 10 and will automatically stop should the criterion falls')
	self.y2 += 30
	
	nproc= QtGui.QLabel('Number of Processors', self)
	nproc.move(self.x1,self.y2)
	self.nprocedit=QtGui.QLineEdit(self)
	self.nprocedit.move(self.x2,self.y2)
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	self.nprocedit.setToolTip('The number of processors to use. Default is single processor mode')

	##########################################################
	
	header=QtGui.QLabel('Attributes xform.align2d and active parameters must be set in the input stack', self)
	header.move(self.x1,self.y3)
	self.y3 += 30
	
        #not linked to a function yet
        self.activeheader_button = QtGui.QPushButton("activate all images", self)
	self.activeheader_button.move(self.x1-5, self.y3)
	self.connect(self.activeheader_button, SIGNAL("clicked()"), self.setactiveheader)
	
	self.a2dheader_button = QtGui.QPushButton("set xform.align2d", self)
	self.a2dheader_button.move(self.x1-5+180, self.y3)
	self.connect(self.a2dheader_button, SIGNAL("clicked()"), self.seta2dheader)
	
	######################################################################################
	
	self.savepbtn = QPushButton("Save Input Parameters", self)
        self.savepbtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.savepbtn.setToolTip('Save Input Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.savepbtn, SIGNAL("clicked()"), self.saveparms)
	self.y4+=30
	
	self.cmdlinebtn = QPushButton("Generate command line from input parameters", self)
        self.cmdlinebtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.cmdlinebtn.setToolTip('Generate command line using input parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.cmdlinebtn, SIGNAL("clicked()"), self.gencmdline_ali2d)

	#######################################################################
	 #Here we create a Button(Run_button with title run sxali2d) and its position in the window
	self.RUN_button = QtGui.QPushButton('Run sxali2d', self)
	# make 3D textured push button look
	s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
	
	self.RUN_button.setStyleSheet(s)
	self.RUN_button.move(self.x5, self.y5)
        #Here we define, that when this button is clicked, it starts subfunction runsxali2d
        self.connect(self.RUN_button, SIGNAL("clicked()"), self.runsxali2d)
        #Labels and Line Edits for User Input	

	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    def outputinfo_ali2d(self):
    	QMessageBox.information(self, "ali2d output",'Output files (average of aligned images and Fourier Ring Correlation curve)\nare saved in Output folder. alignment parameters are saved in the attribute \nxform.align2d in each image header. The images themselves are not changed.')
	
    def gencmdline_ali2d(self,writefile=True):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
   	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	output=self.foldernameedit.text()
	print "output folder="+ output
	ou=self.partradiusedit.text()
	print "Particle radius="+ ou
	xr=self.xyrangeedit.text()
	print "xr=" +xr
	yr=self.xyrangeedit.text()
	print "yr=" +yr
	ts=self.transedit.text()
	print "ts=" +ts
	maxit=self.nriteredit.text()
	print "maxit="+maxit
	
	cmd1 = "sxali2d.py "+str(stack) +" "+ str(output)
	
	args = " --ou="+ str(ou)+ " --xr='"+str(xr)+"'"+ " --yr='"+str(yr)+"'"+ " --ts='"+str(ts)+"'"+  " --maxit="+ str(maxit) 
	
	mask = self.w1.masknameedit.text()
		
	if len(str(mask))> 1:
		cmd1 = cmd1+" "+str(mask) 
	cmd1 = cmd1 + args
	
	ctr=self.w1.centeredit.text()
	ringstep = self.w1.ringstepedit.text()
	inrad = self.w1.innerradiusedit.text()
	CTF=self.w1.ctfchkbx.checkState()
	snr = self.w1.snredit.text()
	fourvar = self.w1.fourvarchkbx.checkState()
	gpn = self.w1.gpnredit.text()
	userf = self.w1.usrfuncedit.text()
	userfile = self.w1.usrfuncfileedit.text()
			
	cmd1 = cmd1+" --center=" +str(ctr) +" --rs="+str(ringstep)+ " --ir=" + str(inrad)+ " --snr=" + str(snr)+ " --Ng=" + str(gpn)
	if CTF == Qt.Checked:
		cmd1 = cmd1 + " --CTF"
	if fourvar == Qt.Checked:
		cmd1 = cmd1 + " --Fourvar"	
	if len(userfile) < 1:
		cmd1 = cmd1 + " --function="+str(userf)
	else:
		userfile = str(userfile)
		# break it down into file name and directory path
		rind = userfile.rfind('/')
		
		if rind == -1:
			userfile = os.path.abspath(userfile)
			rind = userfile.rfind('/')
			
		fname = userfile[rind+1:]
		fname, ext = os.path.splitext(fname)
		fdir = userfile[0:rind]
		cmd1 = cmd1 + " --function=\"[" +fdir+","+fname+","+str(userf)+"]\""
		
	np = self.nprocedit.text()
	
	self.savedparmsdict = {'stackname':str(stack),'foldername':str(output),'partradius':str(ou),'xyrange':str(xr),'trans':str(yr),'nriter':str(maxit),'nproc':str(np),'maskname':str(mask),'center':str(ctr),"ringstep":str(ringstep),"innerradius":str(inrad),"ctf":CTF,"snr":str(snr),"fourvar":fourvar, "gpnr":str(gpn),"usrfunc":str(userf), "usrfuncfile":str(userfile)}
	
	self.w1.savedparmsdict=self.savedparmsdict
	
	if int(str(np)) > 1:
		cmd1="mpirun -np "+ str(np) + " "+ cmd1+" --MPI" 
	
	if writefile:	
		(fname,stat)= QInputDialog.getText(self,"Generate Command Line","Enter name of file to save command line in",QLineEdit.Normal,"")
		if stat:
			f = open(fname,'a')
			f.write(cmd1)
			f.write('\n')
			f.close()
	
	print cmd1
	self.cmd = cmd1
	
    def runsxali2d(self):
	self.gencmdline_ali2d(writefile=False)
	outfolder=self.savedparmsdict['foldername']
	if os.path.exists(outfolder):
		print "output folder "+outfolder+" already exists!"
		return
	process = subprocess.Popen(self.cmd,shell=True)
	self.emit(QtCore.SIGNAL("process_started"),process.pid)
	
    def saveparms(self):	
	(fname,stat)= QInputDialog.getText(self,"Save Input Parameters","Enter name of file to save parameters in",QLineEdit.Normal,"")
	if stat:
		import pickle
		output=open(fname,'wb')
		self.gencmdline_ali2d(writefile=False)
		pickle.dump(self.savedparmsdict,output)
		output.close()
	
    def repoparms_ali2d(self):	
	(fname,stat)= QInputDialog.getText(self,"Repopulate Parameters","Enter name of file parameters were saved in",QLineEdit.Normal,"")
	if stat:
		import pickle
		pkl = open(fname,'rb')
		self.savedparmsdict = pickle.load(pkl)
		self.partradiusedit.setText(self.savedparmsdict['partradius'])
		self.stacknameedit.setText(self.savedparmsdict['stackname'])	
		self.foldernameedit.setText(self.savedparmsdict['foldername'])	
		self.xyrangeedit.setText(self.savedparmsdict['xyrange'])
		self.transedit.setText(self.savedparmsdict['trans'])
		self.nriteredit.setText(self.savedparmsdict['nriter'])
		self.nprocedit.setText(self.savedparmsdict['nproc'])
		self.w1.masknameedit.setText(self.savedparmsdict['maskname'])
		self.w1.centeredit.setText(self.savedparmsdict['center'])
		self.w1.ringstepedit.setText(self.savedparmsdict['ringstep'])
		self.w1.innerradiusedit.setText(self.savedparmsdict['innerradius'])
		self.w1.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
		self.w1.snredit.setText(self.savedparmsdict['snr'])
		self.w1.fourvarchkbx.setCheckState(self.savedparmsdict['fourvar'])
		self.w1.gpnredit.setText(self.savedparmsdict['gpnr'])
		self.w1.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
		self.w1.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
		
    
    def setactiveheader(self):
	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	header(str(stack), "active", one=True)

    def seta2dheader(self):
	#opens a file browser, showing files only in .hdf format
	ok=False
	zerostr='set xform.align2d to zero'
	randstr='randomize xform.align2d'
	importstr='import parameters from file'
	(item,stat)= QInputDialog.getItem(self,"xform.align2d","choose option",[zerostr,randstr,importstr])
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	#self.stacknameedit.setText(str(a))
   	choice= str(item)
	stack = self.stacknameedit.text()
	if stat:
		if choice == zerostr:
			header(str(stack),'xform.align2d',zero=True)
		if choice == randstr:
			header(str(stack),'xform.align2d',rand_alpha=True)
		if choice == importstr:
			file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "(*)")
			a=str(QtCore.QString(file_name))
			if len(a)>0:
				header(str(stack),'xform.align2d',fimport=a)
	
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked
    def choose_file(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.stacknameedit.setText(str(a))
        
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked (same as above but for bdb files(maybe we can combine these two into one function)
    def choose_file1(self):
	file_name1 = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "EMAN2DB/", "BDB FILES (*.bdb)" )
	a=QtCore.QString(file_name1)
	b=os.path.basename(str(a))
	c=os.path.splitext(b)[0]
	d="bdb:"+c
	print d
	self.stacknameedit.setText(d)

	
class Popupadvparams_ali2d(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
	
	self.x1 = 10
	self.x2 = 140
	self.x3 = 285
	
	self.y1 = 10
	self.yspc = 4
	
        #Here we just set the window title
	self.setWindowTitle('sxali2d advanced parameter selection')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxali2d</b> - set advanced params', self)
	title1.move(self.x1,self.y1)
        #Labels and Line Edits for User Input
        #Just a label
	self.y1 += 30
	
	title2= QtGui.QLabel('<b>Advanced</b> parameters', self)
	title2.move(self.x1,self.y1)
	
	self.y1 += 30
	
	self.savedparmsdict=savedparms
        #Example for User input stack name
        #First create the label and define its position
	maskname= QtGui.QLabel('Mask', self)
	maskname.move(self.x1,self.y1)
        #Now add a line edit and define its position
	self.masknameedit=QtGui.QLineEdit(self)
        self.masknameedit.move(self.x2,self.y1)
        #Adds a default value for the line edit
	self.masknameedit.setText(self.savedparmsdict['maskname'])
	self.masknameedit.setToolTip("Default is a circle mask with radius equal to the particle radius")
	
	self.mskfile_button = QtGui.QPushButton("Open File", self)
	self.mskfile_button.move(self.x3, self.y1-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.mskfile_button, QtCore.SIGNAL("clicked()"), self.choose_mskfile)
	
	self.y1 += 30
	
	center= QtGui.QLabel('Center type', self)
	center.move(self.x1,self.y1)
	self.centeredit=QtGui.QLineEdit(self)
	self.centeredit.move(self.x2,self.y1)
	self.centeredit.setText(self.savedparmsdict['center'])
	self.centeredit.setToolTip('-1 - use average centering method (default),\n0 - if you do not want the average to be centered, \n1 - phase approximation of the center of gravity phase_cog, \n2 - cross-correlate with Gaussian function, \n3 - cross-correlate with donut shape image (e.g. inner radius=2, outer radius=7), \n4 - cross-correlate with reference image provided by user, \n5 - cross-correlate with self-rotated average..\ncentering may fail..use 0 to deactive it')
	
	self.y1 += 30
	
	ringstep= QtGui.QLabel('Ring step', self)
	ringstep.move(self.x1,self.y1)
	self.ringstepedit=QtGui.QLineEdit(self)
	self.ringstepedit.move(self.x2,self.y1)
	self.ringstepedit.setText(self.savedparmsdict['ringstep'])
	self.ringstepedit.setToolTip('step between rings in rotational correlation > 0 (set to 1)')
	
	self.y1 += 30
	
	innerradius= QtGui.QLabel('Inner radius', self)
	innerradius.move(self.x1,self.y1)
	self.innerradiusedit=QtGui.QLineEdit(self)
	self.innerradiusedit.move(self.x2,self.y1)
	self.innerradiusedit.setText(self.savedparmsdict['innerradius'])
	self.innerradiusedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	
	
	self.y1 += 30
	
	ctf= QtGui.QLabel('CTF', self)
	ctf.move(self.x1,self.y1)
	self.ctfchkbx = QtGui.QCheckBox("",self)
	self.ctfchkbx.move(self.x2, self.y1)
	self.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
	
	self.y1 += 30
	
	snr= QtGui.QLabel('SNR', self)
	snr.move(self.x1,self.y1)
	self.snredit=QtGui.QLineEdit(self)
	self.snredit.move(self.x2,self.y1)
	self.snredit.setText(self.savedparmsdict['snr'])
	self.snredit.setToolTip('signal-to-noise ratio of the data (default SNR=1.0)')	
	
	self.y1 += 30
		
	fourvar= QtGui.QLabel('Fourvar', self)
	fourvar.move(self.x1,self.y1)
	self.fourvarchkbx=QtGui.QCheckBox("",self)
	self.fourvarchkbx.move(self.x2,self.y1)
	self.fourvarchkbx.setCheckState(self.savedparmsdict['fourvar'])
	self.fourvarchkbx.setToolTip('use Fourier variance to weight the reference (recommended, default False)')
	
	self.y1 += 30
	
	gpnr= QtGui.QLabel('Number of Groups', self)
	gpnr.move(self.x1,self.y1)
	self.gpnredit=QtGui.QLineEdit(self)
	self.gpnredit.move(self.x2,self.y1)
	self.gpnredit.setText(self.savedparmsdict['gpnr'])
	self.gpnredit.setToolTip('number of groups in the new CTF filteration')	
	
	self.y1 += 30
	
	usrfunc= QtGui.QLabel('User Function Name', self)
	usrfunc.move(self.x1,self.y1)
	self.usrfuncedit=QtGui.QLineEdit(self)
	self.usrfuncedit.move(self.x2,self.y1)
	self.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
	self.usrfuncedit.setToolTip('name of the user-supplied-function that prepares reference image for each iteration')
	
	self.y1 += 30
		
	usrfuncfile= QtGui.QLabel('Enter name of external file containing user function:', self)
	usrfuncfile.move(self.x1,self.y1)
	
	self.y1 += 20
	
	usrfuncfile= QtGui.QLabel('(Leave blank if file is not external to Sparx)', self)
	usrfuncfile.move(self.x1,self.y1)
	
	self.y1 += 20
	
	self.usrfuncfileedit=QtGui.QLineEdit(self)
	self.usrfuncfileedit.move(self.x2,self.y1)
	self.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
	self.usrfuncfileedit.setToolTip('name of the external file containing user function')	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    	
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	self.usrfile_button = QtGui.QPushButton("Select File", self)
	self.usrfile_button.move(self.x3, self.y1-self.yspc)
	QtCore.QObject.connect(self.usrfile_button, QtCore.SIGNAL("clicked()"), self.choose_usrfile)
	
    def choose_usrfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing User Fuction", "", "py files (*.py)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.usrfuncfileedit.setText(str(a))
	
    def choose_mskfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing Mask", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.masknameedit.setText(str(a))
		


class Popupthreedali(QWidget):
    def __init__(self):
        QWidget.__init__(self)
	
	########################################################################################
	# class variables
	self.cmd = ""
	# populate with default values
	self.savedparmsdict = {'stackname':'NONE','refname':'NONE','foldername':'NONE','partradius':'-1','xyrange':'4 2 1 1','trans':'2 1 0.5 0.25', 'delta':'15 5 2','nriter':'3','nproc':'1','maskname':'','center':'-1',"ringstep":"1","innerradius":"1","ctf":Qt.Unchecked,"snr":"1.0","fourvar":Qt.Unchecked,"usrfunc":"ref_ali3d","usrfuncfile":"","an":'-1',"ref_a":'S',"sym":'c1',"npad":'4',"deltapsi":'-1',"startpsi":'-1',"stoprnct":'0.0',"debug":False,"nch":False,"chunk":'0.2',"rantest":False}
	
	########################################################################################
	# layout parameters
	
	self.y1 = 10
	self.y2 = self.y1 + 78
	self.y3 = self.y2 + 282
	self.y4 = self.y3 + 80
	self.y5 = self.y4 + 95
	self.yspc = 4
	
	self.x1 = 10
	self.x2 = self.x1 + 150
	self.x3 = self.x2+145
	self.x4 = self.x3+100
	self.x5 = 230
	########################################################################################
	
        #Here we just set the window title
	self.setWindowTitle('sxali3d')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxali3d</b> - 3D projection matching given reference structure and an image series', self)
	title1.move(self.x1,self.y1)
	self.y1 += 30

	self.repopbtn = QPushButton("Repopulate With Saved Parameters", self)
        self.repopbtn.move(self.x1-5,self.y1)
        #sets an infotip for this Pushbutton
        self.repopbtn.setToolTip('Repopulate With Saved Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.repopbtn, SIGNAL("clicked()"), self.repoparms_ali3d)
	
	########################################################################################
	
	stackname= QtGui.QLabel('Name of input stack', self)
	stackname.move(self.x1,self.y2)
        #Now add a line edit and define its position
	self.stacknameedit=QtGui.QLineEdit(self)
        self.stacknameedit.move(self.x2,self.y2)
        #Adds a default value for the line edit
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	
        #Here we create a Button(file_button with title run open .hdf) and its position in the window
	self.file_button = QtGui.QPushButton("Open .hdf", self)
	self.file_button.move(self.x3, self.y2-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button, QtCore.SIGNAL("clicked()"), self.choose_file)
        #exactly the same as above, but for subfunction choose_file1
	self.file_button1 = QtGui.QPushButton("Open .bdb", self)
	self.file_button1.move(self.x4,self.y2-self.yspc)
	QtCore.QObject.connect(self.file_button1, QtCore.SIGNAL("clicked()"), self.choose_file1)
	
	self.y2 += 30
		
	refname= QtGui.QLabel('Name of reference', self)
	refname.move(self.x1,self.y2)
        #Now add a line edit and define its position
	self.refnameedit=QtGui.QLineEdit(self)
        self.refnameedit.move(self.x2,self.y2)
        #Adds a default value for the line edit
	self.refnameedit.setText(self.savedparmsdict['refname'])
	#Here we create a Button(file_button with title run open .hdf) and its position in the window
	self.ref_button = QtGui.QPushButton("Open files", self)
	self.ref_button.move(self.x3, self.y2-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.ref_button, QtCore.SIGNAL("clicked()"), self.choose_reffile)

	
	self.y2 = self.y2+30
	
	#The same as above, but many line edits include Infotips
	foldername= QtGui.QLabel('Output folder', self)
	foldername.move(self.x1,self.y2)
	self.foldernameedit=QtGui.QLineEdit(self)
	self.foldernameedit.move(self.x2,self.y2)
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	
	self.outinfobtn = QPushButton("Output Info", self)
        self.outinfobtn.move(self.x3,  self.y2-self.yspc)
        #sets an infotip for this Pushbutton
        self.outinfobtn.setToolTip('Output Info')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.outinfobtn, SIGNAL("clicked()"), self.outputinfo_ali3d)
	
	self.y2 = self.y2+30
	
	partradius= QtGui.QLabel('Particle radius', self)
	partradius.move(self.x1,self.y2)
	self.partradiusedit=QtGui.QLineEdit(self)
	self.partradiusedit.move(self.x2,self.y2)
	self.partradiusedit.setText(self.savedparmsdict['partradius'])
	self.partradiusedit.setToolTip('Parameter ou: Outer radius for rotational correlation \nshould be set to particle radius\nif not sure, set to boxsize/2-2 ')	

	self.y2 = self.y2+30
	
	xyrange= QtGui.QLabel('xy range', self)
	xyrange.move(self.x1,self.y2)
	self.xyrangeedit=QtGui.QLineEdit(self)
	self.xyrangeedit.move(self.x2,self.y2)
	self.xyrangeedit.setText(self.savedparmsdict['xyrange'])
	self.xyrangeedit.setToolTip('Range for translational search in x, y direction\nif set to 0 only rotational alignment will be performed')

	self.y2 = self.y2+30
	
	trans= QtGui.QLabel('translational step', self)
	trans.move(self.x1,self.y2)
	self.transedit=QtGui.QLineEdit(self)
	self.transedit.move(self.x2,self.y2)
	self.transedit.setText(self.savedparmsdict['trans'])
	self.transedit.setToolTip('Step of translational search in x, y direction\nlarger values increase the speed but decrease the accuracy')	

	self.y2 = self.y2+30
	
	delta= QtGui.QLabel('angular step', self)
	delta.move(self.x1,self.y2)
	self.deltaedit=QtGui.QLineEdit(self)
	self.deltaedit.move(self.x2,self.y2)
	self.deltaedit.setText(self.savedparmsdict['delta'])
	self.deltaedit.setToolTip('angular step for the reference projections in respective iterations')		
	
	self.y2 =self.y2+30

	nriter= QtGui.QLabel('Number of Iterations', self)
	nriter.move(self.x1,self.y2)
	self.nriteredit=QtGui.QLineEdit(self)
	self.nriteredit.move(self.x2,self.y2)
	self.nriteredit.setText(self.savedparmsdict['nriter'])
	self.nriteredit.setToolTip('Maximum number of iterations the program will perform\n Using the default values the program will run 3 rounds with xy-range 4 and translational step 1, 3 rounds with xyrange 2 and translational step 1 and so on..\nif set to 0 maximum iteration number will be 10 and will automatically stop should the criterion falls')
	
	self.y2 =self.y2+30
	
	nproc= QtGui.QLabel('Number of Processors', self)
	nproc.move(self.x1,self.y2)
	self.nprocedit=QtGui.QLineEdit(self)
	self.nprocedit.move(self.x2,self.y2)
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	self.nprocedit.setToolTip('The number of processors to use. Default is single processor mode')
	
	########################################################################################
		
	header=QtGui.QLabel('Attributes xform.projection and active parameters must be set in the input stack', self)
	header.move(self.x1,self.y3)
	self.y3 = self.y3 + 30
	
	 #not linked to a function yet
        self.activeheader_button = QtGui.QPushButton("activate all images", self)
	self.activeheader_button.move(self.x1-5, self.y3)
	self.connect(self.activeheader_button, SIGNAL("clicked()"), self.setactiveheader)
	
	self.projheader_button = QtGui.QPushButton("set xform.projection", self)
	self.projheader_button.move(self.x1-5+180, self.y3)
	self.connect(self.projheader_button, SIGNAL("clicked()"), self.setprojheader)
	
	########################################################################################
	
	self.savepbtn = QPushButton("Save Input Parameters", self)
        self.savepbtn.move(self.x1-5,  self.y4)
        #sets an infotip for this Pushbutton
        self.savepbtn.setToolTip('Save Input Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.savepbtn, SIGNAL("clicked()"), self.saveparms)
	
	self.y4 = self.y4+30
	
	self.cmdlinebtn = QPushButton("Generate command line from input parameters", self)
        self.cmdlinebtn.move(self.x1-5,  self.y4)
        #sets an infotip for this Pushbutton
        self.cmdlinebtn.setToolTip('Generate command line using input parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.cmdlinebtn, SIGNAL("clicked()"), self.gencmdline_ali3d)
	
	########################################################################################
	
	 #Here we create a Button(Run_button with title run sxali2d) and its position in the window
	self.RUN_button = QtGui.QPushButton('Run sxali3d', self)
	# make 3D textured push button look
	s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
	
	self.RUN_button.setStyleSheet(s)
	
	self.RUN_button.move(self.x5,  self.y5)
        #Here we define, that when this button is clicked, it starts subfunction runsxali2d
        self.connect(self.RUN_button, SIGNAL("clicked()"), self.runsxali3d)
        #Labels and Line Edits for User Input

	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
   
    def outputinfo_ali3d(self):
    	QMessageBox.information(self, "ali3d output",'Output volumes and Fourier Shell Criterion curves are saved in Output folder. Projection parameters are saved in the attribute xform.projection in image headers. The images themselves are not changed.')
	
    def gencmdline_ali3d(self,writefile=True):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
   	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	ref = self.refnameedit.text()
	print "reference structure ="+ stack
	output=self.foldernameedit.text()
	print "output folder="+ output
	ou=self.partradiusedit.text()
	print "Particle radius="+ ou
	xr=self.xyrangeedit.text()
	print "xr=" +xr
	yr=self.xyrangeedit.text()
	print "yr=" +yr
	ts=self.transedit.text()
	print "ts=" +ts
	delta=self.deltaedit.text()
	print "delta=" +delta
	maxit=self.nriteredit.text()
	print "maxit="+maxit
	
	cmd1 = "sxali3d.py "+str(stack) +" "+ str(ref)+" "+ str(output)
	
	args = " --ou="+ str(ou)+ " --xr='"+str(xr)+"'"+ " --yr='"+str(yr)+"'"+ " --ts='"+str(ts)+"'"+ " --delta='"+str(delta)+"'"+" --maxit="+ str(maxit) 
	
	
	mask = self.w1.masknameedit.text()
	if len(str(mask))> 1:
		cmd1 = cmd1+" "+str(mask) 
	cmd1 = cmd1 + args
	
	
	ctr=self.w1.centeredit.text()
	ringstep = self.w1.ringstepedit.text()
	inrad = self.w1.innerradiusedit.text()
	CTF=self.w1.ctfchkbx.checkState()
	snr = self.w1.snredit.text()
	userf = self.w1.usrfuncedit.text()
	userfile = self.w1.usrfuncfileedit.text()
	an = self.w1.anedit.text()
	ref_a = self.w1.refaedit.text()
	sym = self.w1.symedit.text()
	npad = self.w1.npadedit.text()
		
	fourvar = self.w2.fourvarchkbx.checkState()
	rantest = self.w2.rantestchkbx.checkState()
	nch = self.w2.nchchkbx.checkState()
	debug = self.w2.debugchkbx.checkState()
	deltapsi = self.w2.deltapsiedit.text()
	startpsi = self.w2.startpsiedit.text()
	stoprnct = self.w2.stoprnctedit.text()
	chunk = self.w2.chunkedit.text()
		
	cmd1 = cmd1+" --center=" +str(ctr)+" --rs="+str(ringstep)+ " --ir=" + str(inrad)+ " --snr=" + str(snr)+ " --an='" + str(an)+ "'"+" --sym=" + str(sym)+ " --ref_a=" + str(ref_a)+ " --npad=" + str(npad)+ " --deltapsi='" + str(deltapsi)+"'"+ " --startpsi='" + str(startpsi)+ "'"+" --stoprnct=" + str(stoprnct)+ " --chunk=" + str(chunk)
	if CTF == Qt.Checked:
		cmd1 = cmd1 + " --CTF"
	if fourvar == Qt.Checked:
		cmd1 = cmd1 + " --Fourvar"	
	if nch == Qt.Checked:
		cmd1 = cmd1 + " --n"
	if rantest == Qt.Checked:
		cmd1 = cmd1 + " --rantest"
	if debug == Qt.Checked:
		cmd1 = cmd1 + " --debug"
				
	if len(userfile) < 1:
		cmd1 = cmd1 + " --function="+str(userf)
	else:
		userfile = str(userfile)
		# break it down into file name and directory path
		rind = userfile.rfind('/')
		
		if rind == -1:
			userfile = os.path.abspath(userfile)
			rind = userfile.rfind('/')
			
		fname = userfile[rind+1:]
		fname, ext = os.path.splitext(fname)
		fdir = userfile[0:rind]
		cmd1 = cmd1 + " --function=\"[" +fdir+","+fname+","+str(userf)+"]\""
		
	np = self.nprocedit.text()
	
	self.savedparmsdict = {'stackname':str(stack),'refname':str(ref),'foldername':str(output),'partradius':str(ou),'xyrange':str(xr),'trans':str(yr),'delta':str(delta),'nriter':str(maxit),'nproc':str(np),'maskname':str(mask),'center':str(ctr),"ringstep":str(ringstep),"innerradius":str(inrad),"ctf":CTF,"snr":str(snr),"fourvar":fourvar,"usrfunc":str(userf), "usrfuncfile":str(userfile),"an":str(an),"ref_a":str(ref_a),"sym":str(sym),"npad":str(npad),"deltapsi":str(deltapsi),"startpsi":str(startpsi),"stoprnct":str(stoprnct),"debug":debug,"nch":nch,"chunk":str(chunk),"rantest":rantest}

	self.w1.savedparmsdict=self.savedparmsdict
	self.w2.savedparmsdict=self.savedparmsdict
	
	if int(str(np)) > 1:
		cmd1="mpirun -np "+ str(np) + " "+ cmd1+" --MPI" 
	
	if writefile:	
		(fname,stat)= QInputDialog.getText(self,"Generate Command Line","Enter name of file to save command line in",QLineEdit.Normal,"")
		if stat:
			f = open(fname,'a')
			f.write(cmd1)
			f.write('\n')
			f.close()
	
	print cmd1
	self.cmd = cmd1
	
    def runsxali3d(self):
	self.gencmdline_ali3d(writefile=False)
	outfolder=self.savedparmsdict['foldername']
	if os.path.exists(outfolder):
		print "output folder "+outfolder+" already exists!"
		return
	process = subprocess.Popen(self.cmd,shell=True)
	self.emit(QtCore.SIGNAL("process_started"),process.pid)
	
    def saveparms(self):	
	(fname,stat)= QInputDialog.getText(self,"Save Input Parameters","Enter name of file to save parameters in",QLineEdit.Normal,"")
	if stat:
		import pickle
		output=open(fname,'wb')
		self.gencmdline_ali3d(writefile=False)
		pickle.dump(self.savedparmsdict,output)
		output.close()
	
    def repoparms_ali3d(self):	
	# repopulate with saved parms
	(fname,stat)= QInputDialog.getText(self,"Repopulate Parameters","Enter name of file parameters were saved in",QLineEdit.Normal,"")
	if stat:
		import pickle
		pkl = open(fname,'rb')
		self.savedparmsdict = pickle.load(pkl)
		print self.savedparmsdict
		self.partradiusedit.setText(self.savedparmsdict['partradius'])
		self.stacknameedit.setText(self.savedparmsdict['stackname'])
		self.refnameedit.setText(self.savedparmsdict['refname'])	
		self.foldernameedit.setText(self.savedparmsdict['foldername'])	
		self.xyrangeedit.setText(self.savedparmsdict['xyrange'])
		self.transedit.setText(self.savedparmsdict['trans'])
		self.deltaedit.setText(self.savedparmsdict['delta'])
		self.nriteredit.setText(self.savedparmsdict['nriter'])
		self.nprocedit.setText(self.savedparmsdict['nproc'])
	
		self.w1.masknameedit.setText(self.savedparmsdict['maskname'])
		self.w1.centeredit.setText(self.savedparmsdict['center'])
		self.w1.ringstepedit.setText(self.savedparmsdict['ringstep'])
		self.w1.innerradiusedit.setText(self.savedparmsdict['innerradius'])
		self.w1.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
		self.w1.snredit.setText(self.savedparmsdict['snr'])
		self.w1.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
		self.w1.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
		self.w1.anedit.setText(self.savedparmsdict['an'])
		self.w1.refaedit.setText(self.savedparmsdict['ref_a'])
		self.w1.symedit.setText(self.savedparmsdict['sym'])
		self.w1.npadedit.setText(self.savedparmsdict['npad'])
		
		self.w2.fourvarchkbx.setCheckState(self.savedparmsdict['fourvar'])
		self.w2.debugchkbx.setCheckState(self.savedparmsdict['debug'])
		self.w2.nchchkbx.setCheckState(self.savedparmsdict['nch'])
		self.w2.rantestchkbx.setCheckState(self.savedparmsdict['rantest'])
		self.w2.deltapsiedit.setText(self.savedparmsdict['deltapsi'])
		self.w2.startpsiedit.setText(self.savedparmsdict['startpsi'])
		self.w2.stoprnctedit.setText(self.savedparmsdict['stoprnct'])
		self.w2.chunkedit.setText(self.savedparmsdict['chunk'])
		
    def setactiveheader(self):
	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	header(str(stack), "active", one=True)

    def setprojheader(self):
	#opens a file browser, showing files only in .hdf format
	ok=False
	zerostr='set xform.projection to zero'
	randstr='randomize xform.projection'
	importstr='import parameters from file'
	(item,stat)= QInputDialog.getItem(self,"xform.projection","choose option",[zerostr,randstr,importstr])
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	#self.stacknameedit.setText(str(a))
   	choice= str(item)
	stack = self.stacknameedit.text()
	if stat:
		if choice == zerostr:
			header(str(stack),'xform.projection',zero=True)
		if choice == randstr:
			header(str(stack),'xform.projection',rand_alpha=True)
		if choice == importstr:
			file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "(*)")
			a=str(QtCore.QString(file_name))
			if len(a)>0:
				header(str(stack),'xform.projection',fimport=a)
	
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked
    def choose_file(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.stacknameedit.setText(str(a))
        
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked (same as above but for bdb files(maybe we can combine these two into one function)
    def choose_file1(self):
	file_name1 = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "EMAN2DB/", "BDB FILES (*.bdb)" )
	a=QtCore.QString(file_name1)
	b=os.path.basename(str(a))
	c=os.path.splitext(b)[0]
	d="bdb:"+c
	print d
	self.stacknameedit.setText(d)

    def choose_reffile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open reference structure file", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.refnameedit.setText(str(a))
        
class Popupadvparams_ali3d_1(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
	
	########################################################################################
	# layout parameters
	
	self.y1=10
	self.yspc = 4
	
	self.x1 = 10
	self.x2 = 140
	self.x3 = 285
	########################################################################################
	
        #Here we just set the window title
	#self.setWindowTitle('sxali3d advanced parameter selection')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxali3d</b> - set advanced parameters related to CTF and search', self)
	title1.move(self.x1,self.y1)
	
	self.y1 += 30
        #Labels and Line Edits for User Input
        #Just a label
	#title2= QtGui.QLabel('<b>Advanced</b> parameters', self)
	#title2.move(self.x1,self.y1)
	
	#self.y1 += 30
	
	self.savedparmsdict=savedparms
        #Example for User input stack name
        #First create the label and define its position
	maskname= QtGui.QLabel('Mask', self)
	maskname.move(self.x1,self.y1)
        #Now add a line edit and define its position
	self.masknameedit=QtGui.QLineEdit(self)
        self.masknameedit.move(self.x2,self.y1)
        #Adds a default value for the line edit
	self.masknameedit.setText(self.savedparmsdict['maskname'])
	self.masknameedit.setToolTip("Default is a circle mask with radius equal to the particle radius")
	
	self.mskfile_button = QtGui.QPushButton("Open Mask", self)
	self.mskfile_button.move(self.x3, self.y1-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.mskfile_button, QtCore.SIGNAL("clicked()"), self.choose_mskfile)
	
	self.y1 += 30
	
	center= QtGui.QLabel('Center type', self)
	center.move(self.x1,self.y1)
	self.centeredit=QtGui.QLineEdit(self)
	self.centeredit.move(self.x2,self.y1)
	self.centeredit.setText(self.savedparmsdict['center'])
	self.centeredit.setToolTip('-1 - use average centering method (default),\n0 - if you do not want the average to be centered, \n1 - phase approximation of the center of gravity phase_cog, \n2 - cross-correlate with Gaussian function, \n3 - cross-correlate with donut shape image (e.g. inner radius=2, outer radius=7), \n4 - cross-correlate with reference image provided by user, \n5 - cross-correlate with self-rotated average..\ncentering may fail..use 0 to deactive it')
	
	self.y1 += 30
	
	ringstep= QtGui.QLabel('Ring step', self)
	ringstep.move(self.x1,self.y1)
	self.ringstepedit=QtGui.QLineEdit(self)
	self.ringstepedit.move(self.x2,self.y1)
	self.ringstepedit.setText(self.savedparmsdict['ringstep'])
	self.ringstepedit.setToolTip('step between rings in rotational correlation > 0 (set to 1)')
	
	self.y1 += 30
	
	innerradius= QtGui.QLabel('Inner radius', self)
	innerradius.move(self.x1,self.y1)
	self.innerradiusedit=QtGui.QLineEdit(self)
	self.innerradiusedit.move(self.x2,self.y1)
	self.innerradiusedit.setText(self.savedparmsdict['innerradius'])
	self.innerradiusedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	
	
	self.y1 += 30
	
	ctf= QtGui.QLabel('CTF', self)
	ctf.move(self.x1,self.y1)
	self.ctfchkbx = QtGui.QCheckBox("",self)
	self.ctfchkbx.move(self.x2, self.y1)
	self.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
	self.ctfchkbx.setToolTip('if this flag is set, the program will use CTF information provided in file headers')
	
	self.y1 += 30
	
	snr= QtGui.QLabel('SNR', self)
	snr.move(self.x1,self.y1)
	self.snredit=QtGui.QLineEdit(self)
	self.snredit.move(self.x2,self.y1)
	self.snredit.setText(self.savedparmsdict['snr'])
	self.snredit.setToolTip('signal-to-noise ratio of the data (default SNR=1.0)')	
	
	self.y1 += 30
	
	refa= QtGui.QLabel('ref_a', self)
	refa.move(self.x1,self.y1)
        #Now add a line edit and define its position
	self.refaedit=QtGui.QLineEdit(self)
        self.refaedit.move(self.x2,self.y1)
        #Adds a default value for the line edit
	self.refaedit.setText(self.savedparmsdict['ref_a'])
	self.refaedit.setToolTip("Default is a circle mask with radius equal to the particle radius")
	
	self.y1 += 30
	
	sym= QtGui.QLabel('Symmetry', self)
	sym.move(self.x1,self.y1)
	self.symedit=QtGui.QLineEdit(self)
	self.symedit.move(self.x2,self.y1)
	self.symedit.setText(self.savedparmsdict['sym'])
	self.symedit.setToolTip('-1 - use average centering method (default),\n0 - if you do not want the average to be centered, \n1 - phase approximation of the center of gravity phase_cog, \n2 - cross-correlate with Gaussian function, \n3 - cross-correlate with donut shape image (e.g. inner radius=2, outer radius=7), \n4 - cross-correlate with reference image provided by user, \n5 - cross-correlate with self-rotated average..\ncentering may fail..use 0 to deactive it')
	
	self.y1 += 30
	
	pad= QtGui.QLabel('npad', self)
	pad.move(self.x1,self.y1)
	self.npadedit=QtGui.QLineEdit(self)
	self.npadedit.move(self.x2,self.y1)
	self.npadedit.setText(self.savedparmsdict['npad'])
	self.npadedit.setToolTip('step between rings in rotational correlation > 0 (set to 1)')
	
	self.y1 += 30
	
	an= QtGui.QLabel('an', self)
	an.move(self.x1,self.y1)
	self.anedit=QtGui.QLineEdit(self)
	self.anedit.move(self.x2,self.y1)
	self.anedit.setText(self.savedparmsdict['an'])
	self.anedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	

	self.y1 += 30
	
	usrfunc= QtGui.QLabel('User Function Name', self)
	usrfunc.move(self.x1,self.y1)
	self.usrfuncedit=QtGui.QLineEdit(self)
	self.usrfuncedit.move(self.x2,self.y1)
	self.usrfuncedit.setText(self.savedparmsdict['usrfunc'])
	self.usrfuncedit.setToolTip('name of the user-supplied-function that prepares reference image for each iteration')
	
	self.y1 += 30
		
	usrfuncfile= QtGui.QLabel('Enter name of external file containing user function:', self)
	usrfuncfile.move(self.x1,self.y1)
	
	self.y1 += 20
	
	usrfuncfile= QtGui.QLabel('(Leave blank if file is not external to Sparx)', self)
	usrfuncfile.move(self.x1,self.y1)
	
	self.y1 += 20
	
	self.usrfuncfileedit=QtGui.QLineEdit(self)
	self.usrfuncfileedit.move(self.x2,self.y1)
	self.usrfuncfileedit.setText(self.savedparmsdict['usrfuncfile'])
	self.usrfuncfileedit.setToolTip('name of the external file containing user function')	
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    	
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	self.usrfile_button = QtGui.QPushButton("Select File", self)
	self.usrfile_button.move(self.x3, self.y1-self.yspc)
	QtCore.QObject.connect(self.usrfile_button, QtCore.SIGNAL("clicked()"), self.choose_usrfile)
	
    def choose_usrfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing User Fuction", "", "py files (*.py)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.usrfuncfileedit.setText(str(a))
	
    def choose_mskfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing Mask", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.masknameedit.setText(str(a))

class Popupadvparams_ali3d_2(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
	
	########################################################################################
	# layout parameters
	
	self.y1=10
	self.yspc = 4
	
	self.x1 = 10
	self.x2 = 140
	self.x3 = 285
	########################################################################################
	
        #Here we just set the window title
	#self.setWindowTitle('sxali3d advanced parameter selection 2')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxali3d</b> - set remaining advanced parameters', self)
	title1.move(self.x1,self.y1)
	
	self.y1 += 30
	
	self.savedparmsdict=savedparms
       	
	fourvar= QtGui.QLabel('Fourvar', self)
	fourvar.move(self.x1,self.y1)
	self.fourvarchkbx=QtGui.QCheckBox("",self)
	self.fourvarchkbx.move(self.x2,self.y1)
	self.fourvarchkbx.setCheckState(self.savedparmsdict['fourvar'])
	self.fourvarchkbx.setToolTip('use Fourier variance to weight the reference (recommended, default False)')
	
	self.y1 += 30
	
	deltapsi= QtGui.QLabel('deltapsi', self)
	deltapsi.move(self.x1,self.y1)
	self.deltapsiedit=QtGui.QLineEdit(self)
	self.deltapsiedit.move(self.x2,self.y1)
	self.deltapsiedit.setText(self.savedparmsdict['deltapsi'])
	self.deltapsiedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	

	self.y1 += 30
	
	startpsi= QtGui.QLabel('startpsi', self)
	startpsi.move(self.x1,self.y1)
	self.startpsiedit=QtGui.QLineEdit(self)
	self.startpsiedit.move(self.x2,self.y1)
	self.startpsiedit.setText(self.savedparmsdict['startpsi'])
	self.startpsiedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	

	self.y1 += 30
	
	stoprnct= QtGui.QLabel('stoprnct', self)
	stoprnct.move(self.x1,self.y1)
	self.stoprnctedit=QtGui.QLineEdit(self)
	self.stoprnctedit.move(self.x2,self.y1)
	self.stoprnctedit.setText(self.savedparmsdict['stoprnct'])
	self.stoprnctedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	

	self.y1 += 30
	
	nch= QtGui.QLabel('n', self)
	nch.move(self.x1,self.y1)
	self.nchchkbx=QtGui.QCheckBox("",self)
	self.nchchkbx.move(self.x2,self.y1)
	self.nchchkbx.setCheckState(self.savedparmsdict['nch'])
	self.nchchkbx.setToolTip('use Fourier variance to weight the reference (recommended, default False)')
	
	self.y1 += 30
	
	chunk= QtGui.QLabel('chunk', self)
	chunk.move(self.x1,self.y1)
	self.chunkedit=QtGui.QLineEdit(self)
	self.chunkedit.move(self.x2,self.y1)
	self.chunkedit.setText(self.savedparmsdict['chunk'])
	self.chunkedit.setToolTip('inner radius for rotational correlation > 0 (set to 1) ')	

	self.y1 += 30
	
	dbg= QtGui.QLabel('debug', self)
	dbg.move(self.x1,self.y1)
	self.debugchkbx=QtGui.QCheckBox("",self)
	self.debugchkbx.move(self.x2,self.y1)
	self.debugchkbx.setCheckState(self.savedparmsdict['debug'])
	self.debugchkbx.setToolTip('use Fourier variance to weight the reference (recommended, default False)')
	
	self.y1 += 30
	
	rant= QtGui.QLabel('rantest', self)
	rant.move(self.x1,self.y1)
	self.rantestchkbx=QtGui.QCheckBox("",self)
	self.rantestchkbx.move(self.x2,self.y1)
	self.rantestchkbx.setCheckState(self.savedparmsdict['rantest'])
	self.rantestchkbx.setToolTip('use Fourier variance to weight the reference (recommended, default False)')
	
	self.y1 += 30
	
    
#################
## kmeans

#Layout of the Pop Up window Popuptwodali (for sxali2d); started by the function twodali of the main window        
class Popupkmeans(QWidget):
    def __init__(self):
        QWidget.__init__(self)
	
	#######################################################################################
	# class variables
	self.cmd = ""
	# populate with default values
	self.savedparmsdict = {'stackname':'NONE','foldername':'NONE','kc':'2','trials':'1','maxiter':'100','nproc':'1','randsd':'-1','maskname':'',"ctf":Qt.Unchecked,"crit":"all","normalize":Qt.Unchecked, "init_method":"rnd"}

	#######################################################################################
	# Layout parameters
	
	self.y1 = 10 # title and Repopulate button
	self.y2 = self.y1 + 78 # Text boxes for inputting parameters
	self.y3 = self.y2 + 222 # activate images button and set xform.align2d button
	self.y4 = self.y3 + 80 # Advanced Parameters, Save Input and Generate command line buttons
	self.y5 = self.y4 + 95 # run button 
	self.yspc = 4
	
	self.x1 = 10 # first column (text box labels)
	self.x2 = self.x1 + 200 # second column (text boxes)
	self.x3 = self.x2+145 # third column (Open .hdf button)
	self.x4 = self.x3+100 # fourth column (Open .bdb button)
	self.x5 = 230 # run button
	#######################################################################################
	
        #Here we just set the window title
	self.setWindowTitle('sxk_means')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxk_means</b> - K-means classification of a set of images', self)
	title1.move(self.x1,self.y1)
	self.y1 += 30

	self.repopbtn = QPushButton("Repopulate With Saved Parameters", self)
        self.repopbtn.move(self.x1-5,self.y1)
        #sets an infotip for this Pushbutton
        self.repopbtn.setToolTip('Repopulate With Saved Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.repopbtn, SIGNAL("clicked()"), self.repoparms_kmeans)

	#######################################################################################
        #Here we create a Button(file_button with title run open .hdf) and its position in the window
	self.file_button = QtGui.QPushButton("Open .hdf", self)
	self.file_button.move(self.x3, self.y2-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button, QtCore.SIGNAL("clicked()"), self.choose_file)
        #exactly the same as above, but for subfunction choose_file1
	self.file_button1 = QtGui.QPushButton("Open .bdb", self)
	self.file_button1.move(self.x4,self.y2-self.yspc)
	QtCore.QObject.connect(self.file_button1, QtCore.SIGNAL("clicked()"), self.choose_file1)
	
	stackname= QtGui.QLabel('Name of input stack', self)
	stackname.move(self.x1,self.y2)
	self.stacknameedit=QtGui.QLineEdit(self)
        self.stacknameedit.move(self.x2,self.y2)
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	self.y2 += 30
	
	foldername= QtGui.QLabel('Output folder', self)
	foldername.move(self.x1,self.y2)
	self.foldernameedit=QtGui.QLineEdit(self)
	self.foldernameedit.move(self.x2,self.y2)
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	
	self.outinfobtn = QPushButton("Output Info", self)
        self.outinfobtn.move(self.x3,  self.y2-self.yspc)
        #sets an infotip for this Pushbutton
        self.outinfobtn.setToolTip('Output Info')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.outinfobtn, SIGNAL("clicked()"), self.outputinfo_kmeans)
	self.y2 += 30
	
	kc= QtGui.QLabel('Number of clusters', self)
	kc.move(self.x1,self.y2)
	self.kcedit=QtGui.QLineEdit(self)
	self.kcedit.move(self.x2,self.y2)
	self.kcedit.setText(self.savedparmsdict['kc'])
	self.kcedit.setToolTip('The requested number of clusters')	
	self.y2 += 30

	trials= QtGui.QLabel('Number of trials', self)
	trials.move(self.x1,self.y2)
	self.trialsedit=QtGui.QLineEdit(self)
	self.trialsedit.move(self.x2,self.y2)
	self.trialsedit.setText(self.savedparmsdict['trials'])
	self.trialsedit.setToolTip('number of trials of K-means (see description below) (default one trial). MPI version ignore --trials, the number of trials in MPI version will be the number of cpu used.')
	self.y2 += 30
	
	maxiter= QtGui.QLabel('Maxinum Number of Iterations', self)
	maxiter.move(self.x1,self.y2)
	self.maxiteredit=QtGui.QLineEdit(self)
	self.maxiteredit.move(self.x2,self.y2)
	self.maxiteredit.setText(self.savedparmsdict['maxiter'])
	self.maxiteredit.setToolTip('maximum number of iterations the program will perform (default 100)')
	self.y2 += 30
	
	# make ctf, normalize and init_method radio button...
	
	nproc= QtGui.QLabel('Number of Processors', self)
	nproc.move(self.x1,self.y2)
	self.nprocedit=QtGui.QLineEdit(self)
	self.nprocedit.move(self.x2,self.y2)
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	self.nprocedit.setToolTip('The number of processors to use. Default is single processor mode')

	##########################################################
	
	header=QtGui.QLabel('The clustering is performed only using images from the stack that has flag active set to one', self)
	header.move(self.x1,self.y3)
	self.y3 += 30
	
        #not linked to a function yet
        self.activeheader_button = QtGui.QPushButton("activate all images", self)
	self.activeheader_button.move(self.x1-5, self.y3)
	self.connect(self.activeheader_button, SIGNAL("clicked()"), self.setactiveheader)
	
	######################################################################################
	
	self.savepbtn = QPushButton("Save Input Parameters", self)
        self.savepbtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.savepbtn.setToolTip('Save Input Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.savepbtn, SIGNAL("clicked()"), self.saveparms)
	self.y4+=30
	
	self.cmdlinebtn = QPushButton("Generate command line from input parameters", self)
        self.cmdlinebtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.cmdlinebtn.setToolTip('Generate command line using input parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.cmdlinebtn, SIGNAL("clicked()"), self.gencmdline_kmeans)

	#######################################################################
	 #Here we create a Button(Run_button with title run sxali2d) and its position in the window
	self.RUN_button = QtGui.QPushButton('Run sxk_means', self)
	# make 3D textured push button look
	s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
	
	self.RUN_button.setStyleSheet(s)
	self.RUN_button.move(self.x5, self.y5)
        #Here we define, that when this button is clicked, it starts subfunction runsxali2d
        self.connect(self.RUN_button, SIGNAL("clicked()"), self.runsxk_means)
        #Labels and Line Edits for User Input	

     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    def outputinfo_kmeans(self):
    	QMessageBox.information(self, "kmeans output",'The directory to which the averages of K clusters, and the variance. The classification charts are written to the logfile. Warning: If the output directory already exists, the program will crash and an error message will come up. Please change the name of directory and restart the program.')
	
    def gencmdline_kmeans(self,writefile=True):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
   	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	output=self.foldernameedit.text()
	print "output folder="+ output
	kc=self.kcedit.text()
	print "Number of requested clusters="+ kc
	trials=self.trialsedit.text()
	print "Number of trials="+ trials
	maxiter=self.maxiteredit.text()
	print "maximum number of iterations=" +maxiter
	
	cmd1 = "sxk_means.py "+str(stack) +" "+ str(output)
	
	args = " --K="+ str(kc)+ " --trials="+str(trials)+ " --maxit="+str(maxiter)
	
	
	mask = self.w1.masknameedit.text()
		
	if len(str(mask))> 1:
		cmd1 = cmd1+" "+str(mask) 
			
	cmd1 = cmd1 + args
	
	randsd=self.w1.randsdedit.text()
	ctf=self.w1.ctfchkbx.checkState()
	normalize=self.w1.normachkbx.checkState()
	init_method=self.w1.init_methodedit.text()
	crit=self.w1.critedit.text()
		
	cmd1 = cmd1+" --rand_seed=" +str(randsd)+" --init_method="+str(init_method)+" --crit="+str(crit)
		
	if ctf == Qt.Checked:
		cmd1 = cmd1 + " --CTF"
	if normalize == Qt.Checked:
		cmd1 = cmd1 + " --normalize"
			
	np = self.nprocedit.text()
	
	self.savedparmsdict = {'stackname':str(stack),'foldername':str(output),'kc':str(kc),'trials':str(trials),'maxiter':str(maxiter),'nproc':str(np),'randsd':str(randsd),'maskname':str(mask),"ctf":ctf,"crit":str(crit),"normalize":normalize, "init_method":str(init_method)}

	self.w1.savedparmsdict=self.savedparmsdict
	
	if int(str(np)) > 1:
		cmd1="mpirun -np "+ str(np) + " "+ cmd1+" --MPI" 
	
	if writefile:	
		(fname,stat)= QInputDialog.getText(self,"Generate Command Line","Enter name of file to save command line in",QLineEdit.Normal,"")
		if stat:
			f = open(fname,'a')
			f.write(cmd1)
			f.write('\n')
			f.close()
	
	print cmd1
	self.cmd = cmd1
	
    def runsxk_means(self):
	self.gencmdline_kmeans(writefile=False)
	outfolder=self.savedparmsdict['foldername']
	if os.path.exists(outfolder):
		print "output folder "+outfolder+" already exists!"
		return
	process = subprocess.Popen(self.cmd,shell=True)
	self.emit(QtCore.SIGNAL("process_started"),process.pid)
	
    def saveparms(self):	
	(fname,stat)= QInputDialog.getText(self,"Save Input Parameters","Enter name of file to save parameters in",QLineEdit.Normal,"")
	if stat:
		import pickle
		output=open(fname,'wb')
		self.gencmdline_kmeans(writefile=False)
		pickle.dump(self.savedparmsdict,output)
		output.close()
	
    def repoparms_kmeans(self):	
	(fname,stat)= QInputDialog.getText(self,"Repopulate Parameters","Enter name of file parameters were saved in",QLineEdit.Normal,"")
	if stat:
		import pickle
		pkl = open(fname,'rb')
		self.savedparmsdict = pickle.load(pkl)
		self.kcedit.setText(self.savedparmsdict['kc'])
		self.stacknameedit.setText(self.savedparmsdict['stackname'])	
		self.foldernameedit.setText(self.savedparmsdict['foldername'])	
		self.trialsedit.setText(self.savedparmsdict['trials'])
		self.maxiteredit.setText(self.savedparmsdict['maxiter'])
		self.nprocedit.setText(self.savedparmsdict['nproc'])
		self.w1.masknameedit.setText(self.savedparmsdict['maskname'])
		self.w1.randsdedit.setText(self.savedparmsdict['randsd'])
		self.w1.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
		self.w1.normachkbx.setCheckState(self.savedparmsdict['normalize'])
		self.w1.critedit.setText(self.savedparmsdict['crit'])
		self.w1.init_methodedit.setText(self.savedparmsdict['init_method'])
		
    def setactiveheader(self):
	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	header(str(stack), "active", one=True)

   
    def choose_file(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.stacknameedit.setText(str(a))
        
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked (same as above but for bdb files(maybe we can combine these two into one function)
    def choose_file1(self):
	file_name1 = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "EMAN2DB/", "BDB FILES (*.bdb)" )
	a=QtCore.QString(file_name1)
	b=os.path.basename(str(a))
	c=os.path.splitext(b)[0]
	d="bdb:"+c
	print d
	self.stacknameedit.setText(d)
	
class Popupadvparams_kmeans(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
	
	self.x1 = 10
	self.x2 = 140
	self.x3 = 285
	
	self.y1 = 10
	self.yspc = 4
	
        #Here we just set the window title
	self.setWindowTitle('sxk_means advanced parameter selection')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxk_means</b> - set advanced params', self)
	title1.move(self.x1,self.y1)
        #Labels and Line Edits for User Input
        #Just a label
	self.y1 += 30
	
	title2= QtGui.QLabel('<b>Advanced</b> parameters', self)
	title2.move(self.x1,self.y1)
	
	self.y1 += 30
	
	self.savedparmsdict=savedparms
        #Example for User input stack name
        #First create the label and define its position
	maskname= QtGui.QLabel('Mask', self)
	maskname.move(self.x1,self.y1)
        #Now add a line edit and define its position
	self.masknameedit=QtGui.QLineEdit(self)
        self.masknameedit.move(self.x2,self.y1)
        #Adds a default value for the line edit
	self.masknameedit.setText(self.savedparmsdict['maskname'])
	
	self.mskfile_button = QtGui.QPushButton("Open .hdf", self)
	self.mskfile_button.move(self.x3, self.y1-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.mskfile_button, QtCore.SIGNAL("clicked()"), self.choose_mskfile)
	
	self.y1 += 30
	
	randsd= QtGui.QLabel('Random Seed', self)
	randsd.move(self.x1,self.y1)
	self.randsdedit=QtGui.QLineEdit(self)
	self.randsdedit.move(self.x2,self.y1)
	self.randsdedit.setText(self.savedparmsdict['randsd'])
	self.randsdedit.setToolTip('the seed used to generating random numbers (set to -1, means different and pseudo-random each time)')
	
	self.y1 += 30
	
	ctf= QtGui.QLabel('CTF', self)
	ctf.move(self.x1,self.y1)
	self.ctfchkbx = QtGui.QCheckBox("",self)
	self.ctfchkbx.move(self.x2, self.y1)
	self.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
	
	self.y1 += 30
	
	norma= QtGui.QLabel('normalize', self)
	norma.move(self.x1,self.y1)
	self.normachkbx = QtGui.QCheckBox("",self)
	self.normachkbx.move(self.x2, self.y1)
	self.normachkbx.setCheckState(self.savedparmsdict['normalize'])
	self.y1 += 30
	
	crit= QtGui.QLabel('Criterion', self)
	crit.move(self.x1,self.y1)
	self.critedit=QtGui.QLineEdit(self)
	self.critedit.move(self.x2,self.y1)
	self.critedit.setText(self.savedparmsdict['crit'])
	self.critedit.setToolTip('names of criterion used: \'all\' all criterions, \'C\' Coleman, \'H\' Harabasz or \'D\' Davies-Bouldin, thoses criterions return the values of classification quality, see also sxk_means_groups. Any combination is accepted, i.e., \'CD\', \'HC\', \'CHD\'.')
	
	self.y1 += 30
	
	initmethod= QtGui.QLabel('Criterion', self)
	initmethod.move(self.x1,self.y1)
	self.init_methodedit=QtGui.QLineEdit(self)
	self.init_methodedit.move(self.x2,self.y1)
	self.init_methodedit.setText(self.savedparmsdict['init_method'])
	self.init_methodedit.setToolTip('Method used to initialize partition: "rnd" randomize or "d2w" for d2 weighting initialization (default is rnd)')
	
	
    def choose_mskfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing Mask", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.masknameedit.setText(str(a))

        
class Popupkmeansgroups(QWidget):
    def __init__(self):
        QWidget.__init__(self)
	
	#######################################################################################
	# class variables
	self.cmd = ""
	# populate with default values
	self.savedparmsdict = {'stackname':'NONE','foldername':'NONE','kc1':'2','kc2':'3','trials':'1','nproc':'1','randsd':'-1','maskname':'',"ctf":Qt.Unchecked,'maxiter':'100'}
	
	#######################################################################################
	# Layout parameters
	
	self.y1 = 10 # title and Repopulate button
	self.y2 = self.y1 + 78 # Text boxes for inputting parameters
	self.y3 = self.y2 + 222 # activate images button and set xform.align2d button
	self.y4 = self.y3 + 80 # Advanced Parameters, Save Input and Generate command line buttons
	self.y5 = self.y4 + 95 # run button 
	self.yspc = 4
	
	self.x1 = 10 # first column (text box labels)
	self.x2 = self.x1 + 200 # second column (text boxes)
	self.x3 = self.x2+145 # third column (Open .hdf button)
	self.x4 = self.x3+100 # fourth column (Open .bdb button)
	self.x5 = 230 # run button
	#######################################################################################
	
        #Here we just set the window title
	self.setWindowTitle('sxk_means_groups')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxk_means_groups</b> - K-means groups classification of a set of images', self)
	title1.move(self.x1,self.y1)
	self.y1 += 30

	self.repopbtn = QPushButton("Repopulate With Saved Parameters", self)
        self.repopbtn.move(self.x1-5,self.y1)
        #sets an infotip for this Pushbutton
        self.repopbtn.setToolTip('Repopulate With Saved Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.repopbtn, SIGNAL("clicked()"), self.repoparms_kmeans_groups)

	#######################################################################################
        #Here we create a Button(file_button with title run open .hdf) and its position in the window
	self.file_button = QtGui.QPushButton("Open .hdf", self)
	self.file_button.move(self.x3, self.y2-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.file_button, QtCore.SIGNAL("clicked()"), self.choose_file)
        #exactly the same as above, but for subfunction choose_file1
	self.file_button1 = QtGui.QPushButton("Open .bdb", self)
	self.file_button1.move(self.x4,self.y2-self.yspc)
	QtCore.QObject.connect(self.file_button1, QtCore.SIGNAL("clicked()"), self.choose_file1)
	
	stackname= QtGui.QLabel('Name of input stack', self)
	stackname.move(self.x1,self.y2)
	self.stacknameedit=QtGui.QLineEdit(self)
        self.stacknameedit.move(self.x2,self.y2)
	self.stacknameedit.setText(self.savedparmsdict['stackname'])
	self.y2 += 30
	
	foldername= QtGui.QLabel('Output folder', self)
	foldername.move(self.x1,self.y2)
	self.foldernameedit=QtGui.QLineEdit(self)
	self.foldernameedit.move(self.x2,self.y2)
	self.foldernameedit.setText(self.savedparmsdict['foldername'])	
	
	self.outinfobtn = QPushButton("Output Info", self)
        self.outinfobtn.move(self.x3,  self.y2-self.yspc)
        #sets an infotip for this Pushbutton
        self.outinfobtn.setToolTip('Output Info')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.outinfobtn, SIGNAL("clicked()"), self.outputinfo_kmeans_groups)
	self.y2 += 30
	
	kc1= QtGui.QLabel('Minimum number of clusters', self)
	kc1.move(self.x1,self.y2)
	self.kc1edit=QtGui.QLineEdit(self)
	self.kc1edit.move(self.x2,self.y2)
	self.kc1edit.setText(self.savedparmsdict['kc1'])
	self.kc1edit.setToolTip('Minimum requested number of clusters')	
	self.y2 += 30
	
	kc2= QtGui.QLabel('Maximum number of clusters', self)
	kc2.move(self.x1,self.y2)
	self.kc2edit=QtGui.QLineEdit(self)
	self.kc2edit.move(self.x2,self.y2)
	self.kc2edit.setText(self.savedparmsdict['kc2'])
	self.kc2edit.setToolTip('The requested number of clusters')	
	self.y2 += 30

	trials= QtGui.QLabel('Number of trials', self)
	trials.move(self.x1,self.y2)
	self.trialsedit=QtGui.QLineEdit(self)
	self.trialsedit.move(self.x2,self.y2)
	self.trialsedit.setText(self.savedparmsdict['trials'])
	self.trialsedit.setToolTip('number of trials of K-means (see description below) (default one trial). MPI version ignore --trials, the number of trials in MPI version will be the number of cpu used.')
	self.y2 += 30
	
	maxiter= QtGui.QLabel('Maxinum Number of Iterations', self)
	maxiter.move(self.x1,self.y2)
	self.maxiteredit=QtGui.QLineEdit(self)
	self.maxiteredit.move(self.x2,self.y2)
	self.maxiteredit.setText(self.savedparmsdict['maxiter'])
	self.maxiteredit.setToolTip('maximum number of iterations the program will perform (default 100)')
	self.y2 += 30
	# make ctf, normalize and init_method radio button...
	
	nproc= QtGui.QLabel('Number of Processors', self)
	nproc.move(self.x1,self.y2)
	self.nprocedit=QtGui.QLineEdit(self)
	self.nprocedit.move(self.x2,self.y2)
	self.nprocedit.setText(self.savedparmsdict['nproc'])
	self.nprocedit.setToolTip('The number of processors to use. Default is single processor mode')

	##########################################################
	
	header=QtGui.QLabel('The clustering is performed only using images from the stack that has flag active set to one', self)
	header.move(self.x1,self.y3)
	self.y3 += 30
	
        #not linked to a function yet
        self.activeheader_button = QtGui.QPushButton("activate all images", self)
	self.activeheader_button.move(self.x1-5, self.y3)
	self.connect(self.activeheader_button, SIGNAL("clicked()"), self.setactiveheader)
	
	######################################################################################
	
	self.savepbtn = QPushButton("Save Input Parameters", self)
        self.savepbtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.savepbtn.setToolTip('Save Input Parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.savepbtn, SIGNAL("clicked()"), self.saveparms)
	self.y4+=30
	
	self.cmdlinebtn = QPushButton("Generate command line from input parameters", self)
        self.cmdlinebtn.move(self.x1-5, self.y4)
        #sets an infotip for this Pushbutton
        self.cmdlinebtn.setToolTip('Generate command line using input parameters')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.cmdlinebtn, SIGNAL("clicked()"), self.gencmdline_kmeans_groups)

	#######################################################################
	 #Here we create a Button(Run_button with title run sxali2d) and its position in the window
	self.RUN_button = QtGui.QPushButton('Run sxk_means', self)
	# make 3D textured push button look
	s = "QPushButton {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #8D0);min-width:90px;margin:5px} QPushButton:pressed {font: bold; color: #000;border: 1px solid #333;border-radius: 11px;padding: 2px;background: qradialgradient(cx: 0, cy: 0,fx: 0.5, fy:0.5,radius: 1, stop: 0 #fff, stop: 1 #084);min-width:90px;margin:5px}"
	
	self.RUN_button.setStyleSheet(s)
	self.RUN_button.move(self.x5, self.y5)
        #Here we define, that when this button is clicked, it starts subfunction runsxali2d
        self.connect(self.RUN_button, SIGNAL("clicked()"), self.runsxk_means_groups)
        #Labels and Line Edits for User Input	

		
     #Function runsxali2d started when  the  RUN_button of the  Poptwodali window is clicked 
    def outputinfo_kmeans_groups(self):
    	QMessageBox.information(self, "k_means_groups output",'Output directory will contain two text files: output_file and output_file.p, where output_file is the name of the output folder. \n\n output_file will contain columns according the criteria chosen, for example if crit=\'CHD\', the columns of numbers: (1) number of clusters, (2) values of Coleman criterion, (3) values of Harabasz criterion and (4) values of Davies-Bouldin criterion \n\n output_file.p will contain a gnuplot script, this file allow plot directly the values of all criteria with the same range. Use this command in gnuplot: load \'output_file.p\'\n\n WATCH_GRP_KMEANS or WATCH_MPI_GRP_KMEANS contain the progress of k-means groups. This file can be read in real-time to watch the evolution of criteria')
	
    def gencmdline_kmeans_groups(self,writefile=True):
	#Here we just read in all user inputs in the line edits of the Poptwodali window
   	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	output=self.foldernameedit.text()
	print "output folder="+ output
	kc1=self.kc1edit.text()
	print "Minimum number of requested clusters="+ kc1
	kc2=self.kc2edit.text()
	print "Maximum number of requested clusters="+ kc2
	trials=self.trialsedit.text()
	print "Number of trials="+ trials
	maxiter=self.maxiteredit.text()
	print "maxiter="+ maxiter
	
	cmd1 = "sxk_means_groups.py "+str(stack) +" "+ str(output)
	
	args = " --K1="+ str(kc1)+" --K2="+ str(kc2)+ " --trials="+str(trials)+ " --maxit="+str(maxiter)
	
	mask = self.w1.masknameedit.text()
		
	if len(str(mask))> 1:
		cmd1 = cmd1+" "+str(mask) 
			
	cmd1 = cmd1 + args
		
	randsd=self.w1.randsdedit.text()
	ctf=self.w1.ctfchkbx.checkState()
		
	cmd1 = cmd1+" --rand_seed=" +str(randsd)
		
	if ctf == Qt.Checked:
		cmd1 = cmd1 + " --CTF"
			
	np = self.nprocedit.text()
	
	self.savedparmsdict = {'stackname':str(stack),'foldername':str(output),'kc1':str(kc1),'kc2':str(kc2),'trials':str(trials),'nproc':str(np),'randsd':str(randsd),'maskname':str(mask),"ctf":ctf,'maxiter':str(maxiter)}

	self.w1.savedparmsdict=self.savedparmsdict
	
	if int(str(np)) > 1:
		cmd1="mpirun -np "+ str(np) + " "+ cmd1+" --MPI" 
	
	if writefile:	
		(fname,stat)= QInputDialog.getText(self,"Generate Command Line","Enter name of file to save command line in",QLineEdit.Normal,"")
		if stat:
			f = open(fname,'a')
			f.write(cmd1)
			f.write('\n')
			f.close()
	
	print cmd1
	self.cmd = cmd1
	
    def runsxk_means_groups(self):
	self.gencmdline_kmeans_groups(writefile=False)
	outfolder=self.savedparmsdict['foldername']
	if os.path.exists(outfolder):
		print "output folder "+outfolder+" already exists!"
		return
	process = subprocess.Popen(self.cmd,shell=True)
	self.emit(QtCore.SIGNAL("process_started"),process.pid)
	
    def saveparms(self):	
	# save all the parms in a text file so we can repopulate if user requests
	(fname,stat)= QInputDialog.getText(self,"Save Input Parameters","Enter name of file to save parameters in",QLineEdit.Normal,"")
	if stat:
		import pickle
		output=open(fname,'wb')
		self.gencmdline_kmeans_groups(writefile=False)
		pickle.dump(self.savedparmsdict,output)
		output.close()
	
    def repoparms_kmeans_groups(self):	
	(fname,stat)= QInputDialog.getText(self,"Get Input Parameters","Enter name of file parameters were saved in",QLineEdit.Normal,"")
	if stat:
		import pickle
		pkl = open(fname,'rb')
		self.savedparmsdict = pickle.load(pkl)
		self.kc1edit.setText(self.savedparmsdict['kc1'])
		self.kc2edit.setText(self.savedparmsdict['kc2'])
		self.stacknameedit.setText(self.savedparmsdict['stackname'])	
		self.foldernameedit.setText(self.savedparmsdict['foldername'])	
		self.trialsedit.setText(self.savedparmsdict['trials'])
		self.maxiteredit.setText(self.savedparmsdict['maxiter'])
		self.nprocedit.setText(self.savedparmsdict['nproc'])
		self.w1.masknameedit.setText(self.savedparmsdict['maskname'])
		self.w1.randsdedit.setText(self.savedparmsdict['randsd'])
		self.w1.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
		
    def setactiveheader(self):
	stack = self.stacknameedit.text()
	print "stack defined="+ stack
	header(str(stack), "active", one=True)

   
    def choose_file(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "", "HDF files (*.hdf)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.stacknameedit.setText(str(a))
        
	#Function choose_file started when  the  open_file of the  Poptwodali window is clicked (same as above but for bdb files(maybe we can combine these two into one function)
    def choose_file1(self):
	file_name1 = QtGui.QFileDialog.getOpenFileName(self, "Open Data File", "EMAN2DB/", "BDB FILES (*.bdb)" )
	a=QtCore.QString(file_name1)
	b=os.path.basename(str(a))
	c=os.path.splitext(b)[0]
	d="bdb:"+c
	print d
	self.stacknameedit.setText(d)

class Popupadvparams_kmeans_groups(QWidget):
    def __init__(self,savedparms):
        QWidget.__init__(self)
	
	self.x1 = 10
	self.x2 = 140
	self.x3 = 285
	
	self.y1 = 10
	self.yspc = 4
	
        #Here we just set the window title
	self.setWindowTitle('sxk_means_groups advanced parameter selection')
        #Here we just set a label and its position in the window
	title1=QtGui.QLabel('<b>sxk_means_groups</b> - set advanced params', self)
	title1.move(self.x1,self.y1)
        #Labels and Line Edits for User Input
        #Just a label
	self.y1 += 30
	
	title2= QtGui.QLabel('<b>Advanced</b> parameters', self)
	title2.move(self.x1,self.y1)
	
	self.y1 += 30
	
	self.savedparmsdict=savedparms
        #Example for User input stack name
        #First create the label and define its position
	maskname= QtGui.QLabel('Mask', self)
	maskname.move(self.x1,self.y1)
        #Now add a line edit and define its position
	self.masknameedit=QtGui.QLineEdit(self)
        self.masknameedit.move(self.x2,self.y1)
        #Adds a default value for the line edit
	self.masknameedit.setText(self.savedparmsdict['maskname'])
	
	self.mskfile_button = QtGui.QPushButton("Open .hdf", self)
	self.mskfile_button.move(self.x3, self.y1-self.yspc)
        #Here we define, that when this button is clicked, it starts subfunction choose_file
	QtCore.QObject.connect(self.mskfile_button, QtCore.SIGNAL("clicked()"), self.choose_mskfile)
	
	self.y1 += 30
	
	randsd= QtGui.QLabel('Random Seed', self)
	randsd.move(self.x1,self.y1)
	self.randsdedit=QtGui.QLineEdit(self)
	self.randsdedit.move(self.x2,self.y1)
	self.randsdedit.setText(self.savedparmsdict['randsd'])
	self.randsdedit.setToolTip('the seed used to generating random numbers (set to -1, means different and pseudo-random each time)')
	
	self.y1 += 30
	
	ctf= QtGui.QLabel('CTF', self)
	ctf.move(self.x1,self.y1)
	self.ctfchkbx = QtGui.QCheckBox("",self)
	self.ctfchkbx.move(self.x2, self.y1)
	self.ctfchkbx.setCheckState(self.savedparmsdict['ctf'])
	
	self.y1 += 30
	
    def choose_mskfile(self):
	#opens a file browser, showing files only in .hdf format
   	file_name = QtGui.QFileDialog.getOpenFileName(self, "Open File Containing Mask", "", "(*)")
        #after the user selected a file, we obtain this filename as a Qstring
	a=QtCore.QString(file_name)
	print a
        #we convert this Qstring to a string and send it to line edit classed stackname edit of the Poptwodali window
	self.masknameedit.setText(str(a))

###MAIN WINDOW	(started by class App)
#This class includes the layout of the main window; within each class, i name the main object self, to avoid confusion)    	
class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #sets the title of the window
	self.setWindowTitle('SPARX GUI')
        #creates a Pushbutton, named sxali2d, defines its position in the window 
        self.btn1 = QPushButton("sxali2d", self)
        self.btn1.move(10, 65)
        #sets an infotip for this Pushbutton
        self.btn1.setToolTip('2D  reference free alignment of an image series ')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.btn1, SIGNAL("clicked()"), self.twodali)
        #another Pushbutton, with a tooltip, not linked to a function yet
	self.btn2 = QPushButton("sxmref_ali2d", self)
        self.btn2.setToolTip('2D MULTI-referencealignment of an image series ')
        self.btn2.move(10, 95)
        #Pushbutton named Info
	self.picbutton = QPushButton(self)
        #when this button is clicked, this action starts the subfunction info
        self.connect(self.picbutton, SIGNAL("clicked()"), self.info)
	#creates a Pushbutton, named sxihrsr defines its position in the window 
        self.btn3 = QPushButton("sxihrsr", self)
        self.btn3.move(10, 125)
        #sets an infotip for this Pushbutton
        self.btn3.setToolTip('Iterative Real Space Helical Refinement ')
        #when this button is clicked, this action starts the subfunction twodali
        self.connect(self.btn3, SIGNAL("clicked()"), self.helicalrefinement)
	
	self.btn4 = QPushButton("sxali3d", self)
        self.btn4.move(10, 155)
        #sets an infotip for this Pushbutton
        self.btn4.setToolTip('Perform 3-D projection matching given initial reference volume and image series')
	self.connect(self.btn4, SIGNAL("clicked()"), self.ali3d)
	
	self.btn4 = QPushButton("sxk_means", self)
        self.btn4.move(10, 185)
        #sets an infotip for this Pushbutton
        self.btn4.setToolTip('K-means classification of a set of images')
	self.connect(self.btn4, SIGNAL("clicked()"), self.kmeans)
	
	
	self.btn5 = QPushButton("sxk_means_groups", self)
        self.btn5.move(10, 185+30)
        #sets an infotip for this Pushbutton
        self.btn5.setToolTip('determine \'best\' number of clusters in the data using K-means classification of a set of images')
	self.connect(self.btn5, SIGNAL("clicked()"), self.kmeansgroups)
	
        #this decorates the button with the sparx image
	icon = QIcon(get_image_directory()+"sparxicon.png")
	self.picbutton.setIcon(icon)
        self.picbutton.move(120, 5)
        self.picbutton.setToolTip('Info Page')
        #Quitbutton
        self.btn3 = QPushButton("Close", self)
        self.btn3.setToolTip('Close SPARX GUI ')
	self.btn3.move(180, 5)
        self.connect(self.btn3, QtCore.SIGNAL('clicked()'),QtGui.qApp, QtCore.SLOT('quit()'))
        #here we set two labels, their position and font style
	title=QtGui.QLabel('<b>SPARX</b> GUI', self)
	title1=QtGui.QLabel('<b>2D alignment</b> applications', self)
	title.move(10,10)
	title1.move(20, 45)
	QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 8))
	
    	#here we set the width and height of the main window
        self.resize(300,350)
	
   
    #This is the function two2ali, which is being started when the Pushbutton btn1 of the main window(called sxali2d) is being clicked
    def twodali(self):
        print "Opening a new popup window..."
        #opens the window Poptwodali, and defines its width and height
        #The layout of the Poptwodali window is defined in class Poptwodali(QWidget Window)
        self.w = Popuptwodali()
	self.w1 = Popupadvparams_ali2d(self.w.savedparmsdict)
        self.w.w1 = self.w1
        self.TabWidget = QtGui.QTabWidget()
    	self.TabWidget.insertTab(0,self.w,'Main')
    	self.TabWidget.insertTab(1,self.w1,'Advanced')
	self.TabWidget.resize(550,570)
    	self.TabWidget.show()
	
    def helicalrefinement(self):
        print "Opening a new popup window..."
        #opens the window Poptwodali, and defines its width and height
        #The layout of the Poptwodali window is defined in class Poptwodali(QWidget Window)
        self.w = PopupHelicalRefinement()
        self.w.resize(600,800)
        self.w.show()   
	
    def ali3d(self):
        print "Opening a new popup window..."
        #opens the window Poptwodali, and defines its width and height
        #The layout of the Poptwodali window is defined in class Poptwodali(QWidget Window)
        self.w = Popupthreedali()
	self.w1 = Popupadvparams_ali3d_1(self.w.savedparmsdict)
	self.w2 = Popupadvparams_ali3d_2(self.w.savedparmsdict)
	self.w.w1 = self.w1
	self.w.w2 = self.w2
	self.TabWidget = QtGui.QTabWidget()
    	self.TabWidget.insertTab(0,self.w,'Main')
    	self.TabWidget.insertTab(1,self.w1,'Advanced CTF and Search')
	self.TabWidget.insertTab(2,self.w2,'Advanced MISC')
	self.TabWidget.resize(550,650)
    	self.TabWidget.show()
        
	
    def kmeans(self):
        print "Opening a new popup window..."
        #opens the window Poptwodali, and defines its width and height
        #The layout of the Poptwodali window is defined in class Poptwodali(QWidget Window)
        
	self.w = Popupkmeans()
	self.w1 = Popupadvparams_kmeans(self.w.savedparmsdict)
        self.w.w1 = self.w1
        self.TabWidget = QtGui.QTabWidget()
    	self.TabWidget.insertTab(0,self.w,'Main')
    	self.TabWidget.insertTab(1,self.w1,'Advanced')
	self.TabWidget.resize(580,570)
    	self.TabWidget.show()
	
    def kmeansgroups(self):
        print "Opening a new popup window..."
	
	self.w = Popupkmeansgroups()
	self.w1 = Popupadvparams_kmeans_groups(self.w.savedparmsdict)
        self.w.w1 = self.w1
        self.TabWidget = QtGui.QTabWidget()
    	self.TabWidget.insertTab(0,self.w,'Main')
    	self.TabWidget.insertTab(1,self.w1,'Advanced')
	self.TabWidget.resize(580,570)
    	self.TabWidget.show()
	
    #This is the function info, which is being started when the Pushbutton picbutton of the main window is being clicked
    def info(self):
        print "Opening a new popup window..."
        #opens the window infosparx, and defines its width and height
        #The layout of the infosparx window is defined in class infosparx(QWidget Window)
        self.w = infosparx()
        self.w.resize(250,200)
        self.w.show()

#  this is the main class of the program
#  Here we provide the necessary imports. The basic GUI widgets are located in QtGui module.
class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        #here we define the main window (class MainWindow)
        self.main = MainWindow()
        #here we define that when all windows are closed, function byebye of class App will be started
        self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        #hshows main window
        self.main.show()
        
    #function byebye (just quit)  
    def byebye( self ):
        print' bye bye!'
        self.exit(0)

      
#  Necessary for execution of the program
def main(args):
    global app
    app = App(args)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)
