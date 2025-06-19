from argparse import ArgumentParser
from pathlib import Path

import pandas as pd


# Indices used through this program for denoting a sample
IDX = ['GRP', 'orientation', 'weight', 'algorithm', 'run']


def get_parser() -> ArgumentParser:
    argparser = ArgumentParser()

    # Required
    argparser.add_argument(
        '-g', '--glob_pattern', required=True,
        help="The glob pattern to identify the files you want to stack. i.e. 'sub-*/**/*_disc_metrics.csv'. "
             "Acts as if `shopt -s globstar` was used, allowing for double asterisk (`**`) recursive search."
    )
    argparser.add_argument(
        '-o', '--output', required=True, type=Path,
        help="The filename that the stacked metrics should be saved too. To avoid issues, provide the full (resolved) "
             "path and filename w/o an extension (results are always saved in `.tsv` format)."
    )

    # Optional
    argparser.add_argument(
        '-r', '--root_dir', default='.', type=Path,
        help="Root directory to initiate the glob search in. If not specified, starts in the director you called this "
             "script from."
    )

    # Flags
    argparser.add_argument(
        '--per_slice', action='store_true',
        help="Denotes that the input data should be treated as 'per-slice' results, calculated metrics across the "
             "entire subject (rather than per-label, the default)."
    )
    argparser.add_argument(
        '--disc_centered', action='store_true',
        help="Denotes that the vertebral labels were offset to center them on the discs; adding this flag will change "
             "the column labels to make clear that this is the case."
    )

    return argparser


def clean_mri_data(init_df: pd.DataFrame):
    # Copy the DF in case the user wants a "dry run"
    cleaned_df = init_df.copy()

    # Getting the "run" for a file is tricky enough to warrant a nested function
    def _get_run(r):
        fname=r['Filename']
        if 'run-' not in fname:
            return 1  # If no run is specified, by definition there was only one
        else:
            run_no = int(fname.split('run-')[-1].split('_')[0])
            return run_no

    # Generate a number of columns based on the original MRI sequence's filename
    filename_derived_attribs = {
        "GRP": lambda r: r['Filename'].split('sub-')[-1].split('_')[0],
        "orientation": lambda r: r['Filename'].split('sub-')[-1].split('_')[1].split('q-')[-1],
        "weight": lambda r: r['Filename'].split('sub-')[-1].split('_')[-2],
        "algorithm": lambda r: r['Filename'].split('sub-')[-1].split('_')[-1].split('.')[0],
        "run": _get_run
    }

    for c, lf in filename_derived_attribs.items():
        cleaned_df[c] = cleaned_df.apply(lf, axis=1)

    # Drop un-needed columns
    cleaned_df.drop(['Filename', 'Timestamp', 'SCT Version', 'DistancePMJ', "Slice (I->S)"], axis=1, inplace=True)

    return cleaned_df


def pivot_vertlabels(init_df: pd.DataFrame):
    # Pivot along the vertebral level to make it a feature (rather than a sample)
    sub_df = init_df.set_index([*IDX, 'VertLevel'])
    pivot_df = sub_df.unstack(level='VertLevel')

    # Re-label the columns to be easier to understand
    vert_label_cols = [f"{c[0]} [V{c[1]}]" for c in pivot_df.columns]
    pivot_df.columns = vert_label_cols

    # Return the result
    return pivot_df


def calc_perslice_stats(init_df: pd.DataFrame):
    # Drop VertLevel and Length, as they have no meaning here
    result_df = init_df.drop(['VertLevel', 'SUM(length)'], axis=1)

    # Drop all STD metrics, as they are not relevant
    std_cols = [c for c in init_df.columns if "STD" in c]
    result_df = result_df.drop(std_cols, axis=1)

    # Strip the "MEAN" from the remaining columns, as we will need to differentiate later
    new_cols = [c.replace('MEAN(', '[').replace(')', ']') for c in result_df.columns]
    result_df.columns = new_cols

    # Group by our indices
    df_groups = result_df.groupby(IDX)

    # Calculate various statistics for each remaining element
    result_subsets = {
        'MIN': df_groups.min(),
        'MAX': df_groups.max(),
        'MEAN': df_groups.mean(),
        'STD': df_groups.std()
    }

    # Update columns to be much clearer
    for k, v in result_subsets.items():
        v.columns = [f"{k} {c}" for c in v.columns]

    # Concatenate them together
    final_df = pd.concat(result_subsets.values(), axis=1)

    # Return the result
    return final_df


def updated_disc_centered_columns(init_df: pd.DataFrame):
    updated_df = init_df.copy()

    new_cols = [c.replace('[V', '[D') for c in updated_df.columns]
    updated_df.columns = new_cols

    return updated_df


def keep_only_last_run(init_df: pd.DataFrame):
    result_df = init_df.reset_index()

    # Sort by the run, then only keep the last one (head of 1)
    result_df = result_df.sort_values('run').groupby(IDX).head(1)
    # Restore the index
    result_df.set_index(IDX, inplace=True)
    return result_df


def drop_angle_metrics(init_df: pd.DataFrame):
    # Drop angle metrics; they were found to hinder ML models more than they helped
    good_cols = [c for c in init_df.columns if "angle" not in c]
    return init_df.loc[:, good_cols]


def drop_rare_imaging_modalities(init_df: pd.DataFrame):
    img_cols = ["orientation", "weight", "algorithm"]
    to_keep_dfs = [df for _, df in init_df.groupby(img_cols) if df.shape[0] > 10]
    return pd.concat(to_keep_dfs)


def main(glob_pattern: str, output: Path, root_dir: Path, per_slice: bool, disc_centered: bool):
    # Identify all the files which match the glob pattern
    files_to_stack = list(root_dir.glob(glob_pattern))
    if len(files_to_stack) < 1:
        raise ValueError(f"No files matching the provided glob pattern within directory '{root_dir.resolve()}' exist!")

    # Load them all into Pandas
    sub_dfs = [pd.read_csv(x) for x in files_to_stack]

    # Stack them all into one "full" dataframe
    full_df = pd.concat(sub_dfs)

    # Clean the result to make it easier to work with
    full_df = clean_mri_data(full_df)

    # Process each patient's data on either a per-label basis (if vertebral/disc focused) or full spine (if per-slice focused)
    if per_slice:
        full_df = calc_perslice_stats(full_df)
    else:
        full_df = pivot_vertlabels(full_df)
        # if these "vertebral" metrics are actually disc-centered, denote as such
        if disc_centered:
            full_df = updated_disc_centered_columns(full_df)

    # Keep only the last run of all sequences
    full_df = keep_only_last_run(full_df)

    # Drop angle metrics, as they poison ML models (based on preliminary testing)
    full_df = drop_angle_metrics(full_df)

    # Drop imaging modalities which are rare (fewer than 10 samples)
    full_df = drop_rare_imaging_modalities(full_df)

    # Save the result
    if '.tsv' != output.name[-4:]:
        output = str(output) + ".tsv"
    full_df.to_csv(output, sep='\t')


if __name__ == '__main__':
    parser = get_parser()

    argvs = parser.parse_args().__dict__

    main(**argvs)
