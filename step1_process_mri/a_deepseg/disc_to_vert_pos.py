from argparse import ArgumentParser
from pathlib import Path

import nibabel as nib
import numpy as np

np.set_printoptions(precision=2, suppress=True)


def get_parser() -> ArgumentParser:
    argparser = ArgumentParser()

    argparser.add_argument(
        "-i", "--initial_disks", required=True, type=Path,
        help="The original disk position annotation file, in Nifti format"
    )

    argparser.add_argument(
        "-o", "--output_path", type=Path,
        help="Where to place the resulting naive vertebral annotations. "
             "If not specified, the file is placed in the same directory as the input file."
    )
    argparser.add_argument(
        "-n", "--name",
        help="The name of the output file. "
             "If not specified, it will be the input files name with '_discs' replaced with '_verts'"
    )

    return argparser


def main(initial_disks: Path, output_path: Path, name: str):
    # Let the user know what's going on
    print(f"Starting conversion for file '{initial_disks}'!")

    # Load the image data
    disk_img_ref = nib.load(initial_disks)
    disk_img = disk_img_ref.get_fdata()

    # Use Numpy to find the "marked" voxels
    disk_img_annots = np.array(np.where(disk_img != 0))

    # Sort them by their SCT assigned labels
    disk_labels = disk_img[disk_img_annots[0, :], disk_img_annots[1, :], disk_img_annots[2, :]]
    sort_order = np.argsort(disk_labels)
    disk_img_annots = disk_img_annots[: , sort_order]

    # Generate a new "blank" image to insert our "vertebrae" annotations into
    vert_img = np.zeros(np.shape(disk_img))

    # "Walk" through pairs of annotated positions and get their mean position
    n_annots = np.shape(disk_img_annots)[1]
    for i in range(n_annots-1):
        p1 = disk_img_annots[:, i]
        p2 = disk_img_annots[:, i+1]
        new_p = np.ceil(np.mean([p1, p2], axis=0)).astype('int16')
        vert_img[new_p[0], new_p[1], new_p[2]] = i+1

    # Create our new annotation image!
    vert_img_ref = nib.Nifti1Image(vert_img, affine=disk_img_ref.affine)

    # Save it to a file
    if not output_path:
        output_path = initial_disks.parent
    if not output_path.exists():
        output_path.mkdir(parents=True)
    if not name:
        name = initial_disks.name.replace('_discs', '_verts')
        print(f"New name: '{name}'")

    output_file = output_path / name

    vert_img_ref.to_filename(output_file)


if __name__ == '__main__':
    parser = get_parser()
    argvs = parser.parse_args().__dict__

    main(**argvs)
