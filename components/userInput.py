from numpy import loadtxt
import os


def userInputLoadAllFiles():
    # Kalibrovat všechna spektra ve složce?
    while True:
        useAllFiles = input("Kalibrovat všechna spektra? Ano (y), Ne (n)").lower()
        if useAllFiles in ["y", "n", ""]:
            match useAllFiles:
                case "n":
                    useAllFiles = False
                case _:
                    useAllFiles = True
            break

    print(f"Kalibrovat všechna spektra: {useAllFiles}")

    return useAllFiles


def userInputLoadOneFile():
    # Kalibrovat všechna spektra ve složce?
    fileName = input("Zadejte název souboru (bez přípony):")

    print(f"Nahrávám soubor se jménem: {fileName}")

    return fileName


def userInputCalibSpectrum():
    # Jedno kalibrační spektrum pro všechny spektra
    while True:
        oneCalibSpectrum = input("Jedno kalibrační spektrum? Ano (y), Ne (n)").lower()
        if oneCalibSpectrum in ["y", "n", ""]:
            match oneCalibSpectrum:
                case "n":
                    oneCalibSpectrum = False
                case _:
                    oneCalibSpectrum = True
            break

    print(f"Dodáno pouze jedno kalibrační spektrum: {oneCalibSpectrum}")

    return oneCalibSpectrum


def userInputGrid():
    # Jaká byla použita mřížka?
    while True:
        grid = input("Zvol použitou mřížku: 1200 (1), 1800 (2)")
        if grid in ["1", "2", ""]:
            if grid in ["2", ""]:
                grid = 1
            else:
                grid = int(grid)
            break

    print(f"Zvolena mřížka: {grid}")

    return grid


def userInputSaveSeparateFiles():
    while True:
        saveSeparateFiles = input(
            "Uložit každé spektrum do samostatného souboru? Ano (y), Ne (n)"
        ).lower()
        if saveSeparateFiles in ["y", "n", ""]:
            match saveSeparateFiles:
                case "n":
                    saveSeparateFiles = False
                case _:
                    saveSeparateFiles = True
            break

    print(f"Uložit každé spektrum do samostatného souboru: {saveSeparateFiles}")

    return saveSeparateFiles


def showFiles(path="."):
    return os.listdir(path)


def loadDataCSV(directory, file: str):
    file_path = f"{directory}/{file}"
    return loadtxt(file_path, usecols=(3, 4))


def loadDataSPE(directory, file: str):
    print("Ještě nefunguje!")
    return []


def loadReferencePeaks(referencePath):
    return loadtxt(referencePath, usecols=(0, 1))
