from __future__ import division
from sys import argv, stderr
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget
from plot import Plot
from rate import RateView
from exchange import ExchangeView
from peak import PeakView
from controller import Controller

class MainWindow(QMainWindow):
    '''The main window of the program'''

    def __init__(self):
        '''Initiallize the main window and it's parents'''
        super(MainWindow, self).__init__()
        self._createtWidgets()
        self._initUI()
        #self._makeConnections()

        # Default to rate in units of ps
        self.rate.rate.click()
        self.rate.rate_value.setValue(1.54)

        # Set initial number of peaks to 2
        # Doing it twice seems to fix a bug
        self.exchange.numpeaks.setValue(5)
        self.exchange.numpeaks.setValue(2)
        # Set matrix to symmetric by default
        self.exchange.symmetry.setChecked(True)

    def _createtWidgets(self):
        '''Creates all the widgets'''

        # Make the views
        self.plot = Plot(self)
        self.rate = RateView(parent=self)
        self.exchange = ExchangeView(parent=self)
        self.peak = PeakView(parent=self)

        # Create the model controller
        self.control = Controller(self)

        # Attach models to the views
        self.rate.setModel(self.control.rate)
        self.exchange.setModel(self.control.exchange, self.control.numpeaks)
        self.peak.setModel(self.control.peak)

        # Init the UI of all the views
        self.rate.initUI()
        self.exchange.initUI()
        self.peak.initUI()

        # Last, make inter-view connections
        self.rate.makeConnections()
        self.exchange.makeConnections()
        self.peak.makeConnections()

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
        self.mainLayout.addWidget(self.plot)

        # Add the widgets to the central widget
        self.centralWidget().setLayout(self.mainLayout)

    def _makeConnections(self):
        '''Connect the widgets to each other'''

        # If the plot button is pressed (or return is pressed), plot the function
        self.plotButton.clicked.connect(self.functionField.plotFunction)
        self.functionField.returnPressed.connect(self.functionField.plotFunction)

        # If the function is broadcasted, have the function class catch and  parse it
        self.functionField.broadcastFunction.connect(self.function.parseFunction)

        # When the function class emits the function, have the plot grab it
        self.function.hasPlotableFunction.connect(self.plot.plotFunction)

    #######
    # SLOTS
    #######

    #########
    # SIGNALS
    #########
