#! /usr/bin/env python

'''\
Spectral exchange can be run from the command line non-interactively
by giving it a text-based input file and having it generate data from
the input, or it can be run as an interactive GUI.

Authors: Seth M. Morton, Lasse Jensen
'''
from __future__ import print_function, division, absolute_import

# Std. lib imports
from sys import argv, exit, stderr, executable
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import call

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
        print("Cannot find input_reader module, so you should", file=stderr)
        print("install it using your favorite method", file=stderr)
        exit(1)

    # Set up an argument parser so that command line help can be given
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__,
                            prog='RAPID')
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('input_file', nargs='?',
        help='This is the file containing the information needed to execute the '
             'calculation.  If not included, GUI mode will be entered. '
             'NOTE: If the file ends with ".py", it is assumed it is a Python '
             'script and will be executed as one. This is intended for users '
             'without Python installed on their machine who wish to be able to '
             'view the scripts made with the "-s" option.  It can also be used '
             'as a general Python interpreter, with the StdLib, numpy, scipy, '
             'matplotlib, pylab, and input_reader modules installed.  It is not '
             'possible to add more modules.')
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument('--params', '-p', action='store_true', default=False,
        help='Print to the screen how the exchange has modified the peak parameters '
             '(i.e. the Gaussian and Lorentzian broadening terms, the peak heights, '
             'and the vibrational frequencies). No plot will be shown on the screen.')
    meg.add_argument('--data', '-d',
        help='Print to file the data points that would be plotted instead of plotting '
             'the data.  The first column is the vibrational frequencies, and the second '
             'is the intensities. No plot will be shown on the screen')
    meg.add_argument('--script', '-s',
        help='Print to file a self-contained python script that will plot the calculated '
             'data using matplotlib. This is useful to share the generated data, or to'
             'fine-tune to look of the plot. No plot will be shown on the screen.  '
             'You can run the resulting script with "rapid yourscript.py" '
             '("rapid.exe yourscript" on Windows).')
    args = parser.parse_args()

    # If no argument was given, then run in GUI mode
    if not args.input_file:
        from gui import run_gui
        exit(run_gui())

    # Otherwise, run non-interactively, unless the file extension is
    # .py, in which case run as a python file using the current executable
    else:
        if args.input_file.endswith('.py'):
            exit(call([executable, args.input_file]))
        else:
            from cl import run_non_interactive
            exit(run_non_interactive(args))
