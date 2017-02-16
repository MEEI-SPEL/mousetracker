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
from logging import info, error, getLogger, ERROR
from os import access, W_OK, utime

import cv2
from attrs_utils.interop import from_docopt
import attr
from core._version import __version__
from core.base import *
from core.eye_blink import EyeBlink
from core.whisker_motion import WhiskerMotion
import core.yaml_config as yaml_config


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

    # reduce to 8-bit greyscale
    cv2.VideoCapture(args.input)
    # invert colors

    # split left and right

    # handle framelength or re-align frame times (tbd)

    # extract whisking data for left and right
    (leftw, rightw) = WhiskerMotion(infile=args.input, outfile=args.output,
                                    camera_params=app_config.camera).extract_all()
    (lefte, righte) = EyeBlink(infile=args.input, outfile=args.output,
                               camera_params=app_config.camera).extract_all()

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
        raise FileNotFoundError('{0} not found!'.format(args.config))


def __touch(fname, times=None):
    """ As coreutils touch.
    """
    with open(fname, 'a+'):
        utime(fname, times)


if __name__ == "__main__":
    # guarantee that we pass the right number of arguments.
    sys.exit(main(sys.argv[1:] if len(sys.argv) > 1 else ""))
