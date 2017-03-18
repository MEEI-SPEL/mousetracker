import warnings
from logging import basicConfig, INFO
from os import path
import attr
from attr.validators import instance_of
from attrs_utils import ensure_enum, ensure_cls
from enum import Enum


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
        self.summaryfile = name + "-summary.xlsx"
        self.labelname = path.splitext(path.basename(name))[0]


@attr.s
class RecordingSessionData(object):
    """
    This class holds all of the analysis results for one video bout
    """
    videos = attr.ib()


@attr.s
class Chunk(object):
    """
    This container holds the file paths to the split and aligned video files to be analyzed,
    as well as start and stop frame IDs if the recording needs to be analyzed in chunks.
    """
    left = attr.ib(validator=instance_of(str))
    right = attr.ib(validator=instance_of(str))
    start = attr.ib(validator=instance_of(int))
    stop = attr.ib(validator=instance_of(int))


modulePath = path.dirname(path.abspath(__file__))

# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))

# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)
