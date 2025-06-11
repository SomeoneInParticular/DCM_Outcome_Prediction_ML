# Post-Surgical Outcome Prediction of DCM Patients Using Machine Learning Models

## What is this?

This repo contains the scripts used to process, clean, and run automated machine learning analyses for predicting post-surgical DCM outcomes, using a combination of clinical and MRI-derived metrics. The publication corresponding to this repository can be found here (TODO).

## Replicating our Analysis

If you want to replicate our analyses, please follow the steps below:

### Pre-requisites

* Have a working installation of SCT 7.0 (available [here](https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/tag/7.0))
* A clone of this repository on your machine
* A Conda/Mamba environment which has the packages designated within `environment.yml`
* A copy of Modular Optuna ML, and the corresponding Conda/Mamba environment
* A copy of our dataset: it is available upon reasonable request from [Dr. David Cadotte](mailto:david.cadotte@ucalgary.ca)

### Processing the MRI Sequences

1. Activate the Conda/Mamba environment you installed the requisite packages into, as detailed in 
1. Follow the steps detailed in `step1_process_mri` to process the MRI sequences, generating the MRI-derived metric datasets using a Spinal Cord Toolbox (version 7 or greater).
1. Then, run the instructions detailed in `step2_prep_data` to gather all the data into one place and format it for use in MOOP.
