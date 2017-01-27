import numpy as np
import pandas as pd
import json
from os import path, makedirs
from datetime import datetime
from collections import OrderedDict, namedtuple
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import seaborn as sns
from .util.filters import butter_bandpass_filter
plt.style.use('fivethirtyeight')
matplotlib.use('PDF')
sns.set(color_codes=True)

timedata = namedtuple("timedata", "frameid,mean_degrees,num_whiskers,stderr")


def test_serialized(pth: str, params:dict):
    with open(pth, 'r') as _:
        whiskdat = json.load(_, object_pairs_hook=OrderedDict)
    timeseries = analyze_stack(whiskdat, params)
    save(path.join(path.expanduser('~'), 'Documents', 'whisk_analysis_data'), timeseries)


def save(rootdirpath: str, df: pd.DataFrame):
    now = datetime.now().strftime('%d%b%y-%H%M%S')
    dirpath = path.join(rootdirpath, now)
    if not path.exists(dirpath):
        makedirs(dirpath, exist_ok=True)
    df.to_csv(path.join(dirpath, df.name + ".csv"), index=False)
    with PdfPages(filename=path.join(dirpath, df.name + ".pdf")) as pdf:
        ax = df.plot.line(x='frameid', y='mean_degrees', yerr='stderr')
        fig = ax.get_figure()
        fig.dpi = 400
        fig.figsize = (8.5, 11)
        pdf.savefig(fig)


def analyze_stack(whiskdat: {}, params:dict) -> pd.DataFrame:
    retval = []
    for frameID, frame in whiskdat.items():
        degrees = []
        for whiskerID, whisker in frame.items():
            thisx = whisker['x']['__ndarray__']
            thisy = whisker['y']['__ndarray__']
            degrees.append(compute_vector_angle(thisx, thisy))
        mean_degrees = np.mean(degrees)
        stderr = np.std(degrees) / np.sqrt(len(degrees))
        retval.append(timedata(frameid=int(frameID),
                               mean_degrees=mean_degrees,
                               num_whiskers=len(degrees),
                               stderr=stderr))

    retval = pd.DataFrame(retval).sort('frameid')
    low = 0.1
    high = 50
    fs = params['framerate']
    retval = retval.assign(mean_degrees_filtered=butter_bandpass_filter(retval['mean_degrees'], low, high, fs))
    retval = retval.assign(time=retval['frameid']/params['framerate'])
    retval.name = 'foo'
    return retval


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
