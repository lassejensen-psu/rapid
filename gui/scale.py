from PyQt4.QtCore import pyqtSignal, QObject, QString
from PyQt4.QtGui import QGroupBox, QHBoxLayout, QLabel, \
                        QLineEdit, QIntValidator, QCheckBox, \
                        QErrorMessage

class Scale(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.xmin = 1800
        self.xmax = 2100
        self.reverse = False

    #######
    # SLOTS
    #######

    def setScale(self, min, max, reversed):
        '''Sets the rate and emits the result'''
        self.xmin = min
        self.xmax = max
        self.reverse = reversed
        self.scaleChanged.emit()

    #########
    # SIGNALS
    #########

    # The rate changed
    scaleChanged = pyqtSignal()

#/\/\/\/\/\/\/\/
# The scale view
#/\/\/\/\/\/\/\/

class ScaleView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Window Limits', parent = None):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self.error = QErrorMessage()
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
            self.error.showMessage(err)
            return
        self.model.setScale(xmin, xmax, reverse)
