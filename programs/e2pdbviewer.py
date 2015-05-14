#!/usr/bin/env python

# Author: James Michael Bell 3/16/14 (jmbell@bcm.edu)
# Copyright (c) 2014-2020 Baylor College of Medicine
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

from EMAN2 import *
from emapplication import EMApp
from emscene3d import EMScene3D, EMInspector3D
from emshapeitem3d import *
import os
import sys

from PyQt4 import QtCore
from PyQt4 import QtGui


def main():
	
	progname = os.path.basename(sys.argv[0])
	usage = """e2pdbviewer.py <project directory>
	
	A simple program to view a .pdb file on your computer. This is simply an PDB
	specific interface to the more general EMScene3D viewer. All functionalities
	are accessible from here.
	"""
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	parser.add_argument("--file",type=str,help="Specify the pdb file you wish to \
		view", required=False, default=None)
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent \
		process, used for cross platform PPID",default=-1)
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", \
		metavar="n", type=int, default=0, help="verbose level [0-9], higner \
		number means higher level of verboseness")
	(options, args) = parser.parse_args()
	
	logid=E2init(sys.argv,options.ppid)
	
	app = EMApp()
	viewer = EMScene3D()
	if options.file:
		structure = EMStructure(options.file)
		viewer.addChild(structure)
	viewer.show()
	app.execute()
	
	E2end(logid)

if __name__ == '__main__':
	main()