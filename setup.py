#! /usr/bin/env python

# Std. lib imports
from os.path import join

# Non-std. lib imports
from setuptools import setup, find_packages


def current_version():
    '''Get the current version number'''
    import re
    VERSIONFILE = join('rapid', '_version.py')
    with open(VERSIONFILE, "rt") as fl:
        versionstring = fl.readline().strip()
    m = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", versionstring)
    if m:
        return m.group(1)
    else:
        s = "Unable to locate version string in {0}"
        raise RuntimeError(s.format(VERSIONFILE))


DESCRIPTION = "RAPID: Simulate IR and Raman peaks with fast exchange"
try:
    with open('README.md') as fl:
        LONG_DESCRIPTION = fl.read()
except IOError:
    LONG_DESCRIPTION = DESCRIPTION

required = ['argparse', 'input_reader >=1.2.2', 'numpy >=1.7',
            'matplotlib', 'scipy', 'PySide']

# Define the build
setup(name='rapid',
      version=current_version(),
      author=['Seth M. Morton',
              'Lasse Jensen'],
      author_email='jensen@chem.psu.com',
      url="http://research.chem.psu.edu/lxjgroup/Research.html",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      license='MIT',
      packages=find_packages(),
      entry_points={'gui_scripts': ['rapid = rapid.__main__:main']},
      install_requires=required,
      use_2to3=True,
      classifiers=('Development Status :: 4 - Beta',
                   #'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Topic :: Scientific/Engineering',
                   ),
      )
