from PyQt4.QtCore import pyqtSignal, QObject, QString
from PyQt4.QtGui import QGroupBox, QHBoxLayout, QLabel, \
                        QLineEdit, QIntValidator, QCheckBox
from numpy import arange
from error import error

class Scale(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.xmin = 1800
        self.xmax = 2100
        self.reverse = False
        self.domain = arange(1790, 2110, 0.5)

    def getScale(self):
        '''Returns the scale parameters'''
        return self.xmin, self.xmax, self.reverse

    def getDomain(self):
        '''Returns the frequency domain'''
        return self.domain

    #######
    # SLOTS
    #######

    def setScale(self, min, max, reversed):
        '''Sets the rate and emits the result'''
        replot = (self.xmin != min or self.xmax != max)
        self.xmin = min
        self.xmax = max
        self.reverse = reversed
        self.domain = arange(min-10, max+10, 0.5)
        self.scaleChanged.emit(replot)

    #########
    # SIGNALS
    #########

    # The rate changed
    scaleChanged = pyqtSignal(bool)

#/\/\/\/\/\/\/\/
# The scale view
#/\/\/\/\/\/\/\/

class ScaleView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Window Limits', parent = None):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''

        # The three choosers
        self.xmin = QLineEdit(self)
        self.xmax = QLineEdit(self)
        self.reverse = QCheckBox("Reverse Limits", self)

        # Set validators for limits
        self.xmin.setValidator(QIntValidator(300, 3000, self.xmin))
        self.xmax.setValidator(QIntValidator(300, 3000, self.xmax))

    def initUI(self):
        '''Lays out the widgets'''
        total = QHBoxLayout()
        total.addWidget(QLabel("Lower Limit"))
        total.addWidget(self.xmin)
        total.addStretch()
        total.addWidget(self.reverse)
        total.addStretch()
        total.addWidget(QLabel("Upper Limit"))
        total.addWidget(self.xmax)
        self.setLayout(total)

    def makeConnections(self):
        '''Connect the widgets together'''

        # If any changes happen, reset the scale
        self.xmin.editingFinished.connect(self.resetScale)
        self.xmax.editingFinished.connect(self.resetScale)
        self.reverse.clicked.connect(self.resetScale)

    def setModel(self, model):
        '''Attaches models to the views'''
        self.model = model

    def setValue(self, xmin, xmax, reversed):
        '''Manually sets the values that are viewed'''
        self.xmin.setText(str(xmin))
        self.xmax.setText(str(xmax))
        self.reverse.setChecked(reversed)
        self.reverse.clicked.emit(reversed)

    #######
    # SLOTS
    #######

    def resetScale(self):
        '''Checks that the given scale is valid, then resets if so'''
        xmin = self.xmin.text().toInt()[0]
        xmax = self.xmax.text().toInt()[0]
        reverse = self.reverse.isChecked()
        if xmin > xmax:
            err = "Lower limit cannot be greater than upper limit"
            error.showMessage(err)
            return
        self.model.setScale(xmin, xmax, reverse)
