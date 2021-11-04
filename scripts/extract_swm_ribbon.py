import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import nibabel as nb
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.spatial import cKDTree

# get arguments
__description__ = '''
This script uses a SWM ribbon created beforehand (from WM surface to 2mm below), removes the midline and assigns region
of interest values based on nearest cortical neighbour.
Output is a cleaned SWM ribbon mask and SWM ribbon with region of interest values from the Desikan-Killiany atlas.

Author: Tom Veale
Email: tom.veale@ucl.ac.uk
'''

# collect inputs
parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                        description=__description__)

parser.add_argument('-swm', '--swm_ribbon',
                    help='Path to the swm-ribbon file generated using mris_expand and volmask. Must be NIFTI. '
                         'e.g. /path/to/freesurfer/mri/swm-ribbon.nii.gz')
parser.add_argument('-ctx', '--cortical_ribbon',
                    help='Path to the cortical ribbon file generated from standard FreeSurfer pipeline. Must be NIFTI. '
                         'e.g. /path/to/freesurfer/mri/ribbon.nii')
parser.add_argument('-aparc', '--parcellation',
                    help='Path to the aparc + aseg file with ROI labels generated from standard FreeSurfer pipeline. '
                         'Must be NIFTI. e.g. /path/to/freesurfer/mri/aparc.DKTatlas+aseg.nii.gz')

args = parser.parse_args()

# load files
swm = nb.load(args.swm_ribbon)
ctx = nb.load(args.cortical_ribbon)
aparc = nb.load(args.parcellation)

# get data arrays
aparc_data = aparc.get_fdata()
swm_data = swm.get_fdata()
ctx_data = ctx.get_fdata()

## Remove unwanted tissue from SWM and cortical masks
# only keep SWM ribbon (remove deep WM and binarise)
swm_data[(swm_data == 20) | (swm_data == 120)] = 0
swm_data[swm_data > 0] = 1

# select only cortex (remove all WM and binarise)
ctx_data[(ctx_data == 41) | (ctx_data == 2)] = 0
ctx_data[ctx_data > 0] = 1

## First part of cleaning - keep SWM voxels within dilated cortical mask
# set up empty nii to store dilated cortex
dilated_ctx = np.zeros(ctx_data.shape)

# dilate cortex by 5 voxels - this is to help clean midline
dilated_ctx = binary_dilation(ctx_data, iterations=5)

# keep SWM voxels that are within dilated cortical mask
cleaned_swm_data = np.zeros(swm_data.shape)
cleaned_swm_data[(swm_data == 1) & (dilated_ctx == 1)] = 1

# Extract voxel indices in the SWM and cortical regions
swm_voxels = np.argwhere(cleaned_swm_data == 1)
ctx_voxels = np.argwhere(ctx_data == 1)

## Assign ROI labels to SWM voxels
# create a KD tree with voxels from the cortex
ctx_tree = cKDTree(ctx_voxels)

# query the tree to find the voxels in the cortex closest to the SWM voxels
distances, ndx = ctx_tree.query(swm_voxels, k=1)

# create empty nii to store nearest voxels
nearest_nii = np.zeros(ctx_data.shape)

# assign nearest voxel indices (ndx from query above) to the empty nii with value of 1
nearest_nii[ctx_voxels[ndx][:,0], ctx_voxels[ndx][:,1], ctx_voxels[ndx][:,2]] = 1

# create empty swm voxels
swm_roi = np.zeros(cleaned_swm_data.shape)

# get aparc label values for the nearest voxels in the cortex
nearest_aparc = aparc_data[ctx_voxels[ndx][:,0], ctx_voxels[ndx][:,1], ctx_voxels[ndx][:,2]]

# assign these values to corresponding SWM voxels using coords in swm_voxels
swm_roi[swm_voxels[:,0], swm_voxels[:,1], swm_voxels[:,2]] = nearest_aparc

## Second part of cleaning SWM voxels
# keep voxels only associated with cortical ROIs (>= 1000 are cortex)
swm_roi[swm_roi < 1000] = 0

# remove non-cortical voxels from the swm ribbon mask too
cleaned_swm_data[swm_roi < 1000] = 0

## save ribbon and roi image
# write the cleaned SWM mask to file
swm_cleaned_fname = os.path.join(os.path.dirname(args.swm_ribbon),
                                 os.path.basename(args.swm_ribbon.split('.')[0])) + '_cleaned.nii.gz'
swm_cleaned_nifti = nb.Nifti1Image(cleaned_swm_data, swm.affine)
nb.save(swm_cleaned_nifti, swm_cleaned_fname)
print('Cleaned SWM ribbon saved to: ', swm_cleaned_fname)

# write the cleaned SWM regions to file
swm_roi_fname = os.path.join(os.path.dirname(args.swm_ribbon),
                             os.path.basename(args.swm_ribbon.split('.')[0])) + '_rois_cleaned.nii.gz'
swm_roi_nifti = nb.Nifti1Image(swm_roi, swm.affine)
nb.save(swm_roi_nifti, swm_roi_fname)
print('SWM ribbon ROIs saved to: ', swm_roi_fname)
