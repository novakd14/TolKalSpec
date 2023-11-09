# TolKalSpec

Calibration of Raman spectra by reference toluene spectrum.

# Input data

Input spectra in CSV format (columns separated by comma). Using fourth and fifth column for pixel values and intensities.

# Calibration

Peaks are find from second derivation of spectrum and fitted with Gaussian function for precise position. Assigning of peaks to reference pixel positions is done by computing distance (dist) from closest reference peak for each peak found and computing the agreement
value as 10/(1+dist\*\*2). Highest sum of agreement value from each peak marks the best shift for assigning wavenumbers to peaks. Assigned peaks are then fitted with cubic polynom. Calibrated spectra are then lineary interpolated so the wavenumbers are equidistant with step of 1 cm\*\*(-1).

# Output

Calibrated spectra are outputted in TXT format with columns separated by white space. For single calibration spectrum there is option to ouput data in one file with first column as wavenumbers and the remaining columns as calibrated spectra.

# To-Do List

- Check peaks assignment (quality of fit, agreement)
- Exceptions handeling
- Faster loading
- Smaller EXE files
- Add possible SPE file input
