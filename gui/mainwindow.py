from __future__ import division
from sys import argv, stderr
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget
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
        plot_lim.addWidget(self.scale)
        self.mainLayout.addLayout(plot_lim)

        # Add the widgets to the central widget
        self.centralWidget().setLayout(self.mainLayout)

    def _makeConnections(self):
        '''Connect the widgets to each other'''

        # When the controller says plot, plot
        self.control.plotSpectrum.connect(self.plot.plotFunction)

        # When the controller says resize x limits, do so
        self.control.newXLimits.connect(self.plot.changeScale)

    def _makeMenu(self):
        '''Makes the menu bar for this widget'''
        # Get the menu bar object
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&File')
        self.fileMenu.addAction('Import XY data...')
        self.fileMenu.addAction('Export XY data...')
        self.fileMenu.addAction('Export as script...')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Exit')

    #######
    # SLOTS
    #######

    #########
    # SIGNALS
    #########
