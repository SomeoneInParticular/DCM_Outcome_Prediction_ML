#!/bin/bash

# Parse the command line arguments
INPUT_FILE=$1
OUT_FOLDER=$2
SCT_PATH=$3

# Output file name for this script
PER_VERT_OUT_NAME="deepseg_disc_metrics.csv"

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
SEG_NAME="${SEG_NAME%%.*}_deepseg.nii.gz"

SEG_FILE="$OUT_FOLDER/$SEG_NAME"

# Run DeepSeg (contrast agnostic segmentation) on the file
if [ ! -f "$SEG_FILE" ]; then
  sct_deepseg "spinalcord" -i "$INPUT_FILE" -o "$SEG_FILE"
else
  printf "\n"
  echo "Segmentation already exists, skipping"
fi

# Generate the output values for vertebral labelling
VERT_FILE="$OUT_FOLDER/${SEG_NAME%%.*}_labeled.nii.gz"

# Identify the vertebrae within the segmentation
if [ ! -f "$VERT_FILE" ]; then
  # Attempt to run vertebrae labelling
  echo "Attempting vertebral labelling!"
  bash "label_vertebrae.sh" "$INPUT_FILE" "$SEG_FILE" "$OUT_FOLDER" "$CONTRAST" "$SCT_PATH" "$VERT_FILE"
else
  printf "\n"
  echo "Vertebral labels already exist, skipping"
fi

if [ ! -f "$VERT_FILE" ]; then
  echo "No vertebral label found, terminating early"
  exit 1
fi

# Designate the positions of the position annotations we have/will generate
DISC_POS_FILE="$OUT_FOLDER/${SEG_NAME%%.*}_labeled_discs.nii.gz"
VERT_POS_FILE="$OUT_FOLDER/${SEG_NAME%%.*}_labeled_verts.nii.gz"

# If the disc position annotations don't exist, generate them
if [ ! -f "$VERT_POS_FILE" ]; then
  # Run the disc offset script
  source activate DCM_Disk_ML
  python disc_to_vert_pos.py -i "$DISC_POS_FILE"
else
  printf "\n"
  echo "Disc offset annotations already exist, skipping."
fi

# A temporary directory to avoid overwriting the previous vertebral labels
TMP_DIR="$OUT_FOLDER/tmp"
TMP_OUT="$TMP_DIR/${SEG_NAME%%.*}_labeled.nii.gz"
DISC_OUT="$OUT_FOLDER/${SEG_NAME%%.*}_disc_centered_labeled.nii.gz"

if [ ! -f "$DISC_OUT" ]; then
  echo "Attempting 'disc' labelling!"
  # Create a tmp directory to avoid overwrites
  if [ ! -d "$TMP_DIR" ]; then
    mkdir "$TMP_DIR"
  fi
  # Attempt to label the "discs" using the vert-centered positions
  sct_label_vertebrae -i "$INPUT_FILE" -s "$SEG_FILE" -c "$CONTRAST" -ofolder "$TMP_DIR" -discfile "$VERT_POS_FILE"
  ls "$TMP_DIR"
  # Rename the result to denote its disc-based nature, and move it alongside the rest of the results
  mv "$TMP_OUT" "$DISC_OUT"
  # Remove the TMP directory
  if [ -d "$TMP_DIR" ]; then
    rm -r "$TMP_DIR"
  fi
else
  printf "\n"
  echo "Disc labels already exist, skipping"
fi

# Generate the output values for segmentation processing
PER_VERT_OUT_FILE="$OUT_FOLDER/$PER_VERT_OUT_NAME"

# Use the disc labels alongside the segmentation to generate disc-centered "vertebral" metrics
if [ ! -f "$PER_VERT_OUT_FILE" ]; then
  echo "Beginning segmentation processing"
  OLD_DIR=$PWD
  cd "$OUT_FOLDER" || echo "Could not enter output directory for some reason; perhaps it got deleted during runtime?"
  sct_process_segmentation -i "$SEG_FILE" -vert 1:7 -vertfile "$DISC_OUT" -perlevel 1 -o "$PER_VERT_OUT_FILE"
  cd "$OLD_DIR" || echo "Could not return to original directory for some reason; no idea how you managed that!"
  echo "Finished segmentation processing"
else
  printf "\n"
  echo "Metric file already exists, skipping"
fi
