from __future__ import division
from sys import argv, stderr
from os import environ
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget, \
                        QAction, QKeySequence, QFileDialog, QPushButton
from PyQt4.Qt import qApp
from numpy import loadtxt, savetxt, array
from plot import Plot
from rate import RateView
from exchange import ExchangeView
from scale import ScaleView
from peak import PeakView
from controller import Controller

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

        # Default to rate in units of ps
        self.rate.rate.click()
        self.rate.unit.setCurrentIndex(2)
        self.rate.rate_value.setText("1.540")
        # Set initial number of peaks to 2
        self.exchange.numpeaks[0].toggle()
        # Set matrix to symmetric by default
        self.exchange.symmetry.setChecked(True)
        # Set the initial window.  
        self.scale.xmin.setText("1900")
        self.scale.xmax.setText("2100")
        # Toggle then untoggle reverse to activate the default limits
        self.scale.reverse.click()
        self.scale.reverse.click()
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

        # Save action
        save = QAction('&Save', self)
        save.setShortcuts(QKeySequence.Save)
        save.triggered.connect(self.saveToInput)
        self.fileMenu.addAction(save)

        # Open action
        open = QAction('&Open', self)
        open.setShortcuts(QKeySequence.Open)
        open.triggered.connect(self.openFromInput)
        self.fileMenu.addAction(open)

        # Import action
        imp = QAction('&Import raw XY data...', self)
        imp.setShortcuts(QKeySequence('Ctrl+I'))
        imp.triggered.connect(self.importXYData)
        self.fileMenu.addAction(imp)

        # Export action
        exp = QAction('&Export calculated XY data...', self)
        exp.setShortcuts(QKeySequence('Ctrl+E'))
        exp.triggered.connect(self.exportXYData)
        self.fileMenu.addAction(exp)

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

    def saveToInput(self):
        '''Save current settings to an input file'''
        pass

    def openFromInput(self):
        '''Open parameters from an input file'''
        pass

    def exportXYData(self):
        '''Export current spectrum to XY data'''
        filter = 'Data Files (*.txt *.data);;All (*)'
        f = QFileDialog.getSaveFileName(self,
                                        'Export calculated XY data',
                                        '',
                                        filter)
        # Grab the XY data from the plot
        x, y = self.plot.calculatedData()
        # Save in a standard format
        savetxt(str(f), array([x,y]).T, fmt='%.1f %.16f')

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

    def clearRawData(self):
        '''Clear the raw data from the plot'''
        self.plot.clearRawData()
        self.clear.setEnabled(False)

    #########
    # SIGNALS
    #########
