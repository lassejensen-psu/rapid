from __future__ import division
from sys import argv
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton
from plot import Plot
from valuebox import ValueBox
from function import Function
from inputfunction import InputFunction

def run_gui():
    '''Start the event loop'''
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    return app.exec_()

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
        #self.functionField = InputFunction(self)
        #self.function = Function(self)
        #self.plotButton = QPushButton('&Plot', self)
        self.vbox = [ValueBox(self, 'Parameter Value Picker 1', 0, self.function),
                     ValueBox(self, 'Parameter Value Picker 2', 1, self.function)]

    def _initUI(self):
        '''Sets up the layout of the window'''

        # Define a central widget and a layout for the window
        self.setCentralWidget(QWidget())
        self.mainLayout = QVBoxLayout()
        self.setWindowTitle('VisualFit')

        # Set up the layout
        for i in xrange(2):
            self.mainLayout.addWidget(self.vbox[i])
        #funcLay = QHBoxLayout()
        #funcLay.addWidget(QLabel('Enter a function: f(x) = '))
        #funcLay.addWidget(self.functionField)
        #funcLay.addWidget(self.plotButton)
        #self.mainLayout.addLayout(funcLay)
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
