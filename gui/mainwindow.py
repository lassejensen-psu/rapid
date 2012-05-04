from __future__ import division
from sys import argv, stderr
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget
from plot import Plot
from valuebox import ValueBox
from rateview import RateView
from exchangeview import ExchangeView
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

    def _createtWidgets(self):
        '''Creates all the widgets'''
        self.plot = Plot(self)
        self.control = Controller(self)
        #self.peak_data = PeakData(self)
        #self.exchange = ExchangeMatrix(self)
        self.vbox = [ValueBox(self, 'Parameter Picker 1', 0, self.control),
                     ValueBox(self, 'Parameter Picker 2', 1, self.control)]
        self.rateview = RateView(self.control.rate, parent=self)
        #self.peakview = 
        #self.exchangeview = 
        #self.tab = QTabWidget(self)

    def _initUI(self):
        '''Sets up the layout of the window'''

        # Define a central widget and a layout for the window
        self.setCentralWidget(QWidget())
        self.mainLayout = QHBoxLayout()
        self.setWindowTitle('Spectral Exchange')

        # Add the tab dialog
        self.mainLayout.addWidget(self.rateview)

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
