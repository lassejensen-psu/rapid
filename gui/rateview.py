from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QGroupBox
from numpy.testing import assert_approx_equal

class RateView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, model, title = 'Rate', parent = 0):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self.model = model
        self._createWidgets()
        self._initUI()
        self._makeConnections()

        # Default to rate in units of ps
        self.rate.click()
        self.unit.setCurrentIndex(1)

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        from PyQt4.QtCore import QString
        from PyQt4.QtGui import QLineEdit, QComboBox, QRadioButton, \
                                QDoubleValidator, QStringListModel

        # Rate or lifetime chooser
        self.rate = QRadioButton('Rate', self)
        self.lifetime = QRadioButton('Lifetime', self)

        # Box containing value
        self.rate_value = QLineEdit(self)
        self.rate_value.setValidator(QDoubleValidator(self.rate_value))

        # Lifetime and rate units
        lstr = QString('fs ps ns s').split(' ')
        rstr = QString('1/fs 1/ps 1/ns 1/s').split(' ')
        self.lifetimeunits = QStringListModel(lstr)
        self.rateunits     = QStringListModel(rstr)
        
        # Unit Box
        self.unit = QComboBox(self)

    def _initUI(self):
        '''Lays out the widgets'''
        from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QLabel
        radios = QHBoxLayout()
        radios.addWidget(self.rate)
        radios.addWidget(self.lifetime)
        units = QHBoxLayout()
        units.addWidget(QLabel("Unit"))
        units.addWidget(self.unit)
        rate = QHBoxLayout()
        rate.addWidget(QLabel("Value"))
        rate.addWidget(self.rate_value)
        total = QVBoxLayout()
        total.addLayout(radios)
        total.addLayout(units)
        total.addLayout(rate)
        self.setLayout(total)

    def _makeConnections(self):
        '''Connect the widgets together'''

        # When one radio button is checked, change the combo box model
        # and unche the other radio button
        self.rate.clicked.connect(self.setRateModel)
        self.lifetime.clicked.connect(self.setLifetimeModel)

        # If the unit is changed, change the converter
        self.unit.currentIndexChanged[str].connect(self.model.setConverter)

        # If the text changes, emit that rate
        self.rate_value.editingFinished.connect(self.emitRate)

        # If the underlying model changes, adjust the text
        self.model.rateInUnits.connect(self.setRate)

    #######
    # SLOTS
    #######

    def setRate(self, rate):
        '''Sets the rate of the text box'''
        try:
            assert_approx_equal(rate, float(self.rate_value.text()))
        except AssertionError: 
            self.rate_value.setText(repr(rate))

    def emitRate(self):
        '''Converts the text to a float and emits'''
        self.model.setRate(float(self.rate_value.text()))

    def setRateModel(self):
        '''Change the model to use the rate'''
        indx = self.unit.currentIndex()
        self.unit.setModel(self.rateunits)
        self.unit.setCurrentIndex(indx)

    def setLifetimeModel(self):
        '''Change the model to use the lifetime'''
        indx = self.unit.currentIndex()
        self.unit.setModel(self.lifetimeunits)
        self.unit.setCurrentIndex(indx)
