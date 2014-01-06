#! /usr/bin/env python

'''\
Spectral exchange can be run from the command line non-interactively
by giving it a text-based input file and having it generate data from
the input, or it can be run as an interactive GUI.
'''

from __future__ import print_function, division
from sys import argv, exit, stderr

__version__ = '0.9'

if __name__ == '__main__':

    # Try to import numpy and scipy, because these are needed
    # no matter the execution method
    try:
        import numpy
    except ImportError:
        print('It appears that you are missing numpy.', file=stderr)
        print('spectral_exchange requires numpy, so you should', file=stderr)
        print('install it using your favorite method', file=stderr)
        exit(1)
    try:
        import scipy
    except ImportError:
        print('It appears that you are missing scipy.', file=stderr)
        print('spectral_exchange requires scipy, so you should', file=stderr)
        print('install it using your favorite method', file=stderr)
        exit(1)
    # Also try input_reader, since both branches need that
    try:
        from input_reader import ReaderError
    except ImportError:
        print("Cannot find input_reader module", file=stderr)
        print("Find it at github.com/SethMMorton/input_reader", file=stderr)
        exit(1)

    # If an argument was given, then run the non-interactive mode
    if len(argv) == 1:
        from gui import run_gui
        exit(run_gui())

    # Otherwise, run the GUI
    else:
        if argv[1] in ('-v', '--version'):
            print('RAPID: version {0}'.format(__version__))
            exit(0)
        from cl import run_non_interactive
        exit(run_non_interactive(argv[1]))
