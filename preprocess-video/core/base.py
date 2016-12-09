from os import path, environ
import warnings
from logging import basicConfig, INFO

modulePath = path.dirname(path.abspath(__file__))
# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)

avidemuxPath = path.join(environ['PROGRAMFILES'], 'Avidemux 2.6 - 64 bits', 'avidemux_cli.exe')
ffmpegPath = path.join(modulePath, 'resources', 'ffmpeg-win64', 'bin', 'ffmpeg.exe')