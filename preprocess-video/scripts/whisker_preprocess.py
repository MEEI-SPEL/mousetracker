#!/usr/bin/env python
"""
Whisker Preprocessor.   Extracts bilateral whisking and eyeblink data from a video snippet.

Usage:
    whisker_preprocess -h | --help
    whisker_preprocess --version
    whisker_preprocess (-i <input_file> | --input <input_file>) [(-o <output_file> | --output <output_file>)]
                       [(-v | --verbose)] [ --config <config_file> | --print-config]

Options:
    -h --help                   Show this screen and exit.
    --version                   Display the version and exit.
    --print-config              Print the default config value and exit.
    -i --input=<input_file>     Specify the file to process.
    -o --output=<output_file>   Specify a location to store the analyzed results.
    --config=<config_file>       Specify a path to a custom config file.  See --print-config for format.
    -v --verbose                Display extra diagnostic information during execution.

"""
import json
import platform
import subprocess
import sys
from logging import info, error, getLogger, ERROR
from os import access, W_OK, utime

import yaml
from docopt import docopt

# noinspection PyProtectedMember
from core._version import __version__
from core.base import *
from core.eye_blink import EyeBlink
from core.whisk_analysis import serialized, plot_left_right
from core.whisker_motion import WhiskerMotion


def main(inputargs):
    __check_requirements()
    args = docopt(__doc__, version=__version__, argv=inputargs)
    __validate_args(args)
    defaults_yaml = __parse_yaml(args)
    if args['--print-config']:
        print(defaults_yaml)
        return 0

    # get the default parameters for the hardware system
    camera_parameters = defaults_yaml['camera']
    info('read default hardware parameters.')
    info('processing file {0}'.format(path.split(args['--input'])[1]))

    # reduce to 8-bit greyscale

    # invert colors

    # split left and right

    # handle framelength or re-align frame times (tbd)

    # extract whisking data for left and right
    (leftw, rightw) = WhiskerMotion(infile=args['--input'], outfile=args['--output'],
                                    camera_params=camera_parameters).extract_all()
    (lefte, righte) = EyeBlink(infile=args['--input'], outfile=args['--output'],
                               camera_params=camera_parameters).extract_all()

    # test_serialized('test.json', camera_parameters)
    # Return whisker data from file.
    sparams = defaults_yaml['system']
    call = [sparams['python27_path'], sparams['trace_path'], '--input',
            'C:\\Users\\VoyseyG\\Desktop\\application\\li1.whiskers']
    info('extracting whisker movement for file {0}', '')
    whisk_data_left = subprocess.check_output(call)
    whisk_data_left = json.loads(whisk_data_left.decode('utf-8'))
    camera_parameters['name'] = 'left'
    left = serialized(whisk_data_left, camera_parameters)

    call = [sparams['python27_path'], sparams['trace_path'], '--input',
            'C:\\Users\\VoyseyG\\Desktop\\application\\ri2.whiskers']
    info('extracting whisker movement for file {0}', '')
    whisk_data_right = subprocess.check_output(call)
    whisk_data_right = json.loads(whisk_data_right.decode('utf-8'))
    camera_parameters['name'] = 'right'
    right = serialized(whisk_data_right, camera_parameters)

    plot_left_right(left, right, 'joined.pdf')
    plot_left_right(left.iloc[500:900], right.iloc[500:900], 'zoomed.pdf')


def __parse_yaml(args:dict) -> dict:
    """
    Read hardware configuration values from a YAML file.
    :param location: a custom YAML file (optional).  If not specified, values from the default are used.
    :return: a deserialized dictionary.
    """
    loc = path.join(modulePath, 'resources', 'defaults.yaml') if args['--config'] is None else args['--config']
    with open(loc, 'r') as _:
        contents = yaml.load(_)
    return contents


def __check_requirements():
    """
    This code relies on a variety of external tools to be available.  If they aren't, warn and barf.
    :return: diagnostic information about what's missing.
    """
    system = platform.system().casefold()
    retval = ""
    if system == "windows":
        if not path.isfile(avidemuxPath):
            retval += "Avidemux not found \n"
        if not path.isfile(ffmpegPath):
            retval += "ffmpeg not found\n"
    else:
        retval += "This operating system is not supported (windows only for now)"

    if retval:
        error(retval)
        sys.exit(1)


def __validate_args(args: dict):
    """
    Makes sure the arguments passed in are reasonable.  Sets the default value for output, if required.  Configures
    logging level.
    :param args:
    :return:
    """
    if not path.isfile(args['--input']):
        raise FileNotFoundError('{0} not found!'.format(args['--input']))
    else:
        if not args['--output']:
            args['--output'] = path.split(args['--input'])[0]
    if not access(args['--output'], W_OK):
        raise PermissionError('{0} is not writable!'.format(args['--output']))
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)
    if args['--config'] and not path.isfile(args['--config']):
        raise FileNotFoundError('{0} not found!'.format(args['--config']))


def __touch(fname, times=None):
    """ As coreutils touch.
    """
    with open(fname, 'a+'):
        utime(fname, times)


if __name__ == "__main__":
    # guarantee that we pass the right number of arguments.
    sys.exit(main(sys.argv[1:] if len(sys.argv) > 1 else ""))
