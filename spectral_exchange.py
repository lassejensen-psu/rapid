from __future__ import print_function, division
from sys import argv, exit

'''\
Spectral exchange can be run from the command line non-interactively
by giving it a text-based input file and having it generate data from
the input, or it can be run as an interactive GUI.
'''

if __name__ == '__main__':

    # If an argument was given, then run the non-interactive mode
    if len(argv) >= 1:
        from gui import gui
        exit(run_gui())

    # Otherwise, run the GUI
    else:
        from cl import run_non_interactive
        exit(run_non_interactive(argv[1]))
