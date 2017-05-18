from enum import Enum
from os import path

import attr
import yaml
from attr.validators import instance_of
from attrs_utils import ensure_cls, ensure_enum, is_path_of_file
from mousetracker.core.base import modulePath

Species = Enum('Species', "mouse, rat")
WhiskColor = Enum('WhiskColor', 'white, black')
EyeColor = Enum('EyeColor', 'red')


@attr.s(frozen=True)
class Camera(object):
    """
    Data container for parameters relating to the camera recording the animal
    """
    width = attr.ib(validator=instance_of(int))
    height = attr.ib(validator=instance_of(int))
    framerate = attr.ib(validator=instance_of(int))
    px2mm = attr.ib(validator=instance_of(float))


@attr.s(frozen=True)
class Animal(object):
    """
    Data about the animal
    """
    species = attr.ib(convert=ensure_enum(Species))
    whisker_color = attr.ib(convert=ensure_enum(WhiskColor))
    eye_color = attr.ib(convert=ensure_enum(EyeColor))
    num_whiskers = attr.ib(validator=instance_of(int))


@attr.s(frozen=True)
class System(object):
    """
    System parameters
    """
    python27_path = attr.ib(validator=is_path_of_file)
    trace_path = attr.ib(validator=is_path_of_file)


@attr.s(frozen=True)
class Storage(object):
    """
    Storage parameters
    """
    root_label = attr.ib(validator=instance_of(str))
    output_root = attr.ib(validator=instance_of(str))
    name_format = attr.ib(validator=instance_of(str))


@attr.s(frozen=True)
class Config:
    """
    All configuration values
    """
    camera = attr.ib(convert=ensure_cls(Camera))
    animal = attr.ib(convert=ensure_cls(Animal))
    system = attr.ib(convert=ensure_cls(System))
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
