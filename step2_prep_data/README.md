# Dataset Preparation

Now, we will prepare the clinically-derived metrics for analysis, and generate the final datasets (clinical, imaging, and combined "full") for MOOP analysis.

1. Run `a_clinical_data/prepare_clinical_data.py`, pointing it to the "participants.tsv" file of the dataset.
   * This should generate a processed file, containing the clinically-derived and demographic features of each patient in the dataset
2. Then, run `b_dataset_gen/generated_full_datasets.py`.
   * It requires two inputs; the `.tsv` file you generated in the prior substep (the `--clinical-data`) and a path to the directory containing the MRI-derived metric files we generated in the prior step (the `--mri-path`)
   * This will generate a number of `.tsv` files in the output directory you specified (`b_dataset_gen/datasets` if you didn't specify one), alongside a the dataset configuration files required to use them in a MOOP analysis.