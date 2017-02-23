#!/usr/bin/env python
"""
Whisker Preprocessor.   Extracts bilateral whisking and eyeblink data from a video snippet.

Usage:
    whisker_preprocess -h | --help
    whisker_preprocess --version
    whisker_preprocess ([-i <input_file> | --input <input_file>] | [ --config <config_file> | --print_config] ) [(-o <output_file> | --output <output_file>)]
                       [(-v | --verbose)]

Options:
    -h --help                   Show this screen and exit.
    --version                   Display the version and exit.
    --print_config              Print the default config value and exit.
    -i --input=<input_file>     Specify the file to process.
    -o --output=<output_file>   Specify a location to store the analyzed results.
    --config=<config_file>       Specify a path to a custom config file.  See --print-config for format.
    -v --verbose                Display extra diagnostic information during execution.

"""
# -i "C:\\Users\\VoyseyG\\Dropbox\\Whisker Tracking\\test videos\\whisking with movement (1).MP4"
import platform
import pprint
import sys
from enum import Enum
from logging import info, error, getLogger, ERROR
from os import access, W_OK, utime
from joblib import Parallel, delayed
from multiprocessing import cpu_count
import attr
import cv2
import progressbar
from attr.validators import instance_of
from attrs_utils.interop import from_docopt
from attrs_utils.validators import ensure_cls, ensure_enum
import subprocess
from math import ceil

import core.yaml_config as yaml_config
from core._version import __version__
from core.base import *

MAX_FRAMES = 1000


class SideOfFace(Enum):
    left = 1
    right = 2


@attr.s
class VideoFileData(object):
    name = attr.ib(validator=instance_of(str))
    side = attr.ib(convert=ensure_enum(SideOfFace))

    def __attrs_post_init__(self):
        name, ext = path.splitext(self.name)
        self.whiskname = name + ".whiskers"
        self.measname = name + ".measurements"


@attr.s
class VideoLocations(object):
    videos = attr.ib()


def main(inputargs):
    args = from_docopt(docstring=__doc__, argv=inputargs, version=__version__)
    __check_requirements()
    app_config = yaml_config.load(args.config)
    if args.print_config:
        print("Detected Configuration Parameters: ")
        pprint.pprint(attr.asdict(app_config), depth=5)
        return 0
    __validate_args(args)

    # get the default parameters for the hardware system
    info('read default hardware parameters.')
    info('processing file {0}'.format(path.split(args.input)[1]))
    files = segment_video(args, app_config)

    result = Parallel(n_jobs=cpu_count() - 1)(delayed(extract_whisk_data)(f, app_config) for f in files.videos)
    # extract whisking data for left and right
    # (leftw, rightw) = WhiskerMotion(infile=args.input, outfile=args.output,
    #                                 camera_params=app_config.camera).extract_all()
    # (lefte, righte) = EyeBlink(infile=args.input, outfile=args.output,
    #                            camera_params=app_config.camera).extract_all()

    # test_serialized('test.json', camera_parameters)
    # Return whisker data from file.
    # sparams = app_config.system
    # call = [sparams.python27_path, sparams.trace_path, '--input',
    #         'C:\\Users\\VoyseyG\\Desktop\\application\\li1.whiskers']
    # info('extracting whisker movement for file {0}', '')
    # whisk_data_left = subprocess.check_output(call)
    # whisk_data_left = json.loads(whisk_data_left.decode('utf-8'))
    # camera_parameters['name'] = 'left'
    # left = serialized(whisk_data_left, camera_parameters)
    #
    # call = [sparams.python27_path, sparams.trace_path, '--input',
    #         'C:\\Users\\VoyseyG\\Desktop\\application\\ri2.whiskers']
    # info('extracting whisker movement for file {0}', '')
    # whisk_data_right = subprocess.check_output(call)
    # whisk_data_right = json.loads(whisk_data_right.decode('utf-8'))
    # camera_parameters['name'] = 'right'
    # right = serialized(whisk_data_right, camera_parameters)
    #
    # plot_left_right(left, right, 'joined.pdf')
    # plot_left_right(left.iloc[500:900], right.iloc[500:900], 'zoomed.pdf')


def extract_whisk_data(video: VideoFileData, config):
    base = config.system.whisk_base_path
    trace_path = path.join(base, 'trace.exe')
    trace_args = [video.name, video.whiskname]
    measure_path = path.join(base, 'measure.exe')
    measure_args = ['--face', video.side.name, video.whiskname, video.measname]
    classify_path = path.join(base, 'classify.exe')
    classify_args = [video.measname, video.measname, video.side.name, '--px2mm', '0.04', 'n', '-1']
    reclassify_path = path.join(base, 'reclassify.exe')
    reclassify_args = [video.measname, video.measname, '-n', '-1']

    istraced = subprocess.run([trace_path, *trace_args])
    if istraced.returncode == 0:
        ismeasured = subprocess.run([measure_path, *measure_args])
        if ismeasured.returncode == 0:
            isclassified = subprocess.run([classify_path, *classify_args])
            if isclassified.returncode == 0:
                isreclassified = subprocess.run([reclassify_path, *reclassify_args])
                if isreclassified.returncode == 0:
                    return True
                else:
                    raise IOError("reclassifer failed on {}".format(video.name))
            else:
                raise IOError("classifer failed on {}".format(video.name))
        else:
            raise IOError("measurement failed on {}".format(video.name))
    else:
        raise IOError("trace failed on {}".format(video.name))


