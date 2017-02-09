import subprocess
import json
from .base import *


class Whisk:
    def trace(self):
        # of the form trace movie.mp4 output.whiskers
        pass

    def measure(self):
        # of the form measure --face <right,left> whiskers.whiskers whiskers.measurements
        pass

    def classify(self):
        # of the form classify whiskers.measurements whiskers.measurements <right,left> --px2mm <num_mm_in_px> -n -1
        pass

    def __init__(self, params):
        self.params = params


sparams = defaults_yaml['system']
call = [sparams['python27_path'], sparams['trace_path'], '--input',
        'C:\\Users\\VoyseyG\\Desktop\\application\\li1.whiskers']
info('extracting whisker movement for file {0}', '')
whisk_data_left = subprocess.check_output(call)
whisk_data_left = json.loads(whisk_data_left.decode('utf-8'))
camera_parameters['name'] = 'left'
left = serialized(whisk_data_left, camera_parameters)
