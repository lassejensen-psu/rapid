from __future__ import print_function, division, absolute_import

# Std. lib imports
from math import pi

# Non-std. lib imports 
from PySide.QtCore import Signal, QObject
from PySide.QtGui import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, \
                        QComboBox, QRadioButton, QStringListModel, \
                        QLineEdit, QDoubleValidator, QGridLayout
from numpy.testing import assert_approx_equal

# Local imports
from .guicommon import error
from .guicommon import toolTipText as ttt

HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )


class Rate(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initialize the function class'''
        super(Rate, self).__init__(parent)
        self.converter = lambda x: x
        self.lunits = QStringListModel('s ns ps fs'.split(' '))
        self.runits = QStringListModel('Hz GHz THz PHz'.split(' '))
        self.method = ''

    def setConverter(self, unit):
        '''Sets the function to perform rate conversion to cm^{-1}'''

        self.unit = str(unit)
        conv = {
                 'fs'   : lambda x : HZ2WAVENUM / ( 1E-15 * x ),
                 'ps'   : lambda x : HZ2WAVENUM / ( 1E-12 * x ),
                 'ns'   : lambda x : HZ2WAVENUM / ( 1E-9  * x ),
                 's'    : lambda x : HZ2WAVENUM / (         x ),
                 'PHz'  : lambda x : HZ2WAVENUM * 1E15 * x,
                 'THz'  : lambda x : HZ2WAVENUM * 1E12 * x,
                 'GHz'  : lambda x : HZ2WAVENUM * 1E9  * x,
                 'Hz'   : lambda x : HZ2WAVENUM        * x,
               }
        try:
            self.converter = conv[self.unit]
        except KeyError:
            pass # This happens when we set a new model.  Ignore

    def getParams(self):
        '''Returns the current rate parameters'''
        # Return None if rate is not yet defined
        try:
            return self.rate, self.unit
        except AttributeError:
            return None, None

    def getConvertedRate(self):
        '''Returns the rate in wavenumbers'''
        # Return None if rate is not yet defined
        try:
            return self.converter(self.rate)
        except AttributeError:
            return None

    #######
    # SLOTS
    #######

    def setRate(self, rate):
        '''Sets the rate and emits the result'''
        self.rate = rate
        self.rateChanged.emit()

    #########
    # SIGNALS
    #########

    # The rate changed
    rateChanged = Signal()

#/\/\/\/\/\/\/\
# The rate view
#/\/\/\/\/\/\/\


class RateView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Rate', parent = None):
        '''Initialize'''
        super(RateView, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''

        # Rate or lifetime chooser
        self.rate = QRadioButton('Rate', self)
        self.rate.setToolTip(ttt('Choose this to express exchange as rate'))
        self.lifetime = QRadioButton('Lifetime', self)
        self.lifetime.setToolTip(ttt('Choose this to express exchange as '
                                     'lifetime'))

        # Box containing value
        self.rate_value = QLineEdit(self)
        validate = QDoubleValidator(self.rate_value)
        validate.setDecimals(3)
        validate.setBottom(0.0)
        self.rate_value.setValidator(validate)
        self.rate_value.setToolTip(ttt('The rate or lifetime value'))

        # Unit
        self.unit = QComboBox(self)
        self.unit.setToolTip(ttt('Selects the input unit for the rate '
                                 'or lifetime'))

    def initUI(self):
        '''Lays out the widgets'''
        radios = QVBoxLayout()
        radios.addWidget(self.rate)
        radios.addWidget(self.lifetime)
        rate = QGridLayout()
        rate.addWidget(QLabel("Unit: "), 1, 1)
        rate.addWidget(self.unit, 1, 2)
        rate.addWidget(QLabel("Value: "), 2, 1)
        rate.addWidget(self.rate_value, 2, 2)
        total = QHBoxLayout()
        total.addLayout(radios)
        total.addStretch()
        total.addLayout(rate)
        self.setLayout(total)

    def makeConnections(self):
        '''Connect the widgets together'''

        # When one radio button is checked, change the combo box model
        # and un-check the other radio button
        self.rate.clicked.connect(self.setRateModel)
        self.lifetime.clicked.connect(self.setLifetimeModel)

        # If the text changes, emit that rate
        self.rate_value.editingFinished.connect(self.emitRate)

        # If the underlying model changes, adjust the text
        self.model.rateChanged.connect(self.updateRate)

        # If the unit changes, update rate
        self.unit.currentIndexChanged.connect(self.updateUnit)

    def setModel(self, model):
        '''Attaches models to the views'''
        self.model = model

    def setRate(self, rate):
        '''Set the rate manually'''
        self.rate_value.setText(str(rate))
        self.rate_value.editingFinished.emit()

    def setUnit(self, unit):
        '''Set the unit manually'''
        if unit == 's':
            self.lifetime.click()
            self.unit.setCurrentIndex(0)
        elif unit == 'ns':
            self.lifetime.click()
            self.unit.setCurrentIndex(1)
        elif unit == 'ps':
            self.lifetime.click()
            self.unit.setCurrentIndex(2)
        elif unit == 'fs':
            self.lifetime.click()
            self.unit.setCurrentIndex(3)
        elif unit in ('Hz', 'hz'):
            self.rate.click()
            self.unit.setCurrentIndex(0)
        elif unit in ('GHz', 'ghz'):
            self.rate.click()
            self.unit.setCurrentIndex(1)
        elif unit in ('THz', 'thz'):
            self.rate.click()
            self.unit.setCurrentIndex(2)
        elif unit in ('PHz', 'phz'):
            self.rate.click()
            self.unit.setCurrentIndex(3)
        else:
            error.showMessage('Invalid unit: {0}'.format(unit))

    #######
    # SLOTS
    #######

    def updateRate(self):
        '''Updates the rate of the text box'''
        # Do nothing if rate is not yet defined
        try:
            rate = self.model.rate
        except AttributeError:
            return
        if 0.1 > rate or rate > 100:
            self.rate_value.setText('{0:.3E}'.format(rate))
        else:
            self.rate_value.setText('{0:.3F}'.format(rate))

    def emitRate(self):
        '''Converts the text to a float and emits'''
        # Do nothing if there is no number
        try:
            self.model.setRate(float(self.rate_value.text()))
        except ValueError:
            pass

    def updateUnit(self):
        '''Update for a change of unit'''
        # If there is no unit yet, just set it
        try:
            unit = self.model.unit
        except AttributeError:
            self.model.setConverter(str(self.unit.currentText()))
            try:
                self.model.setRate(float(self.rate_value.text()))
            except ValueError:
                pass
            return
        # Convert unit appropriately
        if self.rate.isChecked():
            if unit == 'Hz':
                conv = { 'GHz' : 1E-9,
                         'THz' : 1E-12,
                         'PHz' : 1E-15 }
            elif unit == 'GHz':
                conv = { 'Hz'  : 1E9,
                         'THz' : 1E-3,
                         'PHz' : 1E-6 }
            elif unit == 'THz':
                conv = { 'Hz'  : 1E12,
                         'GHz' : 1E3,
                         'PHz' : 1E-3 }
            elif unit == 'PHz':
                conv = { 'Hz'  : 1E15,
                         'GHz' : 1E6,
                         'THz' : 1E3 }
            else:
                conv = { ''    : 1,
                         'Hz'  : 1, 
                         'GHz' : 1, 
                         'THz' : 1, 
                         'PHz' : 1, }
        else:
            if unit == 's':
                conv = { 'ns' : 1E9,
                         'ps' : 1E12,
                         'fs' : 1E15 }
            elif unit == 'ns':
                conv = { 's'  : 1E-9,
                         'ps' : 1E3,
                         'fs' : 1E6 }
            elif unit == 'ps':
                conv = { 's'  : 1E-12,
                         'ns' : 1E-3,
                         'fs' : 1E3 }
            elif unit == 'fs':
                conv = { 's'  : 1E-15,
                         'ns' : 1E-6,
                         'ps' : 1E-3 }
            else:
                conv = { ''   : 1,
                         's'  : 1, 
                         'ns' : 1, 
                         'ps' : 1, 
                         'fs' : 1, }
        try:
            # Set the new converter, then change the rate
            self.model.setConverter(str(self.unit.currentText()))
            try:
                self.model.setRate(float(self.rate_value.text())
                                 * conv[str(self.unit.currentText())])
            except ValueError:
                pass
        except KeyError:
            pass

        # Save the new unit
        self.model.unit = str(self.unit.currentText())

    def setRateModel(self):
        '''Change the model to use the rate'''
        if self.model.method == 'rate':
            return
        self.model.method = 'rate'
        indx = self.unit.currentIndex()
        self.unit.setModel(self.model.runits)
        self.model.unit = str(self.unit.itemText(indx))
        self.unit.setCurrentIndex(indx)
        self.model.setConverter(self.model.unit)
        try:
            self.model.setRate(1 / float(self.rate_value.text()))
        except (ZeroDivisionError, ValueError):
            pass

    def setLifetimeModel(self):
        '''Change the model to use the lifetime'''
        if self.model.method == 'lifetime':
            return
        self.model.method = 'lifetime'
        indx = self.unit.currentIndex()
        self.unit.setModel(self.model.lunits)
        self.model.unit = str(self.unit.itemText(indx))
        self.unit.setCurrentIndex(indx)
        self.model.setConverter(self.model.unit)
        try:
            self.model.setRate(1 / float(self.rate_value.text()))
        except (ZeroDivisionError, ValueError):
            pass
