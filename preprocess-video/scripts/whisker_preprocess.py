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
from os import path
from docopt import docopt
import yaml
from core._version import __version__
from core.base import modulePath
from logging import info, getLogger, ERROR


def main(inputargs):
    args = docopt(__doc__, version=__version__, argv=inputargs)
    if not args["--verbose"]:
        getLogger().setLevel(ERROR)

    # get the default parameters for the hardware system
    foo = __parse_yaml()['Camera']



def __parse_yaml(location: str = None) -> dict:
    loc = path.join(modulePath, 'resources', 'defaults.yaml') if location is None else location
    with open(loc, 'r') as _:
        contents = yaml.load(_)
    return contents


if __name__ == "__main__":
    # guarantee that we pass the right number of arguments.
    sys.exit(main(sys.argv[1:] if len(sys.argv) > 1 else ""))
