from os import path, environ
import warnings
from logging import basicConfig, INFO
import attr
from attr.validators import instance_of


@attr.s
class Consts:
    rootLabel = attr.ib(default='.whisk-output-root')
    outputRoot = attr.ib(default='whisk-output')
    resultDirectoryNameFormat = attr.ib(default="%d %b %y - %H%M")

@attr.s
class Camera:
    width = attr.ib(validator=instance_of(int))
    height = attr.ib(validator=instance_of(int))
    framerate = attr.ib(validator=instance_of(int))

@attr.s
class Animal:
    species = attr.ib(validator=instance_of(str))
    color = attr.ib(validator=instance_of(str))

@attr.s
class System:
    python27_path = attr.ib(instance_of(str))
    trace_path = attr.ib(instance_of(str))

@attr.s
class Config:
    camera = attr.ib(convert=Camera, validator=instance_of(Camera))
    animal = attr.ib(convert=Animal, validator=instance_of(Animal))
    system = attr.ib(convert=System, validator=instance_of(System))


modulePath = path.dirname(path.abspath(__file__))
# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)

avidemuxPath = path.join(environ['PROGRAMFILES'], 'Avidemux 2.6 - 64 bits', 'avidemux_cli.exe')
ffmpegPath = path.join(modulePath, 'resources', 'ffmpeg-win64', 'bin', 'ffmpeg.exe')
defaults = Consts()
