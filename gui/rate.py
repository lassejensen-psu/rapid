from PyQt4.QtCore import pyqtSignal, QObject, QString
from PyQt4.QtGui import QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, \
                        QComboBox, QRadioButton, QStringListModel, \
                        QLineEdit, QDoubleValidator, QGridLayout
from numpy.testing import assert_approx_equal
from math import pi
HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )

class Rate(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.rate = 0
        self.wn_rate = 0
        self.converter = lambda x: x
        self.lunits = QStringListModel(QString('s ns ps fs').split(' '))
        self.runits = QStringListModel(QString('Hz GHz THz PHz').split(' '))
        self.unit = 'THz'
        self.method = ''

    def setConverter(self, unit):
        '''Sets the function to perform rate conversion to cm^{-1}'''

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
            self.converter = conv[str(unit)]
        except KeyError:
            pass # This happens when we set a new model.  Ignore

    #######
    # SLOTS
    #######

    def setRate(self, rate):
        '''Sets the rate and emits the result'''
        self.rate = rate
        self.wn_rate = self.converter(self.rate)
        self.rateChanged.emit()

    #########
    # SIGNALS
    #########

    # The rate changed
    rateChanged = pyqtSignal()

#/\/\/\/\/\/\/\
# The rate view
#/\/\/\/\/\/\/\

class RateView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Rate', parent = None):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''

        # Rate or lifetime chooser
        self.rate = QRadioButton('Rate', self)
        self.lifetime = QRadioButton('Lifetime', self)

        # Box containing value
        self.rate_value = QLineEdit(self)
        validate = QDoubleValidator()
        validate.setDecimals(3)
        validate.setBottom(0.0)
        self.rate_value.setValidator(validate)

        # Unit
        self.unit = QComboBox(self)

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
        # and unche the other radio button
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

    #######
    # SLOTS
    #######

    def updateRate(self):
        '''Updates the rate of the text box'''
        self.rate_value.setText('{0:.3G}'.format(self.model.rate))

    def emitRate(self):
        '''Converts the text to a float and emits'''
        self.model.setRate(self.rate_value.text().toFloat()[0])

    def updateUnit(self):
        '''Update for a change of unit'''
        # Convert unit appropriately
        if self.rate.isChecked():
            if self.model.unit == 'Hz':
                conv = { 'GHz' : 1E-9,
                         'THz' : 1E-12,
                         'PHz' : 1E-15 }
            elif self.model.unit == 'GHz':
                conv = { 'Hz'  : 1E9,
                         'THz' : 1E-3,
                         'PHz' : 1E-6 }
            elif self.model.unit == 'THz':
                conv = { 'Hz'  : 1E12,
                         'GHz' : 1E3,
                         'PHz' : 1E-3 }
            elif self.model.unit == 'PHz':
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
            if self.model.unit == 's':
                conv = { 'ns' : 1E9,
                         'ps' : 1E12,
                         'fs' : 1E15 }
            elif self.model.unit == 'ns':
                conv = { 's'  : 1E-9,
                         'ps' : 1E3,
                         'fs' : 1E6 }
            elif self.model.unit == 'ps':
                conv = { 's'  : 1E-12,
                         'ns' : 1E-3,
                         'fs' : 1E3 }
            elif self.model.unit == 'fs':
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
            self.model.setRate(self.rate_value.text().toFloat()[0]
                             * conv[str(self.unit.currentText())])
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
            self.model.setRate(1/self.rate_value.text().toFloat()[0])
        except ZeroDivisionError:
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
            self.model.setRate(1/self.rate_value.text().toFloat()[0])
        except ZeroDivisionError:
            pass
