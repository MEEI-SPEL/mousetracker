from abc import ABC, abstractmethod
import os
from logging import error


class Extractor(ABC):
    @abstractmethod
    def extract_all(self):
        pass
    @abstractmethod
    def save_left(self):
        pass
    @abstractmethod
    def save_right(self):
        pass
