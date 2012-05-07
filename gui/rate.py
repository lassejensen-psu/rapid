from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QGroupBox
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
        from PyQt4.QtCore import QString
        from PyQt4.QtGui import QComboBox, QRadioButton, \
                                QDoubleSpinBox, QStringListModel

        # Rate or lifetime chooser
        self.rate = QRadioButton('Rate (THz)', self)
        self.lifetime = QRadioButton('Lifetime (ps)', self)

        # Box containing value
        self.rate_value = QDoubleSpinBox(self)
        self.rate_value.setRange(0.001, 100.0)
        self.rate_value.setDecimals(3)
        self.rate_value.setSingleStep(0.1)

    def initUI(self):
        '''Lays out the widgets'''
        from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QLabel
        radios = QHBoxLayout()
        radios.addWidget(self.rate)
        radios.addWidget(self.lifetime)
        rate = QHBoxLayout()
        rate.addWidget(QLabel("Value: "))
        rate.addWidget(self.rate_value)
        total = QVBoxLayout()
        total.addLayout(radios)
        total.addLayout(rate)
        self.setLayout(total)

    def makeConnections(self):
        '''Connect the widgets together'''

        # When one radio button is checked, change the combo box model
        # and unche the other radio button
        self.rate.clicked.connect(self.setRateModel)
        self.lifetime.clicked.connect(self.setLifetimeModel)

        # If the text changes, emit that rate
        self.rate_value.valueChanged.connect(self.emitRate)

        # If the underlying model changes, adjust the text
        self.model.rateChanged.connect(self.updateRate)

    def setModel(self, model):
        '''Attaches models to the views'''
        self.model = model

    #######
    # SLOTS
    #######

    def updateRate(self):
        '''Updates the rate of the text box'''
        #try:
        #    assert_approx_equal(rate, float(self.rate_value.text()))
        #except AssertionError: 
        self.rate_value.setValue(self.model.rate)

    def emitRate(self):
        '''Converts the text to a float and emits'''
        self.model.setRate(self.rate_value.value())

    def setRateModel(self):
        '''Change the model to use the rate'''
        self.model.setConverter('ps')

    def setLifetimeModel(self):
        '''Change the model to use the lifetime'''
        self.model.setConverter('THz')

