# %% VERSION
# ALPHA: first testing version
#   Funguje pro mřížku 1200 (1), pro mřížku 1800 (2) chybí referenční pixelové hodnoty pásů. (row 90,91), (userInput, row 53)
#   Má problém s fitováním doubletu na kraji spektra. (dataProcessing, row 57)
#   Neprobíhají kontroly nahraných souborů!
print("!!! verze ALPHA: první testovací verze")
print("Kalibrace pouze pro mřížku 1200 vrypů/mm a pro soubory CSV.")
print("Výstup ve formátu TXT.")
print("-" * 60)

# %% IMPORT

from components.userInput import (
    loadDataCSV,
    loadReferencePeaks,
    showFiles,
    userInputLoadAllFiles,
    userInputLoadOneFile,
    userInputCalibSpectrum,
    userInputGrid,
    userInputSaveSeparateFiles,
)
from components.dataProcessing import calibrateData, interpolateData, interpolateAxis
from components.output import outputSeparateFiles, outputOneFile
from numpy import asarray
import sys
import os

# %% INPUT

calibrateAllFiles = userInputLoadAllFiles()


if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    dataDirectory = "."
    bundleDirectory = os.path.abspath(os.path.dirname(__file__))
else:
    dataDirectory = "Data"
    bundleDirectory = "."

availableFiles = showFiles(dataDirectory)
availableFiles = [file for file in availableFiles if file.endswith(".csv")]
dataFiles, calibFiles = [], []

if calibrateAllFiles:
    for file in availableFiles:
        if file.startswith("k_") or file.startswith("kalib"):
            calibFiles.append(file)
        else:
            dataFiles.append(file)
    oneCalibSpectrum = userInputCalibSpectrum()
else:
    fileName = userInputLoadOneFile()
    dataFiles = [
        dataFile for dataFile in availableFiles if dataFile.split(".")[0] == fileName
    ]
    calibFiles = [
        calibFile
        for calibFile in availableFiles
        if calibFile.split(".")[0] in ["kalib", f"k_{fileName}"]
    ]
    if len(calibFiles) != 0:
        calibFiles = [calibFiles[0]]
    oneCalibSpectrum = True

grid = userInputGrid()

if calibrateAllFiles:
    saveSeparateFiles = userInputSaveSeparateFiles()
else:
    saveSeparateFiles = True

# %% DATA PREPARATION FOR CALIBRATION

calibrationSpectra = []
for calibFile in calibFiles:
    spectrum = loadDataCSV(dataDirectory, calibFile)
    calibrationSpectra.append(spectrum.T)
calibrationSpectra = asarray(calibrationSpectra)

dataSpectra = []
for file in dataFiles:
    spectrum = loadDataCSV(dataDirectory, file)
    dataSpectra.append(spectrum.T[1])
dataSpectra = asarray(dataSpectra)

if grid == 1:
    referencePath = "referenceValues/toluenReference1200.csv"
else:
    print("Zatím funguje pouze mřížka 1200 (1).")
    referencePath = "referenceValues/toluenReference1200.csv"
referencePath = os.path.join(bundleDirectory, referencePath)
referencePeaks = loadReferencePeaks(referencePath)


# %% CALIBRATION

calibratedAxes = []
for calibrationSpectrum in calibrationSpectra:
    calibratedAxis = calibrateData(calibrationSpectrum, referencePeaks)
    calibratedAxes.append(calibratedAxis)
calibratedAxes = asarray(calibratedAxes)


# %% DATA PREPARATION FOR OUTPUT

finalAxes, finalSpectra = [], []

for axis, spectrum in zip(
    calibratedAxes if not oneCalibSpectrum else [calibratedAxes[0]] * len(dataSpectra),
    dataSpectra,
):
    newAxis, newSpectrum = interpolateData(axis, spectrum)
    finalAxes.append(newAxis)
    finalSpectra.append(newSpectrum)

if oneCalibSpectrum:
    finalAxes = [interpolateAxis(calibratedAxes[0])]

finalAxes = asarray(finalAxes)
finalSpectra = asarray(finalSpectra)


# %% OUTPUT

folderName = "CalibratedSpectra"
if not os.path.exists(folderName):
    os.makedirs(folderName)

if saveSeparateFiles or not oneCalibSpectrum:
    outputSeparateFiles(
        finalAxes, finalSpectra, dataFiles, folderName, oneCalibSpectrum
    )
else:
    outputOneFile(finalAxes, finalSpectra, folderName)

# END
input("Ukončit program?")
