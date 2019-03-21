#!/usr/bin/env python

#
# Copyright (C) 2016  Thorsten Wagner (thorsten.wagner@mpi-dortmund.mpg.de)
#

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

from __future__ import print_function
import argparse
from json import dump
import subprocess

import global_def


argparser = argparse.ArgumentParser(
	description='Train crYOLO on any dataset',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)

argparser.add_argument(
	'particle_diameter',
	type=int,
	help='Particle diameter in pixel')

argparser.add_argument(
	'training_dir',
	type=str,
	help='Path to training images')

argparser.add_argument(
	'annot_dir',
	type=str,
	help='Path to training images')

argparser.add_argument(
	'--architecture',
	default="PhosaurusNet",
	type=str,
	help='Specifiy the used model')

argparser.add_argument(
	'--input_size',
	type=int,
	default=1024,
	help='Size to which the image is resized')

argparser.add_argument(
	'--overlap_patches',
	type=int,
	default=200,
	help='Amount of overlapping in pixel')

argparser.add_argument(
	'--num_patches',
	type=int,
	default=1,
	help='Number of patches used during training')

argparser.add_argument(
	'--train_times',
	type=int,
	default=10,
	help='How often a images is augmented and repeadet in one epoch.')

argparser.add_argument(
	'--saved_weights_name',
	type=str,
	default="cryolo_model.h5",
	help='Name of the model')

argparser.add_argument(
	'--pretrained_weights_name',
	type=str,
	default="cryolo_model.h5",
	help='Name of the model')

argparser.add_argument(
	'--batch_size',
	type=int,
	default=6,
	help='How many patches are processed in parallel')

argparser.add_argument(
	'--learning_rate',
	type=float,
	default=0.0001,
	help='Learning rate used during training.')

argparser.add_argument(
	'--np_epoch',
	type=int,
	default=100,
	help='Maximum number of epochs.')

argparser.add_argument(
	'--object_scale',
	type=float,
	default=5.0,
	help='Loss scale for particles.')

argparser.add_argument(
	'--no_object_scale',
	type=float,
	default=1.0,
	help='Loss scale for background.')

argparser.add_argument(
	'--coord_scale',
	type=float,
	default=1.0,
	help='Loss scale for coordinates.')

argparser.add_argument(
	'--valid_image_dir',
	type=str,
	default="",
	help='Path to validation images')

argparser.add_argument(
	'--valid_annot_dir',
	type=str,
	default="",
	help='Path to validation annotations')

argparser.add_argument(
	'--warmup',
	type=int,
	default=5,
	help='Warm up epochs')

argparser.add_argument(
	'--gpu',
	default=0,
	type=int,
	nargs="+",
	help="Specifiy which gpu(s) should be used. Multiple GPUs are separated by a whitespace")

argparser.add_argument(
	'--early',
	default=5,
	type=int,
	help='Early stop patience. If the validation loss did not improve longer than the early stop patience, '
		 'the training is stopped.')

argparser.add_argument(
	'--fine_tune',
	default=False,
	action="store_true",
	help='Set it to true if you only want to use the fine tune mode')

argparser.add_argument(
    "--gpu_fraction",
    type=float,
    default=1.0,
    help="Specify the fraction of memory per GPU used by crYOLO during training. Only values between 0.0 and 1.0 are allowed.",
)

argparser.add_argument(
    "-nc",
    "--num_cpu",
    type=int,
    default=-1,
    help="Number of CPUs used during training. By default it will use half of the available CPUs.",
)

argparser.add_argument(
	"--cryolo_train_path",
	default=None,
	type=str,
)




def main():
	# Read arguments
	args = argparser.parse_args()

	architecture = args.architecture
	particle_diameter = args.particle_diameter
	trainging_dir = args.training_dir
	annot_dir = args.annot_dir
	input_size = args.input_size
	num_patches = args.num_patches
	overlap_patches = args.overlap_patches
	train_times = args.train_times
	saved_weights_name = args.saved_weights_name
	pretrained_weights_name = args.pretrained_weights_name
	batch_size = args.batch_size
	learning_rate = args.learning_rate
	np_epoch = args.np_epoch
	object_scale = args.object_scale
	no_object_scale = args.no_object_scale
	coord_scale = args.coord_scale
	valid_image_dir = args.valid_image_dir
	valid_annot_dir = args.valid_annot_dir
	fine_tune = args.fine_tune
	gpu_fraction = args.gpu_fraction
	num_cpu = args.num_cpu
	cryolo_train_path = args.cryolo_train_path

	warmup = args.warmup
	early_stop = int(args.early)

	if type(args.gpu) is list:
		str_gpus = [str(entry) for entry in args.gpu]
	else:
		str_gpus = str(args.gpu)

	arg_gpu = ' '.join(str_gpus)

	# Create config file
	model_dict = {'architecture': architecture,
				  'input_size': input_size,
				  'anchors': [particle_diameter, particle_diameter],
				  'overlap_patches': overlap_patches,
				  'max_box_per_image': 1000,
				  'num_patches': num_patches}

	train_dict = {'train_image_folder': trainging_dir,
				  'train_annot_folder': annot_dir,
				  'train_times': train_times,
				  'pretrained_weights': pretrained_weights_name,
				  'batch_size': batch_size,
				  'learning_rate': learning_rate,
				  'nb_epoch': np_epoch,
				  'warmup_epochs': 0,
				  'object_scale': object_scale,
				  'no_object_scale': no_object_scale,
				  'coord_scale': coord_scale,
				  'class_scale': 1.0,
				  "saved_weights_name": saved_weights_name,
				  "debug": True,
				  "log_path": "cryolo_logs/"
				  }

	valid_dict = {'valid_image_folder': valid_image_dir,
				  'valid_annot_folder': valid_annot_dir,
				  'valid_times': 1
				  }
	dict = {"model": model_dict, "train": train_dict, "valid": valid_dict}
	path = "config_yolo.json"
	with open(path, 'w') as f:
		dump(dict, f, ensure_ascii=False, indent=4)

	# Run the training
	warmup_argument = "-w=" + str(warmup)
	gpu_argument = "-g=" + arg_gpu
	early_stop = "-e=" + str(early_stop)
	fine_tune_argument = ""
	if fine_tune:
		fine_tune_argument = "--fine_tune"
	gpu_fraction_arg = "--gpu_fraction=1.0"
	if gpu_fraction < 1.0 and gpu_fraction > 0.0:
		gpu_fraction_arg = "--gpu_fraction=" + str(gpu_fraction)

	num_cpu_arg = ""
	if num_cpu != -1:
		num_cpu_arg = "--num_cpu="+str(num_cpu)
	cryolo_ex_pth = "cryolo_train.py"
	if cryolo_train_path:
		cryolo_ex_pth = cryolo_train_path
	if not fine_tune:
		command = [cryolo_ex_pth, "-c=config_yolo.json", warmup_argument, gpu_argument, early_stop, gpu_fraction_arg]

		if num_cpu != -1:
			command.append(num_cpu_arg)
		subprocess.check_call(
			command)

	warmup_argument = "-w=0"
	command = [cryolo_ex_pth, "-c=config_yolo.json", warmup_argument, gpu_argument, early_stop, gpu_fraction_arg]
	if fine_tune:
		command.append(fine_tune_argument)
	if num_cpu:
		command.append(num_cpu_arg)

	subprocess.check_call(
		command)


if __name__ == "__main__":
	global_def.print_timestamp( "Start" )
	global_def.write_command()
	main()
	global_def.print_timestamp( "Finish" )
