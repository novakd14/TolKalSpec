from scipy.signal import find_peaks, savgol_filter
from scipy.optimize import curve_fit
from numpy.polynomial import Polynomial
import numpy as np


def gaussian(x, a, b, c, d):
    return a * np.exp(-((x - b) ** 2) / (2 * c**2)) + d


def calibrateData(calibrationSpectrum, referencePeaks):
    pixels = calibrationSpectrum[0]
    intensities = calibrationSpectrum[1]

    secondDerivation = savgol_filter(intensities, 11, 2, 2) * (-1)

    minimalHeight = max(secondDerivation) * 0.02

    # nalezení pásů ve spektru
    peaks, _ = find_peaks(secondDerivation, minimalHeight)

    # zpřesnění pásů
    newPeaks = []
    for peak in peaks:
        newPeak = []

        # výběr intervalu podle druhé derivace
        index = peak
        while secondDerivation[index] > 0 and index > max(peak - 10, 0):
            index -= 1
            leftIndex = index

        index = peak
        while secondDerivation[index] > 0 and index < min(
            peak + 10, len(secondDerivation)
        ):
            index += 1
            rightIndex = index

        # vyřadí pásy s malým intervalem
        if rightIndex - leftIndex + 1 < 6:
            continue

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

        # fit pásu
        fit, cov = curve_fit(gaussian, pixels, intensities, initialParameters)

        # vyřadí pás, pokud pozice fitu vypadne z původního intervalu
        if (fit[1] < pixels[leftIndex] or fit[1] > pixels[rightIndex]) or (
            fit[2] < 1 or fit[2] > 8
        ):
            continue

        while False:
            # kontrola intenzity pásu vůči šumu pozadí
            noiseIntervalLeft = slice(max(leftIndex - 10, min(pixels)), leftIndex - 1)
            noiseIntervalRight = slice(
                rightIndex + 1, min(rightIndex + 10, max(pixels))
            )

            intervalSizeLeft = len(intensities[noiseIntervalLeft])
            if intervalSizeLeft > 5:
                averageLeft = np.average(intensities[noiseIntervalLeft])
                sigmaLeft = np.std(intensities[noiseIntervalLeft], ddof=1)
            print(averageLeft, sigmaLeft)

            intervalSizeRight = len(intensities[noiseIntervalRight])
            if intervalSizeRight > 5:
                averageRight = np.average(intensities[noiseIntervalRight])
                sigmaRight = np.std(intensities[noiseIntervalRight], ddof=1)
            print(averageRight, sigmaRight)

            if intervalSizeLeft < 5:
                average = averageRight
                sigma = sigmaRight
            elif intervalSizeRight < 5:
                average = averageLeft
                sigma = sigmaLeft
            elif averageLeft < averageRight:
                average = averageLeft
                sigma = sigmaLeft
            else:
                average = averageRight
                sigma = sigmaRight

            # vyřadí pás, pokud není dostatečně intenzivní oproti šumu
            if (intensities[peak] - average) / sigma < 5:
                print("Eliminated")
                continue
        newPeak.append(fit[1])
        newPeak.append(fit[0] + fit[3] - background)
        newPeaks.append(newPeak)
    newPeaks = np.asarray(newPeaks)

    # přiřazení pásů k vlnočtům
    minShift = referencePeaks[0][0] - newPeaks[0][0] - 100
    maxShift = referencePeaks[-1][0] - newPeaks[-1][0] + 100

    minSumDistance = -1
    for shift in np.arange(minShift, maxShift + 0.5, 0.5):
        nearestPeaks = []
        sumDistance = 0
        for peak, _ in newPeaks:
            minDistance = -1  # ještě zkusit najít lepší způsob
            for referencePeak, referenceWavelength in referencePeaks:
                distance = np.abs(peak + shift - referencePeak)
                if distance < minDistance or minDistance == -1:
                    minDistance = distance
                    nearestPeak = [peak, referenceWavelength, distance]
                else:
                    sumDistance += nearestPeak[2]
                    nearestPeaks.append(np.asarray(nearestPeak))
                    break
        if sumDistance < minSumDistance or minSumDistance == -1:
            minSumDistance = sumDistance
            bestShift = [shift, sumDistance, np.asarray(nearestPeaks)]

    # fit polynomem

    calibFunction = Polynomial.fit(bestShift[2].T[0], bestShift[2].T[1], 3)

    calibratedAxis = calibFunction(pixels)

    # RETURN
    return calibratedAxis


def interpolateData(axis, spectrum):
    newAxis = interpolateAxis(axis)
    newSpectrum = np.interp(newAxis, axis, spectrum)

    return [newAxis, newSpectrum]  # vrátit interpolované spektrum


def interpolateAxis(axis):
    newAxisMin = np.ceil(axis[0])
    newAxisMax = np.floor(axis[-1])
    newAxis = np.arange(newAxisMin, newAxisMax + 1, 1)

    return newAxis
