# Installation Guide (mousetracker)

## Prerequisites

1. Install [git](https://git-scm.com/downloads):
	Then ensure your commit credentials are correct:
	
	```
	git config --global user.name "Your Name"
	git config --global user.email your_email@domain.com
	```
	**N.B.: it's convenient to use git-bash.exe (on windows) to do many of the steps below.  git-bash is just a standard bash command shell, and it's better than `cmd.exe`**
1. Install Python 3.6:
It's easiest to use [anaconda](https://repo.continuum.io/archive/Anaconda3-4.3.1-Windows-x86_64.exe) to install python on windows.  During installation, register _this_ python on the path as "system python".  (this will be an installation prompt)
1. Install Python 2.7:
[anaconda](https://repo.continuum.io/archive/Anaconda2-4.4.0-Windows-x86_64.exe) still easiest.  We need both because the `whisk` API is in python 2. 
1. (optional) Install your python IDE of choice (I prefer `pycharm`, YMMV).
1. Install `ffmpeg`: the latest build is [here](http://ffmpeg.zeranoe.com/builds/), and ensure that it's on your system path.
1. Download and install the Janelia whisk code [here](https://openwiki.janelia.org/wiki/download/attachments/14123320/whisk-1.1.0d-win64.exe?version=2&modificationDate=1338489523000&api=v2).
Make sure to install libraries, python and matlab interfaces.
Also make sure to select the install options for "install to system path."
1. clone the whisk fork to get the python source code and API, from [here](https://github.com/meei-spel/whisk).

## Mousetracker installation
For this section, I assume that the *current working directory* is somewhere convenient.  A popular choice is `C:/Users/<user name>/Projects/`; YMMV.

1. Clone the repositiory to a directory on your computer, as follows
from a bash prompt:

    ```
    $> cd /c/Users/<username>/Projects
    $> git clone https://github.com/meei-spel/mousetracker
    ```
    
1. Install the dependencies needed.

	```
	cd mousetracker
	pip install opencv_*
	pip install -e .
	```

1. Test the installation.
	
	Run the command with the `--help` option.  If the help text displays, you're probably not missing any libraries.
	
	```
	$> analyze_bout --help
	Bout Analyzer.   Extracts bilateral whisking and eyeblink data from a video snippet.
	
	Usage:
	analyze_bout -h | --help
	analyze_bout --version
	analyze_bout ([-i <input_file> | --input <input_file>] | --print_config) [--config <config_file>]
	[(-o <output_file> | --output <output_file>)] [(-v | --verbose)] [--clean]
	
	Options:
	-h --help                   Show this screen and exit.
	--version                   Display the version and exit.
	--print_config              Print the default config value and exit.
	-i --input=<input_file>     Specify the file to process.
	-o --output=<output_file>   Specify a location to store the analyzed results.
	--config=<config_file>      Specify a path to a custom config file.  See --print-config for format.
	--clean                     If existing processed videos and analysis data exist, overwrite them with new.
	-v --verbose                Display extra diagnostic information during execution.
	```
	
1. Generate a new configuration file.

	```
	$> generate_mousetracker_config --output /path/to/directory
	```

1. edit the configuration file. 

	Make sure it's got the correct values in it.  Any text editor will do.
python27_path and trace_path will need to be updated. Everything else should be OK.


## Usage

`analyze_bout --help`  will display the usage guides.  

In brief: pass in the video file (full mouse face) to analyze with the `-i` option. If no other options are specified, a subdirectory in the same common directory will be created and contain analysis results.   The `summary_data.csv` file contains the real meat for later analysis: eye and whisker data for every frame.

