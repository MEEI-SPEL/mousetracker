from .base import *
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

#plt.style.use('fivethirtyeight')
matplotlib.use('PDF')
sns.set(color_codes=True)


def make_summary_plots(results: RecordingSessionData):
    """
    Produce summary plots for a recorded bout.
    :param results:
    :return:
    """
    left = next(pd.read_csv(v.summaryfile) for v in results.videos if v.side is SideOfFace.left)
    right = next(pd.read_csv(v.summaryfile) for v in results.videos if v.side is SideOfFace.right)

    with PdfPages(filename=results.summaryfigure) as pdf:
        # plot left vs right
        fig = plt.figure(1, figsize=(11, 8.5), dpi=400)
        ax = fig.gca()
        left.plot.line(ax=ax, x='left_time', y='left_mean_degrees_filtered')
        right.plot.line(ax=ax, x='right_time', y='right_mean_degrees_filtered')
        pdf.savefig(fig)

        d = pdf.infodict()
        d['Title'] = 'Whisking and eyeblink summary'
        d['Author'] = "Graham Voysey <gvoysey@bu.edu>"
        d['Keywords'] = ''
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.now()