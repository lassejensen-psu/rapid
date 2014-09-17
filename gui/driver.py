from __future__ import print_function, division, absolute_import

# Std. lib imports
from sys import argv, stderr


def run_gui():
    '''Start the event loop to caclucate spectra interactively'''
    # Import Qt functions.  Do so here to handle errors better
    try:
        from PySide.QtGui import QApplication
    except ImportError:
        print("Cannot find PySide", file=stderr)
        print("You must install this to run the GUI", file=stderr)
        return 1
    # For good measure, try to find PyQwt5 now as a check
    try:
        import pyqtgraph
    except ImportError:
        print("Cannot find pyqtgraph", file=stderr)
        print("You must install this to run the GUI", file=stderr)
        return 1

    # Start the actual event loop
    app = QApplication(argv)

    # Create the GUI window
    from .mainwindow import MainWindow
    window = MainWindow()
    window.show()
    window.raise_()
    return app.exec_()
