from setuptools import setup, find_packages, Extension
# makes __version__ a local variable
exec(open('bout_analysis/core/_version.py').read())
setup(
    name='mousetracker',
    version=__version__,
    packages=find_packages(),
    scripts=['bout_analysis/scripts/analyze_bout.py',
            ],
    url='https://github.com/MEEI-SPEL/mousetracker',
    license='',
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description=''
)
