#!/bin/bash

# Pull the Modular Optuna ML commit used by these analyses
git submodule init
git submodule update

# Create a directory for the local conda environments if they don't already exist
LOCAL_ENV_DIR="./env"
if [ ! -d "$LOCAL_ENV_DIR" ]; then
  mkdir "$LOCAL_ENV_DIR"
fi

# Create the Conda environment with the packages needed for this project, if it doesn't already exist
ANALYSIS_ENV_NAME="DCM_Disk_ML"
if conda env list | grep "$ANALYSIS_ENV_NAME"; then
  echo "$ANALYSIS_ENV_NAME already exists"
else
  conda env create --file "environment.yml"
fi

# Create the Conda environment with the packages used by MOOP
MOOP_ENV_NAME="modular_optuna_ml"
if conda env list | grep "$MOOP_ENV_NAME"; then
  echo "$MOOP_ENV_NAME already exists"
else
  conda env create --file "modular_optuna_ml/environment.yml"
fi

# Link the pre-commit hook for Jupyter notebook handling, if it doesn't already exist
if [[ ! -f ".git/hooks/pre-commit" ]]; then
  ln git_hooks/pre-commit .git/hooks/
fi