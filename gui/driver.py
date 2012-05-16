from __future__ import print_function, division
from sys import argv, stderr

def run_gui():
    '''Start the event loop to calucate spectra interactively'''
    # Import Qt functions.  Do so here to handle errors better
    try:
        from PyQt4.QtGui import QApplication
    except ImportError:
        print("Cannot find PyQt4", file=stderr)
        print("You must install this to run the GUI", file=stderr)
        return 1
    # Start the actual event loop
    app = QApplication(argv)

    # For good measure, try to find PyQwt5 now as a check
    try:
        import PyQt4.Qwt5
    except ImportError:
        print("Cannot find PyQwt5", file=stderr)
        print("You must install this to run the GUI", file=stderr)
        return 1

    # Create the GUI window
    from mainwindow import MainWindow
    window = MainWindow()
    window.show()
    window.raise_()
    return app.exec_()
