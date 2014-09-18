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

# Local imports
from rapid._version import __version__


def main():
    """Main Driver."""

    # Set up an argument parser so that command line help can be given
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__,
                            prog='RAPID')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    parser.add_argument('input_file', nargs='?',
        help='This is the file containing the information needed to execute the '
             'calculation.  If not included, GUI mode will be entered.')
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
        from rapid.gui import run_gui
        exit(run_gui())

    # Otherwise, run non-interactively
    else:
        from rapid.cl import run_non_interactive
        exit(run_non_interactive(args))


if __name__ == '__main__':
    main()
