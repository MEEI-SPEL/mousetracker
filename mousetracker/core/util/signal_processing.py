from scipy.signal import butter, filtfilt, welch
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt


def lowpass(data, fs, cutoff=25, order=5):
    """
    A lowpass, zero-phase butterworth filter
    :param data: array-like; the data to be filtered.
    :param fs:  data sampling frequency, in hz
    :param cutoff: the highest frequency to preserve, in hz (default: 25)
    :param order: butterworth filter order (default: 5)
    :return: 
    """
    b, a = butter(order, cutoff / (fs / 2), 'low')
    return filtfilt(b, a, data)


def nearest_idx(arr, val):
    """ Get the index of an array closest to the given scalar value"""
    return (np.abs(arr - val)).argmin()


def fftspectrum(y, Fs):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    """
    n = len(y)
    T = 1.00 / Fs
    x = np.linspace(0.0, n * T, n)
    yf = fft(y)
    xf = np.linspace(0.0, 1.0 / (2.0 * T), n // 2)
    return xf, yf, n


def plot_fft_around(xf, yf, n, start_freq=1, stop_freq=30):
    """ plot the single-sided amplitude spectrum of a fft around bounds"""
    start = nearest_idx(xf, start_freq)
    stop = nearest_idx(xf, stop_freq)
    plt.plot(xf[start:stop], 2.0 / n * np.abs(yf[start:stop]))  # n//2]))
    plt.xlabel('Frequency, Hz')
    plt.ylabel('|Y(z)|')
    plt.title('Frequency Spectrum')


def plot_psd(y, fs, start_freq=0, stop_freq=30):
    f, Pxx_den = welch(y, fs, nperseg=1024)
    plt.semilogy(f, Pxx_den)
    plt.xlim([start_freq, stop_freq])
    plt.xlabel('Frequency, Hz')
    plt.ylabel('PSD [V**2/Hz]')
    plt.title('Power Spectrum')
