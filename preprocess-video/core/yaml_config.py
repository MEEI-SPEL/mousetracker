from enum import Enum
from os import path

import attr
import yaml
from attr.validators import instance_of

Species = Enum('Species', "mouse, rat")
WhiskColor = Enum('WhiskColor', 'white, black')


def ensure_cls(cl):
    """If the attribute is an instance of cls, pass, else try constructing."""

    def converter(val):
        if isinstance(val, cl):
            return val
        else:
            return cl(**val)

    return converter


def ensure_enum(cl):
    """If the attribute is an instance of cls, pass, else try constructing."""

    def converter(val):
        if isinstance(val, cl):
            return val
        else:
            return cl[val]

    return converter


def is_path_of_file(instance, attribute, value):
    if not type(value) == str or not path.isfile(value):
        raise FileExistsError('{} is not a valid file.'.format(value))


def low_smaller_than_high(instance, attribute, value):
    if value >= instance.high:
        raise ValueError("'low' has to be smaller than 'high'!")


@attr.s
class Camera(object):
    width = attr.ib(validator=instance_of(int))
    height = attr.ib(validator=instance_of(int))
    framerate = attr.ib(validator=instance_of(int))


@attr.s
class Animal(object):
    species = attr.ib(convert=ensure_enum(Species))
    whisker_color = attr.ib(convert=ensure_enum(WhiskColor))


@attr.s
class System(object):
    python27_path = attr.ib(validator=is_path_of_file)
    trace_path = attr.ib(validator=is_path_of_file)


@attr.s
class Bandpass(object):
    low = attr.ib(validator=low_smaller_than_high)
    high = attr.ib(validator=instance_of(int))


@attr.s
class Config:
    camera = attr.ib(convert=ensure_cls(Camera))
    animal = attr.ib(convert=ensure_cls(Animal))
    system = attr.ib(convert=ensure_cls(System))
    bandpass = attr.ib(convert=ensure_cls(Bandpass))


if __name__ == "__main__":
    with open(path.join(path.dirname(path.abspath(__file__)), 'resources', 'defaults.yaml'), 'r') as _:
        contents = yaml.load(_)
    test = Config(**contents)
    print(test)
