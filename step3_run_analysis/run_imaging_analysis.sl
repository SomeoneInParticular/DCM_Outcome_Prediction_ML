#!/bin/bash
#SBATCH --mem=1G
#SBATCH --nodes=1
#SBATCH --cpus-per-task 16
#SBATCH --time 48:00:00
#SBATCH --partition=cpu2023,cpu2022,cpu2021,cpu2019
#SBATCH --array=0-74
##########################################################################
# ^ VALIDATE THIS MANUALLY; IT SHOULD BE THE PRODUCT OF THE NUMBER OF  ^ #
# ^ STUDY, MODEL, AND DATA CONFIGURATION, MINUS 1                      ^ #
##########################################################################

# Validate that all values here are correct before running the SLURM script!
N_DATASETS=15
N_MODELS=5
STUDY_FOLDER="./study_config"
MODEL_FOLDER="./model_configs"
DATA_FOLDER="../step2_prep_data/b_dataset_gen/datasets/imaging/configs"
MOOPS_SOURCE="../modular_optuna_ml"

# Purge any loaded modules
module purge

# Reset to the base environment; otherwise stupidity ensues
source activate base

## Un-comment the statement below to take the first command line parameter as the task ID. ##
#SLURM_ARRAY_TASK_ID=$1

# Calculate the study divisor
STUDY_DIVISOR=$((N_MODELS * N_DATASETS))

# Grab the corresponding study configuration
STUDY_IDX=$((SLURM_ARRAY_TASK_ID / STUDY_DIVISOR + 1))
STUDY_FILE=$(find $STUDY_FOLDER/*.json | head -n $STUDY_IDX | tail -n 1)

# Get the "inner" index for further querying via modulo
INNER_IDX=$((SLURM_ARRAY_TASK_ID % STUDY_DIVISOR))

# Get the model configuration via modulo indexing of the fileset
MODEL_IDX=$((INNER_IDX % N_MODELS + 1))
MODEL_FILE=$(find $MODEL_FOLDER/*.json | head -n $MODEL_IDX | tail -n 1)

# Get the data configuration via floor division of the fileset
DATA_IDX=$((INNER_IDX / N_MODELS + 1))
DATA_FILE=$(find $DATA_FOLDER/*.json | head -n $DATA_IDX | tail -n 1)

# Run Modular Optuna ML using the configuration files selected
conda activate modular_optuna_ml
python "$MOOPS_SOURCE/run_ml_analysis.py" -d "$DATA_FILE" -m "$MODEL_FILE" -s "$STUDY_FILE" --overwrite --timeout 300
