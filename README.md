# Extracting a Superficial White Matter Ribbon

This repository gives an example of extracting a superficial white matter segmentation using commands from FreeSurfer and python.

The main notebook goes through my process for extracting the superficial white matter ribbon and associating them with regions of interest in the overlying cortex `swm_ribbons_rois.ipynb`

The files in `data/` are used to reproduce the work explored in `swm_ribbons_rois.ipynb`. Permission to use this MRI data has been given and also defaced using FreeSurfer's `mri_deface`.

The files in `scripts/` are for creating the original swm ribbon when repurposing FreeSurfer commands `create_swm_ribbon.sh` and `extract_swm_ribbon.py` puts the work from the jupyter notebook into one command that can be called from the command line.

Note: A caveat is that 2mm below the GM/WM boundary is an approximation of SWM's thickness. The thickness of SWM is likely to vary between regions of the brain.
