#!/bin/bash
# Repurpose FreeSurfer commands to create a ribbon of superficial white matter (rather than cortical grey matter)
# This script assumes that FreeSurfer's basic 'recon-all' pipeline has already been run https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all
# Note - this takes hours!

# input directory where freesurfer processing is (no trailing /)
freesurferDir=$1

# set hemispheres to loop over (left = lh, right = rh)
hemis=(lh rh)

# extract subject ID from the freesurfer directory (needed for last command)
fsSubjID=`basename ${freesurferDir}`

for ihemi in ${hemis[@]}; do
  mris_expand ${freesurferDir}/surf/${ihemi}.white -2 ${freesurferDir}/surf/${ihemi}.swm-2mm-surf
done

# fill in voxels between the GM/WM boundary to -2mm below the GM/WM boundary (what we created above) - this gives us the SWM ribbon
# the pial surface is now the white surface, the white surface is now the -2mm SWM boundary (this is the main repurposing)
mris_volmask --surf_pial white --surf_white swm-2mm-surf --out_root swm-ribbon --save_ribbon --save_distance --sd ${isess}/anat/ ${fsSubjID}
