import os
import warnings
from logging import basicConfig, INFO

modulePath = os.path.dirname(os.path.abspath(__file__))
# PyYAML has some warnings we'll suppress
warnings.simplefilter(action="ignore", category=(FutureWarning, UserWarning))
# By default, log INFO and up.
basicConfig(format='%(levelname)s %(asctime)s- %(message)s', datefmt='%d %b %H:%M:%S', level=INFO)
