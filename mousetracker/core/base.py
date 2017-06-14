import warnings
from enum import Enum
from logging import basicConfig, INFO
from os import path

import attr
from attr.validators import instance_of
from attrs_utils import ensure_enum


class SideOfFace(Enum):
    """
    Label for which side of the face is being analyzed.  Direction is animal-relative not video relative.
    """
    left = 1
    right = 2


@attr.s
class VideoFileData(object):
    """
    This class holds the file locations for the source video, analyzed results, and raw eye data.
    """
    name = attr.ib(validator=instance_of(str))
    side = attr.ib(convert=ensure_enum(SideOfFace))
    eye = attr.ib()
    nframes = attr.ib(validator=instance_of(int))

    def __attrs_post_init__(self):
        name, ext = path.splitext(self.name)
        self.basename = name
        self.whiskname = name + ".whiskers"
        self.measname = name + ".measurements"
        self.eyecheck = name + "-eye-checkpoint.csv"
        self.whiskraw = name + "-whisk-raw.csv"
        self.whiskcheck = name + "-whisk-checkpoint.csv"
        self.summaryfile = name + "-summary.csv"
        self.labelname = path.splitext(path.basename(name))[0]


@attr.s
class RecordingSessionData(object):
    """
    This class holds all of the analysis results for one video bout
    """
    videos = attr.ib()

    def __attrs_post_init__(self):
        self.rootdir = path.split(self.videos[0].name)[0] if len(self.videos) > 0 else None
        self.summaryfigure = path.join(self.rootdir, "summary_plots.pdf") if self.rootdir else None
        self.summarystats = path.join(self.rootdir, "summary_data.csv") if self.rootdir else None


modulePath = path.dirname(path.abspath(__file__))

# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))

# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)
