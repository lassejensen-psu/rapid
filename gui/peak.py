from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QTabWidget, QVBoxLayout, QWidget, QLineEdit, \
                        QDoubleSpinBox, QLabel, QGridLayout

class PeakView(QTabWidget):
    '''Class to display the peak information'''

    def __init__(self, parent = None):
        '''Initiallize'''
        super(QTabWidget, self).__init__(parent)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        self.pages = [
                      PeakPage("Peak 1", 0),
                      PeakPage("Peak 2", 1),
                      PeakPage("Peak 3", 2),
                      PeakPage("Peak 4", 3),
                    ]

    def initUI(self):
        '''Initilizes the layout of the contained widgets'''
        self.addTab(self.pages[0], self.pages[0].title)
        self.addTab(self.pages[1], self.pages[1].title)
        self.npeaks = 2
        # Fill the pages with some default values
        self.pages[0].inputpeak.setValue(self.model.peaks[0])
        self.pages[0].inputGL.setValue(self.model.GL[0])
        self.pages[0].inputGG.setValue(self.model.GG[0])
        self.pages[0].inputH.setValue(self.model.h[0])
        self.pages[1].inputpeak.setValue(self.model.peaks[1])
        self.pages[1].inputGL.setValue(self.model.GL[1])
        self.pages[1].inputGG.setValue(self.model.GG[1])
        self.pages[1].inputH.setValue(self.model.h[1])
        self.pages[2].inputpeak.setValue(self.model.peaks[2])
        self.pages[2].inputGL.setValue(self.model.GL[2])
        self.pages[2].inputGG.setValue(self.model.GG[2])
        self.pages[2].inputH.setValue(self.model.h[2])
        self.pages[3].inputpeak.setValue(self.model.peaks[3])
        self.pages[3].inputGL.setValue(self.model.GL[3])
        self.pages[3].inputGG.setValue(self.model.GG[3])
        self.pages[3].inputH.setValue(self.model.h[3])

    def makeConnections(self):
        '''Connect all the contained widgets togeter'''
        self.model.newParams.connect(self.distributeNewParams)
        self.model.changeNumPeaks.connect(self.changePeakNum)
        self.pages[0].changeInputParams.connect(self.model.setInputParams)
        self.pages[1].changeInputParams.connect(self.model.setInputParams)
        self.pages[2].changeInputParams.connect(self.model.setInputParams)
        self.pages[3].changeInputParams.connect(self.model.setInputParams)

    def setModel(self, model):
        '''Attaches a model to this view'''
        self.model = model

    #######
    # SLOTS
    #######

    def distributeNewParams(self, p, GL, GG, h):
        '''When the new parameters are given, send the results to the
        appropriate page'''
        for i, vals in enumerate(zip(p, GL, GG, h)):
            self.pages[i].viewNewParams(*vals)

    def changePeakNum(self, npeaks):
        '''Change the number of peaks by adding or removing tabs'''
        if self.npeaks == 2:
            if npeaks == 3:
                self.addTab(self.pages[2], self.pages[2].title)
                self.npeaks = 3
            elif npeaks == 4:
                self.addTab(self.pages[2], self.pages[2].title)
                self.addTab(self.pages[3], self.pages[3].title)
                self.npeaks = 4
        elif self.npeaks == 3:
            if npeaks == 2:
                self.removeTab(2)
                self.npeaks = 2
            elif npeaks == 4:
                self.addTab(self.pages[3], self.pages[3].title)
                self.npeaks = 4
        elif self.npeaks == 4:
            if npeaks == 2:
                self.removeTab(3)
                self.removeTab(2)
                self.npeaks = 2
            elif npeaks == 3:
                self.removeTab(3)
                self.npeaks = 3

class PeakPage(QWidget):
    '''A peak page widget'''

    def __init__(self, title, ID):
        '''Initiallize'''
        super(QWidget, self).__init__()
        self.title = title
        self.ID = ID
        self._createWidgets()
        self._initUI()
        self._makeConnections()

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

    def _makeConnections(self):
        '''Connect the conatined widgets together'''
        self.inputpeak.valueChanged.connect(self.inputParamsChanged)
        self.inputGL.valueChanged.connect(self.inputParamsChanged)
        self.inputGG.valueChanged.connect(self.inputParamsChanged)
        self.inputH.valueChanged.connect(self.inputParamsChanged)

    def viewNewParams(self, p, GL, GG, h):
        '''View the new parameters after exchange'''
        self.newpeak.setText('{0:.3f}'.format(p))
        self.newGL.setText('{0:.3f}'.format(GL))
        self.newGG.setText('{0:.3f}'.format(GG))
        self.newH.setText('{0:.3f}'.format(h))

    #######
    # SLOTS
    #######

    def inputParamsChanged(self):
        '''Collects the parameters from this page and broadcasts them'''
        self.changeInputParams.emit(self.ID,
                                    self.inputpeak.value(),
                                    self.inputGL.value(),
                                    self.inputGG.value(),
                                    self.inputH.value())

    #########
    # SIGNALS
    #########

    # Signals for when a value is changed
    changeInputParams = pyqtSignal(int, float, float, float, float)

class PeakModel(QObject):
    '''Class to hold all information about the peaks'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.npeaks = 0
        self.peaks    = [2000.0, 2000.0, 2000.0, 2000.0]
        self.GL       = [5.0, 5.0, 5.0, 5.0]
        self.GG       = [5.0, 5.0, 5.0, 5.0]
        self.h        = [1.0, 1.0, 1.0, 1.0]
        self.newpeaks = [0.0, 0.0, 0.0, 0.0]
        self.newGL    = [0.0, 0.0, 0.0, 0.0]
        self.newGG    = [0.0, 0.0, 0.0, 0.0]
        self.newh     = [0.0, 0.0, 0.0, 0.0]

    #######
    # SLOTS
    #######

    def setNewParams(self, p, GL, GG, h):
        '''Set the parameters after exchange'''

        # First, replace the values in the lists
        for i, vals in enumerate(zip(p, GL, GG, h)):
            self.newpeaks[i] = vals[0]
            self.newGL[i]    = vals[1]
            self.newGG[i]    = vals[2]
            self.newh[i]     = vals[3]

        # Now broadcast results
        self.newParams.emit(p, GL, GG, h)

    def changePeakNum(self, npeaks):
        '''Change the number of peaks'''
        self.npeaks = npeaks
        self.changeNumPeaks.emit(self.npeaks)

    def setInputParams(self, num, p, GL, GG, h):
        '''Set the input parameter for a given peak, then emit'''
        self.peaks[num] = p
        self.GL[num] = GL
        self.GG[num] = GG
        self.h[num] = h
        self.inputParamsChanged.emit()

    #########
    # SIGNALS
    #########

    # Release the parameters to calculate the spectrum
    inputParamsChanged = pyqtSignal()

    # View the new parameters after exchange
    newParams = pyqtSignal(list, list, list, list)

    # Change the number of peaks
    changeNumPeaks = pyqtSignal(int)
