#!/bin/bash

# Parse the command line arguments
INPUT_FILE=$1
SEG_FILE=$2
OUT_FOLDER=$3
CONTRAST=$4
SCT_PATH=$5
EXPECTED_OUT=$6

# Add the SCT utilities to the PATH
export PATH="$PATH:$SCT_PATH"

# Bad run file, denoting this has been tried before and failed
BAD_RUN_FILE="$OUT_FOLDER/FAILED_VERTEBRAE_SEG"

# Check if a file exists in the output directory, denoting that this has been attempted (and failed) already
if [ -f "$BAD_RUN_FILE" ]; then
  echo "Prior attempt to label vertebrae failed, not trying again!"
  exit 1
fi

# Attempt to label the vertebrae
echo "Beginning vertebrae labelling."
sct_label_vertebrae -i "$INPUT_FILE" -s "$SEG_FILE" -c "$CONTRAST" -ofolder "$OUT_FOLDER"

# Generate the output values for vertebral labelling
SEG_NAME="${INPUT_FILE##*/}"
SEG_NAME="${SEG_NAME%%.*}"

# If it failed to do so (usually due to not automatically finding the C2C3 disk), 'touch' a file marking it as such
if [ ! -f "$EXPECTED_OUT" ]; then
  echo "Vertebral labelling failed, creating marking file"
  touch "$BAD_RUN_FILE"
fi
