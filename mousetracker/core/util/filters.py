from scipy.signal import butter, filtfilt


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
