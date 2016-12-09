from .extractor import Extractor
from .base import avidemuxPath, ffmpegPath
import shutil


class WhiskerMotion(Extractor):
    def __init__(self, infile, outfile, camera_params):
        self.camera_params = camera_params
        self.outfile = outfile
        self.infile = infile

    def extract_all(self):
        pass
