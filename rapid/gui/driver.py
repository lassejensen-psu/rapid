from __future__ import print_function, division, absolute_import

# Std. lib imports
from sys import argv, stderr

# Non-std. lib import
from PySide.QtGui import QApplication

# Local imports
from rapid.pyqtgraph import Qt


def run_gui():
    '''Start the event loop to calculate spectra interactively'''

    # Start the actual event loop
    app = QApplication(argv)

    # Create the GUI window
    from .mainwindow import MainWindow  # Need to import after QApplication
                                        # is created.
    window = MainWindow()
    window.show()
    window.raise_()
    return app.exec_()
