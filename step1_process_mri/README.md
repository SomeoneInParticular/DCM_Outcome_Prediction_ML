# MRI-Derived Metric Generation

First, we need to process the MRI sequences in your dataset to generate MRI-morphometrics for each patient. To do this:

1. Run `a_deepseg/iterative_sct.py` once for each `run_` script; run `python a_deepseg/iterative_sct.py -h` for details on how to do this.
   * The script searches for **ALL** `.nii.gz` files in a specified directory to run the script on. You should ensure only the MRI sequences you want to segment are contained within it (and not, for example, any image segmentations or labels that happen to be in the `.nii.gz` format).
   * You will need an output directory to store the results of each script. If using a BIDS dataset, we recommend specifying the `derivatives` path as the output for ease of re-use. Alternatively, if you don't want to modify your BIDS dataset, the output directory can be anywhere, so long as it exists before you run the script.
   * Given the size of our dataset, we recommend running this on a HPC (or overnight) if possible, as each script can take a while to complete.
2. Once all scripts are done, modify the `ROOT_DIR` of the `b_stack_metrics/gather_results.sh` file and run it. 
   * This should create a directory `b_stack_metrics/mri_metrics` with four `.tsv` files within it; these are the MRI-derived morphometrics for all samples in the dataset.
