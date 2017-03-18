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

from scripts.whisker_preprocess import VideoFileData
from .util.filters import butter_bandpass_filter
from .yaml_config import Config

plt.style.use('fivethirtyeight')
matplotlib.use('PDF')
sns.set(color_codes=True)

timedata = namedtuple("timedata", "frameid,mean_degrees,num_whiskers,stderr")


def plot_left_right(results: [VideoFileData]):
    with PdfPages(filename=fp) as pdf:
        ax = left.plot.line(x='time', y='mean_degrees_filtered')
        right.plot.line(ax=ax, x='time', y='mean_degrees_filtered')
        fig = ax.get_figure()
        fig.dpi = 400
        fig.figsize = (8.5, 11)
        pdf.savefig(fig)


def plot(dirpath, df):
    with PdfPages(filename=path.join(dirpath, df.name + ".pdf")) as pdf:
        ax = df.plot.line(x='frameid', y='mean_degrees', yerr='stderr')
        fig = ax.get_figure()
        fig.dpi = 400
        fig.figsize = (8.5, 11)
        pdf.savefig(fig)


def filter_raw(whiskdat: pd.DataFrame, params: Config, name: str) -> pd.DataFrame:
    low = 2
    high = 50
    fs = params.camera.framerate

    whiskdat = whiskdat.assign(mean_degrees_filtered=butter_bandpass_filter(whiskdat['mean_degrees'], low, high, fs))
    whiskdat = whiskdat.assign(time=whiskdat['frameid'] / fs)
    whiskdat.name = name
    return whiskdat
