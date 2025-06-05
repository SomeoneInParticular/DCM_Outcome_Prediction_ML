#!/bin/bash

# Parse the command line arguments
INPUT_FILE=$1
OUT_FOLDER=$2
SCT_PATH=$3

# Output file name for this script
PER_SLICE_OUT_NAME="deepseg_perslice_metrics.csv"

# Add the SCT utilities to the PATH
export PATH="$PATH:$SCT_PATH"

# Identify attributes of the file
if [[ "$INPUT_FILE" == *"T1"* ]]; then
  CONTRAST="t1"
elif [[ "$INPUT_FILE" == *"T2"* ]]; then
  CONTRAST="t2"
else
  echo "Invalid file contrast, ending early"
  exit
fi

# Generate the output values for this segmentation
SEG_NAME="${INPUT_FILE##*/}"
SEG_NAME="${SEG_NAME%%.*}"

SEG_FILE="$SEG_NAME""_deepseg.nii.gz"
SEG_FILE="$OUT_FOLDER/$SEG_FILE"

# Run DeepSeg (contrast agnostic segmentation) on the file
if [ ! -f "$SEG_FILE" ]; then
  sct_deepseg "spinalcord" -i "$INPUT_FILE" -o "$SEG_FILE"
else
  printf "\n"
  echo "Segmentation already exists, skipping"
fi

# Generate the output values for vertebral labelling
VERT_FILE="$OUT_FOLDER/$SEG_NAME""_labeled.nii.gz"

# Identify the vertebrae within the segmentation
if [ ! -f "$VERT_FILE" ]; then
  echo "Begging vertebrae labelling."
  sct_label_vertebrae -i "$INPUT_FILE" -s "$SEG_FILE" -c "$CONTRAST" -ofolder "$OUT_FOLDER"
else
  printf "\n"
  echo "Vertebral labels already exist, skipping"
fi

# Generate the output values for segmentation processing
PER_SLICE_OUT_FILE="$OUT_FOLDER/$PER_SLICE_OUT_NAME"

# Use those labels alongside the segmentation to generate per-vertebrae metrics
if [ ! -f "$PER_SLICE_OUT_FILE" ]; then
  echo "Beginning segmentation processing"
  OLD_DIR=$PWD
  cd "$OUT_FOLDER" || echo "Could not enter output directory for some reason; perhaps it got deleted during runtime?"
  sct_process_segmentation -i "$SEG_FILE" -vert 2:7 -vertfile "$VERT_FILE" -perslice 1 -o "$PER_SLICE_OUT_NAME"
  cd "$OLD_DIR" || echo "Could not return to original directory for some reason; no idea how you managed that!"
  echo "Finished segmentation processing"
else
  printf "\n"
  echo "Metric file already exists, skipping"
fi
