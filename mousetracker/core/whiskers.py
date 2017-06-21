import subprocess
from collections import namedtuple
from logging import info

import os
import pandas as pd
import shutil
from mousetracker.core.base import *
from mousetracker.core.util.signal_processing import lowpass
from mousetracker.core.yaml_config import Config

timedata = namedtuple("timedata", "frameid,mean_degrees,num_whiskers,stderr")


def estimate_whisking_from_measurements(video: VideoFileData, config, keep_files):
    """
    Extract statistics from the Measurements file
    :param video: 
    :param config: 
    :param keep_files: 
    :return: 
    """
    checkpoint = video.whiskraw
    if not (path.isfile(checkpoint) and keep_files):
        call = [config.system.python27_path, config.system.load_measurements_path, '--input', video.whiskname, '-o',
                checkpoint]
        info(f'extracting whisker movement from {video.labelname}')
        data = subprocess.run(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if data.returncode == 0:
            data = pd.read_csv(checkpoint)
        else:
            raise IOError(f"failed to extract from {video.labelname}: {repr(data.stderr)}")
    else:
        info(f"found existing whisker data for {video.labelname}")
        data = pd.read_csv(checkpoint)

def estimate_whisking_from_raw_whiskers(video: VideoFileData, config, keep_files):
    """
    Extract the bulk pad displacement per frame from a whiskers file.
    :param video:
    :param config:
    :param keep_files:
    :return:
    """
    checkpoint = video.whiskraw
    if not (path.isfile(checkpoint) and keep_files):
        call = [config.system.python27_path, config.system.load_whiskers_path, '--input', video.whiskname, '-o', checkpoint]
        info(f'extracting whisker movement from {video.labelname}')
        data = subprocess.run(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if data.returncode == 0:
            data = pd.read_csv(checkpoint)
        else:
            raise IOError(f"failed to extract from {video.labelname}: {repr(data.stderr)}")
    else:
        info(f"found existing whisker data for {video.labelname}")
        data = pd.read_csv(checkpoint)

    side = filter_raw(data, config, video.labelname)
    # rename columns to match side of face.
    side.columns = (side.columns[0], *[video.side.name+'_'+x for x in side.columns[1:]])
    side.to_csv(video.whiskcheck)
    side = side.set_index('frameid')
    # eeeew.
    if path.isfile(video.eyecheck) and video.eye is None:
        video.eye = pd.read_csv(video.eyecheck)
    joined = side.join(video.eye)
    joined.to_csv(video.summaryfile)


def extract_whisk_data(video: VideoFileData, config, keep_files):
    """
    Run the whisk code toolchain on a video file.  generate a whiskers and measurements file.
    :param video:
    :param config:
    :param keep_files:
    :return:
    """
    trace_path = shutil.which('trace')
    trace_args = [video.aligned, video.whiskname]
    measure_path = shutil.which('measure')
    measure_args = ['--face', video.side.name, video.whiskname, video.measname]
    classify_path = shutil.which('classify')
    classify_args = [video.measname, video.measname, video.side.name, '--px2mm', str(config.camera.px2mm),
                     '-n', str(config.animal.num_whiskers)]
    reclassify_path = shutil.which('reclassify.exe')
    reclassify_args = [video.measname, video.measname, '-n', '-1']
    if not (keep_files and path.exists(video.whiskname)):
        info(f'tracing whiskers for {video.labelname}')
        istraced = subprocess.run([trace_path, *trace_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        info(f'found existing whiskers file for {video.labelname}')
        istraced = subprocess.CompletedProcess(args=[], returncode=0)  # fake a completed run.
    if istraced.returncode == 0:
        info(f"trace OK for {video.labelname}")
        if not (keep_files and path.exists(video.measname)):
            info(f'measuring whiskers for {video.labelname}')
            ismeasured = subprocess.run([measure_path, *measure_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            info(f'found existing measurements file for {video.labelname}')
            ismeasured = subprocess.CompletedProcess(args=[], returncode=0)  # fake a completed run.

        if ismeasured.returncode == 0:
            info(f"measure OK for {video.labelname}")
            if not (keep_files and path.exists(video.measname)):
                info(f'classifying whiskers for {video.labelname}')
                isclassified = subprocess.run([classify_path, *classify_args], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
            else:
                info(f'found existing measurements file for {video.labelname}')
                isclassified = subprocess.CompletedProcess(args=[], returncode=0)  # fake a completed run.

            if isclassified.returncode == 0:
                info(f"classification OK for {video.labelname}")
                if not (keep_files and path.exists(video.measname)):
                    info(f'reclassifying whiskers for {video.labelname}')
                    isreclassified = subprocess.run([reclassify_path, *reclassify_args], stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
                else:
                    info(f'found existing measurements file for {video.labelname}')
                    isreclassified = subprocess.CompletedProcess(args=[], returncode=0)  # fake a completed run.

                if isreclassified.returncode == 0:
                    info(f"reclassification OK for {video.labelname}")
                    info(f"whiskers complete for {video.labelname}")
                    if not path.isfile(video.whiskname) or not path.isfile(video.measname):
                        raise IOError(f"whisker or measurement file was not saved for {video.name}")
                    if not (path.isfile(video.summaryfile) and keep_files):
                        estimate_whisking_from_raw_whiskers(video, config, keep_files)
                        # return video
                else:
                    raise IOError(f"reclassifier failed on {video.labelname}")
            else:
                raise IOError(f"classifier failed on {video.labelname}")
        else:
            raise IOError(f"measurement failed on {video.labelname}")
    else:
        raise IOError(f"trace failed on {video.labelname}")


def filter_raw(whiskdat: pd.DataFrame, params: Config, name: str) -> pd.DataFrame:
    """
    Apply a low-pass filter to whisker displacement measurements
    :param whiskdat: 
    :param params: 
    :param name: 
    :return: 
    """
    fs = params.camera.framerate
    whiskdat = whiskdat.assign(mean_degrees_filtered=lowpass(data=whiskdat['mean_degrees'], fs=fs))
    whiskdat = whiskdat.assign(time=whiskdat['frameid'] / fs)
    whiskdat.name = name
    return whiskdat
