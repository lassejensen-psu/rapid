from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QTabWidget, QVBoxLayout, QWidget, QLineEdit, \
                        QDoubleSpinBox, QLabel, QGridLayout

class PeakView(QTabWidget):
    '''Class to display the peak information'''

    def __init__(self, parent = None):
        '''Initiallize'''
        super(QTabWidget, self).__init__(parent)
        self._createWidgets()
        self.addTab(self.pages[0], self.pages[0].title)
        self.addTab(self.pages[1], self.pages[1].title)

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        self.pages = [
                      PeakPage("Peak 1"),
                      PeakPage("Peak 2"),
                      PeakPage("Peak 3"),
                      PeakPage("Peak 4"),
                    ]

    def initUI(self):
        '''Initilizes the layout of the contained widgets'''
        pass

    def makeConnections(self):
        '''Connect all the contained widgets togeter'''
        pass

    def setModel(self, model):
        '''Attaches a model to this view'''
        self.model = model

class PeakPage(QWidget):
    '''A peak page widget'''

    def __init__(self, title):
        '''Initiallize'''
        super(QWidget, self).__init__()
        self.title = title
        self._createWidgets()
        self._initUI()

    def _createWidgets(self):
        '''Create the contained widgets'''
        self.inputpeak = QDoubleSpinBox(self)
        self.inputGL   = QDoubleSpinBox(self)
        self.inputGG   = QDoubleSpinBox(self)
        self.inputH    = QDoubleSpinBox(self)
        self.newpeak   = QLineEdit(self)
        self.newGL     = QLineEdit(self)
        self.newGG     = QLineEdit(self)
        self.newH      = QLineEdit(self)

        self.inputpeak.setRange(300.0, 3000.0)
        self.inputGL.setRange(0.0, 100.0)
        self.inputGG.setRange(0.0, 100.0)
        self.inputH.setRange(0.0, 1.0)
        self.inputpeak.setDecimals(3)
        self.inputGL.setDecimals(3)
        self.inputGG.setDecimals(3)
        self.inputH.setDecimals(3)

        self.newpeak.setReadOnly(True)
        self.newGL.setReadOnly(True)
        self.newGG.setReadOnly(True)
        self.newH.setReadOnly(True)

    def _initUI(self):
        '''Layout the contained widgets'''
        lo = QGridLayout()
        lo.addWidget(QLabel("Input Value"), 1, 2)
        lo.addWidget(QLabel("New Value"), 1, 4)
        lo.addWidget(QLabel("Peak"), 2, 1)
        lo.addWidget(self.inputpeak, 2, 2)
        lo.addWidget(QLabel("-->"), 2, 3)
        lo.addWidget(self.newpeak, 2, 4)
        lo.addWidget(QLabel("Lorentz FWHM"), 3, 1)
        lo.addWidget(self.inputGL, 3, 2)
        lo.addWidget(QLabel("-->"), 3, 3)
        lo.addWidget(self.newGL, 3, 4)
        lo.addWidget(QLabel("Gauss FWHM"), 4, 1)
        lo.addWidget(self.inputGG, 4, 2)
        lo.addWidget(QLabel("-->"), 4, 3)
        lo.addWidget(self.newGG, 4, 4)
        lo.addWidget(QLabel("Height"), 5, 1)
        lo.addWidget(self.inputH, 5, 2)
        lo.addWidget(QLabel("-->"), 5, 3)
        lo.addWidget(self.newH, 5, 4)
        self.setLayout(lo)     

    ######
    # SLOT
    ######

    def viewNewParams(self, p, GL, GG, h):
        '''View the new parameters after exchange'''
        self.newpeak.setText('{0:.3f}'.format(p))
        self.newGL.setText('{0:.3f}'.format(GL))
        self.newGG.setText('{0:.3f}'.format(GG))
        self.newH.setText('{0:.3f}'.format(h))

    #########
    # SIGNALS
    #########

class PeakModel(QObject):
    '''Class to hold all information about the peaks'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.peaks = [0.0, 0.0, 0.0, 0.0]
        self.GL    = [0.0, 0.0, 0.0, 0.0]
        self.GG    = [0.0, 0.0, 0.0, 0.0]
        self.h     = [0.0, 0.0, 0.0, 0.0]

    ######
    # SLOT
    ######

    def setNewParams(self, p, GL, GG, h):
        '''Set the parameters after exchange'''
        pass

    #########
    # SIGNALS
    #########

    releaseParams = pyqtSignal(list, list, list, list)
