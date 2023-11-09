from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial
import numpy as np


def gaussian(x, a, b, c, d):
    return a * np.exp(-((x - b) ** 2) / (2 * c**2)) + d


def calibrateData(calibrationSpectrum, referencePeaks):
    pixels = [int(pixel) for pixel in calibrationSpectrum[0]]
    axis = calibrationSpectrum[0]
    intensities = calibrationSpectrum[1]

    # Find peaks in calibration spectrum
    secondDerivation = savgol_filter(intensities, 11, 2, 2) * (-1)
    peaks, _ = find_peaks(secondDerivation)

    # Removing of non-relevant peaks and determining precise position of peaks
    newPeaks = []
    for peak in peaks:
        newPeak = []

        # Peak interval determination based on second derivation
        index = peak
        leftIndex = peak
        while secondDerivation[index] > 0 and index > max(peak - 10, 0):
            index -= 1
            leftIndex = index

        index = peak
        rightIndex = peak
        while secondDerivation[index] > 0 and index < min(
            peak + 10, len(secondDerivation)
        ):
            index += 1
            rightIndex = index

        # Discard peaks with insufficient interval
        if rightIndex - leftIndex + 1 < 6:
            continue

        # Control of peak intensity against backgroun noise
        noiseIntervalLeft = slice(max(leftIndex - 10, min(pixels)), leftIndex - 1)
        noiseIntervalRight = slice(rightIndex + 1, min(rightIndex + 10, max(pixels)))

        intervalSizeLeft = len(intensities[noiseIntervalLeft])
        if intervalSizeLeft > 5:
            averageLeft = np.average(intensities[noiseIntervalLeft])
            sigmaLeft = np.std(intensities[noiseIntervalLeft], ddof=1)

        intervalSizeRight = len(intensities[noiseIntervalRight])
        if intervalSizeRight > 5:
            averageRight = np.average(intensities[noiseIntervalRight])
            sigmaRight = np.std(intensities[noiseIntervalRight], ddof=1)

        if intervalSizeLeft <= 5:
            average = averageRight
            sigma = sigmaRight
        elif intervalSizeRight <= 5:
            average = averageLeft
            sigma = sigmaLeft
        elif averageLeft < averageRight:
            average = averageLeft
            sigma = sigmaLeft
        else:
            average = averageRight
            sigma = sigmaRight

        # Discard peaks with insufficient intensity
        if (intensities[peak] - average) / sigma < 5:
            continue

        # Initial parameters fro fit of peak
        backgroundInterval = slice(
            max(peak - 30, min(pixels)), min(peak + 30, max(pixels))
        )
        background = min(intensities[backgroundInterval])
        initialParameters = [
            intensities[peak] - background,  # intensity
            pixels[peak],  # position
            (pixels[rightIndex] - pixels[leftIndex]) / 3,  # width
            background,  # background
        ]

        # Fit of peak
        fitInterval = slice(leftIndex, rightIndex)
        fit, _ = curve_fit(
            gaussian,
            pixels[fitInterval],
            intensities[fitInterval],
            initialParameters,
        )

        # Discrad the peak if its position falls out of the original interval
        if (fit[1] < pixels[leftIndex] or fit[1] > pixels[rightIndex]) or (
            fit[2] < 1 or fit[2] > 8
        ):
            continue

        newPeak.append(fit[1])
        newPeak.append(fit[0] + fit[3] - background)
        newPeaks.append(newPeak)
    newPeaks = np.asarray(newPeaks)

    # Assigning of wavenumbers to peaks
    minShift = referencePeaks[0][0] - newPeaks[0][0] - 100
    maxShift = referencePeaks[-1][0] - newPeaks[-1][0] + 100

    maxShoda = -1
    for shift in np.arange(minShift, maxShift + 0.5, 0.5):
        nearestPeaks = []
        shoda = 0
        lastWeight = 1
        for peak, _ in newPeaks:
            minDistance = -1  # ještě zkusit najít lepší způsob!!!
            for referencePeak, referenceWavelength in referencePeaks:
                distance = np.abs(peak + shift - referencePeak)
                if distance < minDistance or minDistance == -1:
                    minDistance = distance
                    nearestPeak = [peak, referenceWavelength, distance]
                else:
                    weight = 10 / (1 + nearestPeak[2] ** 2)
                    shoda += weight * lastWeight
                    lastWeight = weight
                    nearestPeaks.append(nearestPeak)
                    break
        if shoda > maxShoda or maxShoda == -1:
            maxShoda = shoda
            bestShiftValues = {
                "shift": shift,
                "shoda": shoda,
                "assignedPeaks": nearestPeaks,
            }

    # Duplicate wavenumber assignment check
    assignedPeaks = bestShiftValues["assignedPeaks"]
    i = 0
    while i < len(assignedPeaks) - 1:
        if assignedPeaks[i][1] == assignedPeaks[i + 1][1]:
            if assignedPeaks[i][2] <= assignedPeaks[i + 1][2]:
                del assignedPeaks[i + 1]
            else:
                del assignedPeaks[i]
        else:
            i += 1
    pixelPeaks, assignedPeaks, _ = np.asarray(assignedPeaks).T

    # Fit of assigned wavenumbers by a polynomyial
    calibFunction, [residuals, _, _, _] = Polynomial.fit(
        pixelPeaks, assignedPeaks, 3, full=True
    )
    calibratedAxis = calibFunction(axis)

    # Goodness of fit
    totalSumSquares = ((assignedPeaks - np.mean(assignedPeaks)) ** 2).sum()
    rSquared = 1 - residuals / totalSumSquares

    # RETURN
    return (calibratedAxis, bestShiftValues["shift"], rSquared)


def interpolateData(axis, spectrum):
    newAxis = interpolateAxis(axis)
    newSpectrum = np.interp(newAxis, axis, spectrum)

    return [newAxis, newSpectrum]


def interpolateAxis(axis):
    newAxisMin = np.ceil(axis[0])
    newAxisMax = np.floor(axis[-1])
    newAxis = np.arange(newAxisMin, newAxisMax + 1, 1)

    return newAxis


def getPeakInterval(peak, secondDerivation):
    index = peak
    leftIndex = peak
    while secondDerivation[index] > 0 and index > max(peak - 10, 0):
        index -= 1
        leftIndex = index

    index = peak
    rightIndex = peak
    while secondDerivation[index] > 0 and index < min(peak + 10, len(secondDerivation)):
        index += 1
        rightIndex = index

    return (leftIndex, rightIndex)
