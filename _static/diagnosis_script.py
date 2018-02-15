""" Script to run diagnostic analysis on FMRI run

The FMRI 'run' is a continuous collection of one or more 3D volumes.
A run is usually stored as a 4D NIfTI image.
Fill in the code necessary under the comments below.
"""

# import standard libraries here


"""
* Load "ds114_sub009.nii" as an image object
* Load the image data from the image
* Drop the first four volumes, as we know these are outliers
"""

"""
Use your vol_std function to get the volume standard deviation values
for the remaining 169 volumes. Save these values to a text file
called 'vol_std_values.txt'.
"""

"""
Use the iqr_outlier detection routine to get indices of outlier volumes.
Save these indices to a text file called 'vol_std_outliers.txt'.
"""

"""
Plot all these on the same plot:
* The volume standard deviation values;
* The outlier points from the std values marked with an 'o' marker;
* A horizontal dashed line at the lower IRQ threshold;
* A horizontal dashed line at the higher IRQ threshold;

Save the figure to the current directory as ``vol_std.png``.
"""

"""
Next calculate and plot the RMS difference values:
* Calculate the RMS difference values for the image data;
* Use the ``iqr_outlier`` function to return indices of possible
  outliers in this RMS difference vector;

On the same plot, plot the following:
* The RMS vector;
* The identified outlier points marked with an `o` marker;
* A horizontal dashed line at the lower IRQ threshold;
* A horizontal dashed line at the higher IRQ threshold;

Save this plot as ``vol_rms_outliers.png``
"""
