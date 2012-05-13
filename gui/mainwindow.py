from __future__ import division
from sys import argv, stderr
from os import environ
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget, \
                        QAction, QKeySequence, QFileDialog, QPushButton
from PyQt4.Qt import qApp
from numpy import loadtxt, savetxt, array
from input_reader import ReaderError
from plot import Plot
from rate import RateView
from exchange import ExchangeView
from scale import ScaleView
from peak import PeakView
from controller import Controller
from common import save_script, read_input
from error import error

class MainWindow(QMainWindow):
    '''The main window of the program'''

    def __init__(self):
        '''Initiallize the main window and it's parents'''
        super(MainWindow, self).__init__()
        self._createtWidgets()
        self._initUI()
        self._makeMenu()
        self._makeConnections()
        self.fileName = None
        self.scriptName = None
        self.expName = None

        # Set initial number of peaks
        self.exchange.setNumPeaks(2)
        # Set matrix to symmetric by default
        self.exchange.setMatrixSymmetry(True)
        # Set the initial window.  
        self.scale.setValue(1900, 2100, False)
        # Default to rate in units of THz
        self.rate.setUnit('THz')
        # Clear button starts off inactive
        self.clear.setEnabled(False)

    def _createtWidgets(self):
        '''Creates all the widgets'''

        # Make the views
        self.plot = Plot(self)
        self.rate = RateView(parent=self)
        self.exchange = ExchangeView(parent=self)
        self.peak = PeakView(parent=self)
        self.scale = ScaleView(parent=self)

        # Create the model controller
        self.control = Controller(self)

        # Attach models to the views
        self.rate.setModel(self.control.rate)
        self.exchange.setModel(self.control.exchange, self.control.numpeaks)
        self.peak.setModel(self.control.peak)
        self.scale.setModel(self.control.scale)

        # Init the UI of all the views
        self.rate.initUI()
        self.exchange.initUI()
        self.peak.initUI()
        self.scale.initUI()

        # Last, make inter-view connections
        self.rate.makeConnections()
        self.exchange.makeConnections()
        self.peak.makeConnections()
        self.scale.makeConnections()

        # The window will own a button to clear raw data
        self.clear = QPushButton('Clear Raw Data', self)

    def _initUI(self):
        '''Sets up the layout of the window'''

        # Define a central widget and a layout for the window
        self.setCentralWidget(QWidget())
        self.mainLayout = QHBoxLayout()
        self.setWindowTitle('Spectral Exchange')

        # Make a layout for all the parameter views
        params = QVBoxLayout()
        params.addWidget(self.rate)
        params.addWidget(self.exchange)
        params.addWidget(self.peak)

        # Add the parameter dialog
        self.mainLayout.addLayout(params)

        # Add the plot 
        plot_lim = QVBoxLayout()
        plot_lim.addWidget(self.plot)
        lim_clear = QHBoxLayout()
        lim_clear.addWidget(self.scale)
        lim_clear.addWidget(self.clear)
        plot_lim.addLayout(lim_clear)
        self.mainLayout.addLayout(plot_lim)

        # Add the widgets to the central widget
        self.centralWidget().setLayout(self.mainLayout)

    def _makeConnections(self):
        '''Connect the widgets to each other'''

        # When the controller says plot, plot
        self.control.plotSpectrum.connect(self.plot.plotCalculatedData)

        # When the controller says resize x limits, do so
        self.control.newXLimits.connect(self.plot.changeScale)

        # Clear raw data if pushed
        self.clear.clicked.connect(self.clearRawData)

    def _makeMenu(self):
        '''Makes the menu bar for this widget'''
        # Get the menu bar object
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&File')

        # Open action
        open = QAction('&Open', self)
        open.setShortcuts(QKeySequence.Open)
        open.triggered.connect(self.openFromInput)
        self.fileMenu.addAction(open)

        # Save action
        save = QAction('&Save', self)
        save.setShortcuts(QKeySequence.Save)
        save.triggered.connect(self.saveToInput)
        self.fileMenu.addAction(save)

        # Save action
        saveas = QAction('Save As', self)
        save.triggered.connect(self.saveToInputAs)
        self.fileMenu.addAction(saveas)

        # Menu seperator
        self.fileMenu.addSeparator()

        # Import action
        imp = QAction('&Import raw XY data', self)
        imp.setShortcuts(QKeySequence('Ctrl+I'))
        imp.triggered.connect(self.importXYData)
        self.fileMenu.addAction(imp)

        # Export action
        exp = QAction('&Export calculated XY data', self)
        exp.setShortcuts(QKeySequence('Ctrl+E'))
        exp.triggered.connect(self.exportXYData)
        self.fileMenu.addAction(exp)

        # Make script action
        scr = QAction('Make Sc&ript', self)
        scr.setShortcuts(QKeySequence('Ctrl+R'))
        scr.triggered.connect(self.makeScript)
        self.fileMenu.addAction(scr)

        # Menu seperator
        self.fileMenu.addSeparator()

        # Quit action
        quit = QAction('&Quit', self)
        quit.setShortcuts(QKeySequence.Quit)
        quit.triggered.connect(qApp.quit)
        self.fileMenu.addAction(quit)

    #######
    # SLOTS
    #######

    def clearRawData(self):
        '''Clear the raw data from the plot'''
        self.plot.clearRawData()
        self.clear.setEnabled(False)

    def openFromInput(self):
        '''Open parameters from an input file'''
        filter = 'Input Files (*.inp);;All (*)'
        self.fileName = QFileDialog.getOpenFileName(self,
                                                   'Open Input File',
                                                   '',
                                                   filter)
        # Read given input file
        try:
            args.read_input(self.fileName)
        except ReaderError as r: # Error reading the input file
            error.showMessage(str(r))
            return


    def saveToInput(self):
        '''Save current settings to current input file if available'''
        pass

    def saveToInputAs(self):
        '''Save current settings to an input file of specified name'''
        pass

    def exportXYData(self):
        '''Export current spectrum to XY data'''
        filter = 'Data Files (*.txt *.data);;All (*)'
        d = '' if self.expName is None else self.expName
        self.expName = QFileDialog.getSaveFileName(self,
                                                  'Export calculated XY data',
                                                  d,
                                                  filter)
        # Grab the XY data from the plot
        x, y = self.plot.calculatedData()
        # Save in a standard format
        savetxt(str(self.expName), array([x,y]).T, fmt='%.1f %.16f')

    def importXYData(self):
        '''Import data from an XY file'''
        filter = 'Data Files (*.txt *.data);;All (*)'
        f = QFileDialog.getOpenFileName(self,
                                        'Import raw XY data',
                                        '',
                                        filter)
        # Load raw data and plot in a second curve
        rawData = loadtxt(str(f))
        self.plot.plotRawData(rawData[:,0], rawData[:,1])
        self.clear.setEnabled(True)

    def makeScript(self):
        '''Open parameters from an input file'''
        filter = 'Python Scripts (*.py)'
        d = '' if self.scriptName is None else self.scriptName
        self.scriptName = QFileDialog.getSaveFileName(self,
                                                     'Make script',
                                                     d,
                                                     filter)
        # Get parameters needed
        xlim, rev, oldp, newp = self.control.getParametersForScript()
        x, y = self.plot.calculatedData()
        if self.clear.isEnabled():
            raw = self.plot.rawData()
        else:
            raw = None
        save_script(x, y, raw, xlim, rev, oldp, newp, self.scriptName)

    #########
    # SIGNALS
    #########