@attr.s
class Chunk(object):
    left = attr.ib(validator=instance_of(str))
    right = attr.ib(validator=instance_of(str))
    start = attr.ib(validator=instance_of(int))
    stop = attr.ib(validator=instance_of(int))


def segment_video(args, app_config):
    name, ext = path.splitext(path.basename(args.input))

    cap = cv2.VideoCapture(args.input)
    framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    chunks = ceil(framecount / MAX_FRAMES)

    videos = []
    for c in range(chunks):
        start_frame = MAX_FRAMES * c
        stop_frame = start_frame + MAX_FRAMES - 1
        if stop_frame > framecount:
            stop_frame = framecount

        thisLeft = path.join(args.output, name + "-left" + str(c) + ext)
        thisRight = path.join(args.output, name + "-right" + str(c) + ext)
        chunk = Chunk(left=thisLeft, right=thisRight, start=start_frame, stop=stop_frame)
        videos.extend(prepare_video(args, app_config, chunk))
    return VideoLocations(videos=videos)


def prepare_video(args, app_config, chunk: Chunk):
    """

    :param chunk:
    :param rightpath:
    :param leftpath:
    :param args:
    :param app_config:
    :return:
    """
    left = VideoFileData(name=chunk.left, side=SideOfFace.left)
    right = VideoFileData(name=chunk.right, side=SideOfFace.right)
    if path.isfile(left.name) and path.isfile(right.name):
        return left, right
    else:
        cap = cv2.VideoCapture(args.input)
        # jump to the right frame
        cap.set(1, chunk.start)
        codec = cv2.VideoWriter_fourcc(*'MPEG')
        framerate = app_config.camera.framerate
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        cropped_size = (round(size[0] / 2), size[1])
        framecount = chunk.stop - chunk.start

        vw_left = cv2.VideoWriter(filename=left.name, fourcc=codec, fps=framerate, frameSize=cropped_size, isColor=False)
        vw_right = cv2.VideoWriter(filename=right.name, fourcc=codec, fps=framerate, frameSize=cropped_size, isColor=False)
        curframe = 0
        with progressbar.ProgressBar(min_value=0, max_value=framecount) as pb:
            while cap.isOpened():
                ret, frame = cap.read()
                if ret and (curframe < framecount):
                    curframe += 1
                    pb.update(curframe)
                    # convert to greyscale
                    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # invert colors
                    inverted = cv2.bitwise_not(grey)
                    # split in half
                    left_frame = inverted[0:cropped_size[1], 0:cropped_size[0]]
                    right_frame = inverted[0:cropped_size[1], cropped_size[0]:size[0]]
                    # write out
                    vw_left.write(left_frame)
                    vw_right.write(right_frame)
                    # uncomment to see live preview.
                    # cv2.imshow('left', left)
                    # cv2.imshow('right', right)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #    break
                else:
                    break
            # clean up, because openCV is stupid and doesn't implement `with ...`
            cap.release()
            vw_left.release()
            vw_right.release()
            cv2.destroyAllWindows()
        # either return or die.
        if path.isfile(left.name) and path.isfile(right.name):
            info("wrote {0}".format(left.name))
            info("wrote {0}".format(right.name))
            return left, right
        else:
            raise IOError("Video preprocessing failed on file {}".format(args.input))


def __check_requirements():
    """
    This code relies on a variety of external tools to be available.  If they aren't, warn and barf.
    :return: diagnostic information about what's missing.
    """
    system = platform.system().casefold()
    if system == "windows":
        pass
    else:
        error("This operating system is not supported (windows only for now)")
        sys.exit(1)


def __validate_args(args):
    """
    Makes sure the arguments passed in are reasonable.  Sets the default value for output, if required.  Configures
    logging level.
    :param args:
    :return:
    """
    if not path.isfile(args.input):
        raise FileNotFoundError('{0} not found!'.format(args.input))
    else:
        if not args.output:
            args.output = path.split(args.input)[0]
    if not access(args.output, W_OK):
        raise PermissionError('{0} is not writable!'.format(args.output))
    if not args.verbose:
        getLogger().setLevel(ERROR)
    if args.config and not path.isfile(args.config):
        raise FileNotFoundError('User-supplied configuration file {0} not found!'.format(args.config))


def __touch(fname, times=None):
    """ As coreutils touch.
    """
    with open(fname, 'a+'):
        utime(fname, times)


if __name__ == "__main__":
    # guarantee that we pass the right number of arguments.
    sys.exit(main(sys.argv[1:] if len(sys.argv) > 1 else ""))
