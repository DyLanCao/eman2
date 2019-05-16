#!/usr/bin/env bash

set -xe

# Download and install Miniconda
export MINICONDA_URL="https://repo.continuum.io/miniconda"
export MINICONDA_FILE="Miniconda3-4.4.10-Linux-x86_64.sh"

curl -L -O "${MINICONDA_URL}/${MINICONDA_FILE}"
bash $MINICONDA_FILE -b

# Configure conda
source ${HOME}/miniconda3/bin/activate root
conda config --set show_channel_urls true

conda update conda -c defaults --yes
conda install conda-build -c defaults --yes
conda install cmake=3.9 -c defaults --yes
conda install eman-deps=15.0 -c cryoem/label/py3 -c cryoem -c defaults -c conda-forge --yes
conda clean --all --yes
