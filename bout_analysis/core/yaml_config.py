from enum import Enum
from os import path

import attr
import yaml
from attr.validators import instance_of
from attrs_utils import ensure_cls, ensure_enum, is_path_of_file
from .base import modulePath

Species = Enum('Species', "mouse, rat")
WhiskColor = Enum('WhiskColor', 'white, black')


def low_smaller_than_high(instance, attribute, value):
    if value >= instance.high:
        raise ValueError("'low' has to be smaller than 'high'!")


@attr.s(frozen=True)
class Camera(object):
    width = attr.ib(validator=instance_of(int))
    height = attr.ib(validator=instance_of(int))
    framerate = attr.ib(validator=instance_of(int))


@attr.s(frozen=True)
class Animal(object):
    species = attr.ib(convert=ensure_enum(Species))
    whisker_color = attr.ib(convert=ensure_enum(WhiskColor))


@attr.s(frozen=True)
class System(object):
    python27_path = attr.ib(validator=is_path_of_file)
    trace_path = attr.ib(validator=is_path_of_file)
    avidemux_path = attr.ib(validator=is_path_of_file)
    ffmpeg_path = attr.ib(validator=is_path_of_file)
    whisk_base_path = attr.ib(validator=instance_of(str))


@attr.s(frozen=True)
class Bandpass(object):
    low = attr.ib(validator=low_smaller_than_high)
    high = attr.ib(validator=instance_of(int))


@attr.s(frozen=True)
class Storage(object):
    root_label = attr.ib(validator=instance_of(str))
    output_root = attr.ib(validator=instance_of(str))
    name_format = attr.ib(validator=instance_of(str))


@attr.s(frozen=True)
class Config:
    camera = attr.ib(convert=ensure_cls(Camera))
    animal = attr.ib(convert=ensure_cls(Animal))
    system = attr.ib(convert=ensure_cls(System))
    bandpass = attr.ib(convert=ensure_cls(Bandpass))
    storage = attr.ib(convert=ensure_cls(Storage))


def load(customconfig: str) -> Config:
    """
    Read hardware configuration values from a YAML file.
    :param customconfig: a custom YAML file (optional).  If not specified, values from the default are used.
    :return: a deserialized dictionary.
    """
    loc = path.join(modulePath, 'resources', 'defaults.yaml') if customconfig is None else customconfig
    with open(loc, 'r') as _:
        contents = yaml.load(_)
    return Config(**contents)


if __name__ == "__main__":
    with open(path.join(path.dirname(path.abspath(__file__)), 'resources', 'defaults.yaml'), 'r') as _:
        contents = yaml.load(_)
    test = Config(**contents)
    print(test)
