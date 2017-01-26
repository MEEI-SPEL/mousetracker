import numpy as np
import pandas as pd
import json
from collections import OrderedDict, namedtuple
import matplotlib.pyplot as plt

timedata = namedtuple("timedata", "frameid,mean_degrees,num_whiskers")


def test_serialized(pth: str):
    with open(pth, 'r') as _:
        whiskdat = json.load(_, object_pairs_hook=OrderedDict)
    timeseries = analyze_stack(whiskdat)
    plt.figure()
    timeseries.plot(x='frameid', y='mean_degrees')
    plt.show()


def analyze_stack(whiskdat: {}) -> pd.DataFrame:
    retval = []
    for frameID, frame in whiskdat.items():
        degrees = []
        for whiskerID, whisker in frame.items():
            thisx = whisker['x']['__ndarray__']
            thisy = whisker['y']['__ndarray__']
            degrees.append(compute_vector_angle(thisx, thisy))
        mean_degrees = np.mean(degrees)
        retval.append(timedata(frameid=int(frameID),
                               mean_degrees=mean_degrees,
                               num_whiskers=len(degrees)))
    return pd.DataFrame(retval).sort('frameid')


def compute_vector_angle(x: list, y: list) -> float:
    """
    Estimate the vector angle given by the parametric vectors x and y relative to the euclidian axis.
    :param x:
    :param y:
    :return:
    """
    # normalize
    x_end = x[-1] - x[0]
    y_end = y[-1] - y[0]
    retval = np.arctan(y_end / x_end)
    if not np.isnan(retval):
        return np.degrees(retval)
    else:
        raise ArithmeticError('error calculating whisker angle')
