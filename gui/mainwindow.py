from __future__ import division
from sys import argv, stderr
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget
from plot import Plot
from valuebox import ValueBox
from rate import RateView
from exchange import ExchangeView
from controller import Controller

class MainWindow(QMainWindow):
    '''The main window of the program'''

    def __init__(self):
        '''Initiallize the main window and it's parents'''
        super(MainWindow, self).__init__()
        self._createtWidgets()
        self._initUI()
        #self._makeConnections()

        # Set the default function to be sin
        #self.functionField.setText("a*sin(b*x+c)+d")
        #self.plotButton.clicked.emit(True)
        #self.vbox[0].changeParameter(0)
        #self.vbox[1].changeParameter(1)

        # Default to rate in units of ps
        self.rate.rate.click()
        self.rate.rate_value.setValue(1.54)

        # Set initial number of peaks to 2
        # Doing it twice seems to fix a bug
        self.exchange.numpeaks.setValue(5)
        self.exchange.numpeaks.setValue(2)

    def _createtWidgets(self):
        '''Creates all the widgets'''

        # Make the views
        self.plot = Plot(self)
        self.vbox = [ValueBox(self, 'Parameter Picker 1', 0),
                     ValueBox(self, 'Parameter Picker 2', 1)]
        self.rate = RateView(parent=self)
        self.exchange = ExchangeView(parent=self)
        #self.peak_data = PeakData(self)

        # Create the model controller
        self.control = Controller(self, self.exchange)

        # Attach models to the views
        self.vbox[0].setModel(self.control)
        self.vbox[1].setModel(self.control)
        self.rate.setModel(self.control.rate)
        self.exchange.setModel(self.control.exchange, self.control.numpeaks)

        # Init the UI of all the views
        self.vbox[0].initUI()
        self.vbox[1].initUI()
        self.rate.initUI()
        self.exchange.initUI()

        # Last, make inter-view connections
        #self.vbox[0].makeConnections()
        #self.vbox[1].makeConnections()
        self.rate.makeConnections()
        self.exchange.makeConnections()

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

        # Add the parameter dialog
        self.mainLayout.addLayout(params)

        # Add the value box and plot
        vbox_plot = QVBoxLayout()
        for i in xrange(2):
            vbox_plot.addWidget(self.vbox[i])
        #funcLay = QHBoxLayout()
        #funcLay.addWidget(QLabel('Enter a function: f(x) = '))
        #funcLay.addWidget(self.functionField)
        #funcLay.addWidget(self.plotButton)
        #self.mainLayout.addLayout(funcLay)
        vbox_plot.addWidget(self.plot)
        self.mainLayout.addLayout(vbox_plot)

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
