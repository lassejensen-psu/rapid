from __future__ import print_function, division, absolute_import

# Non-std. lib imports
from PySide.QtCore import Signal, QObject
from PySide.QtGui import QGroupBox, QHBoxLayout, QLabel, \
                        QLineEdit, QIntValidator, QCheckBox
from numpy import arange

# Local imports
from .guicommon import error
from .guicommon import toolTipText as ttt


class Scale(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initialize the function class'''
        super(Scale, self).__init__(parent)
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
        replot = (self.xmin != min or self.xmax != max or self.reverse != reversed)
        self.xmin = min
        self.xmax = max
        self.reverse = reversed
        self.domain = arange(min-10, max+10, 0.5)
        self.scaleChanged.emit(replot)

    #########
    # SIGNALS
    #########

    # The rate changed
    scaleChanged = Signal(bool)

#/\/\/\/\/\/\/\/
# The scale view
#/\/\/\/\/\/\/\/


class ScaleView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Window Limits', parent = None):
        '''Initialize'''
        super(ScaleView, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''

        # The three choosers
        self.xmin = QLineEdit(self)
        self.xmin.setToolTip(ttt('The lower limit of the plot, in '
                                 'wavenumbers'))
        self.xmax = QLineEdit(self)
        self.xmax.setToolTip(ttt('The upper limit of the plot, in '
                                 'wavenumbers'))
        self.reverse = QCheckBox("Reverse Limits", self)
        self.reverse.setToolTip(ttt('Display plot with higher frequencies on '
                                    'the left, not the right'))

        # Set validators for limits
        self.xmin.setValidator(QIntValidator(300, 3000, self.xmin))
        self.xmax.setValidator(QIntValidator(300, 3000, self.xmax))

        # The wavelength selection
        self.wavenum = QLineEdit('      ')
        self.wavenum.setReadOnly(True)
        self.intense = QLineEdit('     ')
        self.intense.setReadOnly(True)

    def initUI(self):
        '''Lays out the widgets'''
        total = QHBoxLayout()
        total.addWidget(QLabel("Wavenum: "))
        total.addWidget(self.wavenum)
        total.addWidget(QLabel("Intens.: "))
        total.addWidget(self.intense)
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
        self.reverse.clicked.emit()

    #######
    # SLOTS
    #######

    def resetScale(self):
        '''Checks that the given scale is valid, then resets if so'''
        try:
            xmin = int(self.xmin.text())
        except ValueError:
            return
        try:
            xmax = int(self.xmax.text())
        except ValueError:
            return
        reverse = self.reverse.isChecked()
        if xmin > xmax:
            err = "Lower limit cannot be greater than upper limit"
            error.showMessage(err)
            return
        self.model.setScale(xmin, xmax, reverse)

    def setSelection(self, x, y):
        '''Displays the current selection'''
        x = max(min(x, float(self.xmax.text())),
                float(self.xmin.text()))
        y = max(min(y, 1.0), 0.0)
        self.wavenum.setText('{0:.1f}'.format(x))
        self.intense.setText('{0:.3f}'.format(y))
