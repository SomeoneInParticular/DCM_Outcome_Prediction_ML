#!/bin/bash

# Replace this with the output directory you used prior
ROOT_DIR=""

# Un-comment if you are running this in an HPC context, so the Conda environment is loaded properly
#conda activate DCM_Disk_ML

# Create a directory to store everything in
if [ ! -d "./mri_metrics" ]; then
  mkdir "mri_metrics"
fi

# Gather the vertebral metrics
echo "Gathering vertebral metrics..."
python stack_metrics.py -r "$ROOT_DIR" -g "**/*_vertebrae_metrics.csv" -o "mri_metrics/dcm_vert.tsv"
echo "Vertebral metrics gathered!"

# Gather the disc-centered metrics
echo "Gathering disc metrics..."
python stack_metrics.py -r "$ROOT_DIR" -g "**/*_disc_metrics.csv" -o "mri_metrics/dcm_disc.tsv" --disc_centered
echo "Disc metrics gathered!"

# Gather the per-slice metrics
echo "Gathering slice metrics..."
python stack_metrics.py -r "$ROOT_DIR" -g "**/*_perslice_metrics.csv" -o "mri_metrics/dcm_slice.tsv" --per_slice
echo "Slice metrics gathered!"

# Gather the PAM50 slice metrics
echo "Gathering PAM50-normalized slice metrics..."
python stack_metrics.py -r "$ROOT_DIR" -g "**/*_pam50_metrics.csv" -o "mri_metrics/dcm_pam50.tsv" --per_slice
echo "PAM50-normalized slice metrics gathered!"

echo "DONE!"
