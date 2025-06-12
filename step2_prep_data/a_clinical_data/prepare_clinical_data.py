from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import pandas as pd


def get_parser():
    argparser = ArgumentParser()

    argparser.add_argument(
        '-c', "--clinical_data", required=True, type=Path,
        help="A `.tsv` file containing the clinical and demographic metrics for patients to be cleaned."
    )

    argparser.add_argument(
        '-o', '--output_folder', type=Path, default=Path('clinical_metrics'),
        help="The path name where results should be saved too."
    )

    return argparser


def process_mjoa(init_df):
    # Reformat the mJOA columns to avoid duplications and redundancies
    mjoa_cols = [
        "('mJOA', 'initial')",
        "('mJOA', '12 months')",
        "('mJOA; Total [CSA]', 'initial')",
        "('mJOA; Total [CSA]', '12 months')"
    ]
    mjoa_df = init_df.loc[:, mjoa_cols]
    # Try and fill in the mJOA initial with the values in replicated column if they are null
    ## Initial mJOA (pre-surgery)
    missing_idx = mjoa_df.loc[:, "('mJOA', 'initial')"].isna()
    mjoa_df.loc[missing_idx, "('mJOA', 'initial')"] = mjoa_df.loc[missing_idx, "('mJOA; Total [CSA]', 'initial')"]
    ## 1 year mJOA (post-surgery)
    missing_idx = mjoa_df.loc[:, "('mJOA', '12 months')"].isna()
    mjoa_df.loc[missing_idx, "('mJOA', '12 months')"] = mjoa_df.loc[missing_idx, "('mJOA; Total [CSA]', '12 months')"]
    # Isolate the mJOA columns from the rest of the dataset for safekeepting
    mjoa_df = mjoa_df.drop(["('mJOA; Total [CSA]', 'initial')", "('mJOA; Total [CSA]', '12 months')"], axis=1)
    return mjoa_cols, mjoa_df


def filter_post_surgical_metrics(init_df):
    timeless_first = np.where(init_df.columns == 'Site')[0][0]
    timeless_df = init_df.iloc[:, timeless_first:]
    timed_df = init_df.iloc[:, :timeless_first]
    # As we have handled mJOA already, keep only the values which would be available pre-surgery
    pre_surg_metrics = []
    for c in timed_df.columns:
        if c.split(',')[1] == " 'initial')":
            pre_surg_metrics.append(c)
    return pre_surg_metrics, timeless_df


def hrr(mjoa_init, mjoa_1year):
    numerator = mjoa_1year - mjoa_init
    denominator = 18 - mjoa_init
    return numerator / denominator


def misc_clean(cleaned_df):
    # Filter out any patients which were non-surgical
    cleaned_df = cleaned_df.loc[cleaned_df['Surgical'] == 1, :]
    cleaned_df = cleaned_df.drop('Surgical', axis=1)

    # Drop some remaining duplicated/irrelevant columns
    cleaned_df = cleaned_df.drop(columns=[
        "('Surgical', 'initial')",  # Uniform by definition
        "Number of Surgeries",  # Very rare to see more than 1
        "Treatment Plan",  # Always surgery
        "Site",  # Too difficult to encode w/o introducing bias
        "('BMI', 'initial')",  # Duplicate
        "CSM Duration",  # Symptom duration is nearly identical
        "Followup: 6-18 weeks",  # Not relevant
        "Followup: 12 month",  # Not relevant
        "Followup: 24 month",  # Not relevant
        "Followup: 60 month",  # Not relevant
        "Date of Assessment",  # Not relevant
        "Work Status"  # Better encoding exists in 'Work Status (Category)'
    ])

    # Update the column headers to no longer state the time point (as they are all the same now)
    cleaned_df.columns = [c.replace("'initial'", "") for c in cleaned_df.columns]

    # Set all EQ5D values of '4' to null (clinicians use this to represent "did not answer" for some reason)
    for c in cleaned_df.columns:
        if 'EQ5D' in c:
            cleaned_df.loc[cleaned_df[c] == 4, c] = np.nan

    # Fix a malformed BMI value; set it to null so imputation can handle it later
    cleaned_df.loc[cleaned_df['BMI'] == 0, 'BMI'] = np.nan
    return cleaned_df


def calculate_targets(final_df):
    # Calculate the Hirabayashi Recovery Ratio (HRR) for each patient
    hrr_vals = hrr(final_df['mJOA initial'], final_df['mJOA 12 months'])
    final_df['HRR'] = hrr_vals

    # Calculate the recovery class of each patient
    final_df['Recovery Class'] = ['good' if v >= 0.5 else "fair" for v in hrr_vals]
    final_df.loc[pd.isna(hrr_vals), 'Recovery Class'] = np.nan
    final_df = final_df.dropna(subset=['Recovery Class'])

    return final_df


def main(clinical_data: Path, output_folder: Path):
    # Read the clinical data into a dataframe
    init_df = pd.read_csv(clinical_data, sep='\t')
    init_df = init_df.set_index('GRP')

    # Process the mJOA columns to be more useful
    mjoa_cols, mjoa_df = process_mjoa(init_df)

    # Drop the mJOA columns from the original DF, as they are in mjoa_df now
    init_df = init_df.drop(mjoa_cols, axis=1)

    # Split the dataframe into columns which were collected at multiple timepoints, and those which weren't
    pre_surgery_columns, timeless_df = filter_post_surgical_metrics(init_df)

    # Select only the pre-surgical metrics from the original dataset
    cleaned_df = init_df.loc[:, pre_surgery_columns]

    # Add back in the (clean) time-insensitive metrics
    cleaned_df.loc[:, timeless_df.columns] = timeless_df

    # Do some remaining miscellaneous cleaning tasks
    cleaned_df = misc_clean(cleaned_df)

    # Add back in the mJOA values in preparation for HRR calculation
    final_df = cleaned_df.copy()
    final_df.loc[:, mjoa_df.columns] = mjoa_df

    # Reformat the column labels to prevent issues during analysis
    cols = [c.replace("'", "").replace(",", "").replace(" )", ")") for c in final_df.columns]
    cols = [c[1:-1] if c[0] == "(" and c[-1] == ")" else c for c in cols]
    final_df.columns = cols

    # Calculate the final target metrics, HRR and recovery ratio
    final_df = calculate_targets(final_df)

    # Create the output directory if it doesn't already exist
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    # Save the dataframe in this current state for use in clinical metric analysis
    full_data_file = output_folder / "full_data.tsv"
    final_df.to_csv(full_data_file, sep='\t')

    # Drop metrics which would confuse the ML model
    final_df = final_df.drop(columns=[
        'mJOA 12 months',
        'HRR'
    ])

    # Save the ML-prepped file
    ml_data_file = output_folder / "clinical_ml.tsv"
    final_df.to_csv(ml_data_file, sep='\t')


if __name__ == '__main__':
    # Parse the command-line arguments
    parser = get_parser()
    argvs = parser.parse_args().__dict__

    main(**argvs)
