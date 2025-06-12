# Post-Surgical Outcome Prediction of DCM Patients Using Machine Learning Models

## What is this?

This repo contains the scripts used to process, clean, and run automated machine learning analyses for predicting post-surgical DCM outcomes, using a combination of clinical and MRI-derived metrics. The publication corresponding to this repository can be found here (TODO).

## Replicating our Analysis

If you want to replicate our analyses, please follow the steps below:

### Pre-requisites

* A working Linux operating system (or other OS with Bash installed on the Path)
* A working Git installation, to clone and manage the needed files
* A working installation of SCT 7.0 (available [here](https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/tag/7.0)).
* A working Conda (or, even better, Mamba) installation. We recommend [MiniForge](https://github.com/conda-forge/miniforge).
* A clone of this repository on your machine. It is available [here](https://github.com/SomeoneInParticular/DCM_Outcome_Prediction_ML) if you somehow found this README outside the repository website.
* A copy of our dataset: it is available upon reasonable request from [Dr. David Cadotte](mailto:david.cadotte@ucalgary.ca).
* Ran `setup.sh`; this should do the following for you:
  * Pull the Modular Optuna submodule which was used for this analysis.
  * Create a local Conda environment with the dependencies packages for this repository.
  * Create a local Conda environment with the dependencies for Modular Optuna ML.
  * Create a git hook which strips the outputs/metadata of Jupyter Notebooks before each commit; prevents use from accidentally committing the output of our analyses (and risking confidentiality breaches).

### Processing the MRI Sequences

1. Activate the Conda/Mamba environment for the module; this can be done on the command line via:

```bash
conda activate ./env/DCM_Disk_ML
```

1. Follow the steps detailed in `step1_process_mri` to process the MRI sequences, generating the MRI-derived metric datasets using a Spinal Cord Toolbox (version 7 or greater).
1. Then, run the instructions detailed in `step2_prep_data` to gather all the data into one place and format it for use in MOOP.
1. Run the MOOP analyses for all combinations of dataset, model, and study configuration by following the instructions in `step3_run_analysis`.
