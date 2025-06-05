"""
Analogous to SCT's "sct_run_batch", running a script repeatedly on a set of patient records.
However, this script differs in a few key ways required to our analysis:
    * Runs the desired script per-MRI, rather than per-subject
    * No configuration; the provided script must be self-contained!
    * The script handles output management (we generate output folders in a hierarchical manner for ease of management)
"""
import multiprocessing as mp
import subprocess
import timeit

from argparse import ArgumentParser
from itertools import repeat
from pathlib import Path


def valid_path(arg: str):
    """
    Checks an input path to make sure it is a valid input directory
    :param arg: The argument to check
    :return: The properly typed argument, given it passes all checks
    """
    p = Path(arg)
    if not p.exists():
        print(f"Path '{p}' does not exist; did you perhaps make a typo?")
        raise ValueError()
    return p


def run_script(script_path: Path, mri_file: Path, out_path: Path, sct_path: Path, log_name: str):
    # Interpret the file name to extract needed parameters
    fname = mri_file.name.split('.')[0]
    subject = fname.split('_')[0]

    # Generate the directory the output will be placed within
    dest_path = out_path / subject
    dest_path /= fname
    dest_path.mkdir(exist_ok=True, parents=True)

    # (Re)Generate a logging file to track this thread's progress
    log_file = dest_path / log_name
    if log_file.exists():
        log_file.unlink()
    log_file.touch()

    # Run the script
    subprocess.run(f"{script_path} {mri_file} {dest_path} {sct_path} >> {log_file} 2>&1", shell=True)


def build_parser():
    # Build an argument parser to parse arguments from the command line
    parser = ArgumentParser(
        prog="SCT Batch Processing",
        description="Processes all files in a designated directory with a standardized preparation procedure."
    )
    parser.add_argument(
        '-i', '--input', type=valid_path, required=True,
        help="The top-level directory containing all files to process"
    )
    parser.add_argument(
        '-s', '--script', type=valid_path, required=True,
        help="The script you want to run for each MRI sequence contained within the input directory."
    )
    parser.add_argument(
        '-o', '--output', type=valid_path, required=True,
        help="The directory all outputs of this process should be placed within. Must exist before this script is run!"
    )
    parser.add_argument(
        '-t', '--threads', type=int, default=1,
        help="Number of threads to use in this process."
    )
    parser.add_argument(
        '-sct', '--sct_path', type=valid_path, required=True,
        help="The directory containing all SCT scripts. "
             "This can be found easily using 'which {sct_command}' on a console."
    )
    parser.add_argument(
        '-l', '--log_file', type=str, required=True,
        help="The name of the log file that will be generated for each file. Include the extension you want!"
    )

    return parser


if __name__ == "__main__":
    # Parse the CLI arguments provided by the user
    argparser = build_parser()
    argvs = argparser.parse_args()

    # Begin timing
    start = timeit.default_timer()

    # Process the files, in parallel if multiple threads are available
    with mp.Pool(argvs.threads) as p:
        p.starmap(run_script, zip(
            repeat(argvs.script),
            argvs.input.rglob("anat/*.nii.gz"),
            repeat(argvs.output),
            repeat(argvs.sct_path),
            repeat(argvs.log_file)
        ))

    # End timing
    end = timeit.default_timer()

    print(f"Process took {end-start} seconds")
