"""
Detection and Analysis of eyes in video frames.
"""
import cv2
import numpy as np
import attr
from attr.validators import instance_of
import pandas as pd
import math
from mousetracker.core.util.detect_peaks import detect_peaks


@attr.s(frozen=True)
class EyeStats:
    """
    Modeled eye information.
    :param center: The tuple (x,y) representing the center of the eye, in pixels, from the top left corner.
    :param size: The tuple  (major, minor) representing the two axes of an ellipse that is fit to the eye contour.
    :param angle: The angle, in degrees, representing the orientation of the major axis of the eye relative to the x axis.
    :param fitted_area: The computed area of the fitted ellipse, in  pixels^2.
    :param contour_area: The raw area of the contour of the eye, in pixels^2. 
    """
    center_x = attr.ib(default=None)
    center_y = attr.ib(default=None)
    minor_axis = attr.ib(default=None)
    major_axis = attr.ib(default=None)
    angle = attr.ib(default=None)
    fitted_area = attr.ib(default=None)
    contour_area = attr.ib(default=None)


def find_blinks(series: pd.Series, min_dist: int = 120, std_num:float=2.5) -> np.ndarray:
    """find blinks (rapid eye closing events)"""
    temp = series.copy()
    # restrict search to only those peaks between 0 and `std_num` number of standard deviations from the mean.
    threshold = temp.mean() - std_num*temp.std()
    temp.loc[temp > threshold] = threshold
    return detect_peaks(temp, mpd=min_dist, valley=True)


def __num_samples_for_duration(dur_msec: float, fs: int = 240):
    """returns an always-even sample length that covers the given duration"""
    dur_sec = dur_msec / 1000.0
    n = math.floor(dur_sec * fs)
    if n % 2 == 0:
        return n
    else:
        return n + 1


def window(series: pd.Series, center_idx: int, timedur: float) -> pd.Series:
    nsamples = __num_samples_for_duration(timedur)
    start = center_idx - (nsamples // 2)
    stop = center_idx + (nsamples // 2)
    return series.iloc[start:stop]
    # return np.arange(start, stop), series.iloc[start:stop].as_matrix()

def overlay_windows(windowdf:pd.DataFrame) -> pd.DataFrame:
    # df = pd.DataFrame()
    # for colname, series in windowdf.iteritems():
    #     df[colname] = series.copy().reset_index(drop=True)
    # print(df.head())
    # return df
    return pd.DataFrame({n: v.reset_index(drop=True) for n,v in windowdf.iteritems()}).apply(lambda x: pd.Series(x.dropna().values))


def make_windows(series: pd.Series, duration_ms: float, show=False) -> [pd.DataFrame]:
    if show:
        import matplotlib.pyplot as plt
        plt.plot(series)
        plt.plot(series[find_blinks(series)], 'r^')
        plt.xlabel('sample index')
        plt.ylabel('scaled eye area')
        plt.legend(('eye area', 'blink events'))
    df = pd.DataFrame({f'blink_{i}': window(series, blink, duration_ms)
                       for i, blink in enumerate(find_blinks(series))})
    return df
    # return [window(series, blink, duration_ms) for blink in find_blinks(series, percent_closed_threshold=blink_threshold)]


def compute_areas(frame) -> EyeStats:
    """
    Compute the contour and fitted ellipse areas for the largest contour in the frame, which we assume represents the eye.
    :param frame: an extracted video frame.
    :return: A class containing measurement results.
    """
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    output_grey = _red_mask(frame_hsv=frame_hsv)
    thresh1 = _threshold_frame(output_grey)
    closing = _morph_and_smooth(thresh1)
    return _contour_to_ellipse(closing)


def _contour_to_ellipse(opened):
    """
    Find the ellipse which most closely fits the largest contour in the frame.
    :param opened: an extracted and processed video frame.
    :return: A class containing measurement results.  If no contours are present in the frame, return an empty class.
    """
    _, contours, _ = cv2.findContours(opened, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    try:
        largest_contour = max(contours, key=cv2.contourArea)
        center, size, angle = cv2.fitEllipse(largest_contour)
        fitted_area = np.pi * (size[0] / 2) * (size[1] / 2)
        return EyeStats(center_x=center[0],
                        center_y=center[1],
                        minor_axis=size[0],
                        major_axis=size[1],
                        angle=angle,
                        fitted_area=fitted_area,
                        contour_area=cv2.contourArea(largest_contour)
                        )
    except ValueError:
        return EyeStats()


def _morph_and_smooth(thresh1):
    """
    Smooth a thresholded frame's contours via erosion and dilation.  See http://docs.opencv.org/trunk/d9/d61/tutorial_py_morphological_ops.html
    :param thresh1: A thresholded frame.
    :return: a smoothed frame.
    """
    # the value of 3 is chosen by trial-and-error to produce the best results
    kernel = np.ones((3, 3), np.uint8)
    # square image kernel used for erosion
    erosion = cv2.erode(thresh1, kernel, iterations=2)
    # refines all edges in the binary image

    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE,
                               kernel)  # this is for further removing small noises and holes in the image
    # todo: improve this to join large blobs (in case of eyebrow occlusion)
    return closing


def _threshold_frame(output_grey):
    """
    Threshold the values of a frame according to their hue
    :param output_grey:  A greyscale intensity frame.
    :return: a thresholded frame.
    """
    ret, thresh1 = cv2.threshold(output_grey, 150, 255,
                                 cv2.THRESH_OTSU)
    # __show_debug_image('thresholded', thresh1)
    return thresh1


def _red_mask(frame_hsv):
    """
    Extract the red channel from a frame
    :param frame_hsv: A frame in HSV format
    :return: a greyscale frame containing non-null values only where red pixels were present in the original.
    """
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(frame_hsv, lower_red, upper_red)
    lower_red1 = np.array([170, 50, 50])
    upper_red1 = np.array([180, 255, 255])
    mask1 = cv2.inRange(frame_hsv, lower_red1, upper_red1)
    mask = mask0 + mask1
    output_img = frame_hsv.copy()
    output_img[np.where(mask == 0)] = 0

    return cv2.cvtColor(output_img, cv2.COLOR_BGR2GRAY)


if __name__ == "__main__":
    this_frame = cv2.imread('first.png')
    compute_areas(this_frame)
