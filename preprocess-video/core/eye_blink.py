from .extractor import Extractor


class EyeBlink(Extractor):
    def __init__(self, infile, outfile, camera_params):
        self.camera_params = camera_params
        self.outfile = outfile
        self.infile = infile

    def extract_all(self):
        pass

