from .base import *
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

plt.style.use('fivethirtyeight')
matplotlib.use('PDF')
sns.set(color_codes=True)


def make_plots(results: [VideoFileData]):
    """
    Produce summary plots for a recorded bout.
    :param results:
    :return:
    """
    plot_left_right(results)


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
