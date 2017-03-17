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
from .yaml_config import Config

plt.style.use('fivethirtyeight')
matplotlib.use('PDF')
sns.set(color_codes=True)

timedata = namedtuple("timedata", "frameid,mean_degrees,num_whiskers,stderr")


def plot_left_right(left, right, fp):
    with PdfPages(filename=fp) as pdf:
        ax = left.plot.line(x='time', y='mean_degrees_filtered')
        right.plot.line(ax=ax, x='time', y='mean_degrees_filtered')
        fig = ax.get_figure()
        fig.dpi = 400
        fig.figsize = (8.5, 11)
        pdf.savefig(fig)


def serialized(df: pd.DataFrame, params, name):
    timeseries = filter_raw(df, params, name)
    return save(path.join(path.expanduser('~'), 'Documents', 'whisk_analysis_data'), timeseries)


def test_serialized(pth: str, params: dict):
    with open(pth, 'r') as _:
        whiskdat = json.load(_, object_pairs_hook=OrderedDict)
    timeseries = filter_raw(whiskdat, params)
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
    return df


def filter_raw(whiskdat: pd.DataFrame, params: Config, name: str) -> pd.DataFrame:
    low = 2
    high = 50
    fs = params.camera.framerate

    whiskdat = whiskdat.assign(mean_degrees_filtered=butter_bandpass_filter(whiskdat['mean_degrees'], low, high, fs))
    whiskdat = whiskdat.assign(time=whiskdat['frameid'] / fs)
    whiskdat.name = name
    return whiskdat