# MOOP Analysis

This step runs MOOP for all combinations of study, model, and data configurations. Given the sheer number of permutations, we elected to use SLURM to mediate this process; these are the `.sl` in this folder.

If you have access to an SLURM-managed HPC cluster, you can run each with an `sbatch` command. You may need to edit the variable declarations at the top of each script to point the script to the right places, but otherwise it should handle itself:

```bash
sbatch run_clinical_analysis.sl
```

If you cannot run these scripts on SLURM, you can uncomment the following code-block to make it act as a bash script instead:

```bash
## Un-comment the statement below to take the first command line parameter as the task ID. ##
#SLURM_ARRAY_TASK_ID=$1
```

Once this is done, you can run each job in series with the following command, replacing (or setting) `$ARRAY_MAX` to the larger number specified in the SLURM header's `#SBATCH --array` range:

```angular2html
for i in $(seq 0 $ARRAY_MAX); do run_clinical_analysis.sh $i ; done
```

A few notes if you run into problems:

* The scripts were written under the assumption that they are called from this directory, and that all the prior step was run with default output locations. If this is not the case, you may need to change the variable stack within the `.sl` scripts to reflect this.
* If you added custom datasets, model configurations, or other study configurations, the `N_` variables, range for the `#SBATCH --array` header, and the value of `$ARRAY_MAX` (if doing the workaround mentioned prior) will need to be updated to reflect this for each `.sl` script.
