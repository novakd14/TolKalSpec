import os


def outputSeparateFiles(axes, spectra, files, folderName, oneCalibSpectrum):
    for file, axis, spectrum in zip(
        files, axes if not oneCalibSpectrum else [axes[0]] * len(files), spectra
    ):
        fileName, _ = os.path.splitext(file)
        newFile = f"{folderName}/{fileName}.txt"

        with open(newFile, "w") as outputFile:
            for point, row in zip(axis, spectrum):
                outputFile.write(f"{point} {row}\n")
        print(f"Data has been written to {newFile}.")


def outputOneFile(axes, spectra, folderName):
    newFile = f"{folderName}/calibratedSpectra.txt"
    with open(newFile, "w") as outputFile:
        for point, row in zip(axes[0], spectra.T):
            outputFile.write(f"{point}")
            for cell in row:
                outputFile.write(f" {cell}")
            outputFile.write(f"\n")

    print(f"Data has been written to {newFile}.")
