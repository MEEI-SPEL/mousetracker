#!/usr/bin/env python
"""
Whisker Preprocessor.   Extracts bilateral whisking and eyeblink data from a video snippet.

Usage:
    whisker_preprocess -h | --help
    whisker_preprocess --version
    whisker_preprocess (-i <input_file> | --input <input_file>) [(-o <output_file> | --output <output_file>)]
                       [(-v | --verbose)]

Options:
    -h --help                   Show this screen and exit.
    --version                   Display the version and exit.
    -i --input=<input_file>     Specify the file to process.
    -o --output=<output_file>   Specify a location to store the analyzed results.
    -v --verbose                Display extra diagnostic information during execution.

"""
import sys
from os import path, environ, access, W_OK
import platform
from docopt import docopt
import yaml
from core._version import __version__
from core.base import modulePath
from core.whisker_motion import WhiskerMotion
from core.eye_blink import EyeBlink
from logging import info, error, getLogger, ERROR


def main(inputargs):
    __check_requirements()
    args = docopt(__doc__, version=__version__, argv=inputargs)
    __validate_args(args)

    # get the default parameters for the hardware system
    camera_parameters = __parse_yaml()['camera']
    info('read default hardware parameters.')

    # extract measures
    info('processing file {0}'.format(path.split(args['--input'])[1]))
    WhiskerMotion(infile=args['--input'], outfile=args['--output'], camera_params=camera_parameters).extract_all()
    EyeBlink(infile=args['--input'], outfile=args['--output'], camera_params=camera_parameters).extract_all()


def __parse_yaml(location: str = None) -> dict:
    """
    Read hardware configuration values from a YAML file.
    :param location: a custom YAML file (optional).  If not specified, values from the default are used.
    :return: a deserialized dictionary.
    """
    loc = path.join(modulePath, 'resources', 'defaults.yaml') if location is None else location
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
        if not path.isfile(path.join(environ['PROGRAMFILES'], 'Avidemux 2.6 - 64 bits', 'avidemux_cli.exe')):
            retval += "Avidemux not found \n"
        if not path.isfile(path.join(modulePath, 'resources', 'ffmpeg-win64', 'bin', 'ffmpeg.exe')):
            retval += "ffmpeg not found\n"
    else:
        retval += "This operating system is not supported (windows only for now)"

    if retval:
        error(retval)
        sys.exit(1)


def __validate_args(args: dict):
    if not path.isfile(args['--input']):
        error('{0} not found!'.format(args['--input']))
    if not access(args['--output'], W_OK):
        error('{0} is not writable!'.format(args['--output']))

    if not args["--verbose"]:
        getLogger().setLevel(ERROR)


if __name__ == "__main__":
    # guarantee that we pass the right number of arguments.
    sys.exit(main(sys.argv[1:] if len(sys.argv) > 1 else ""))
