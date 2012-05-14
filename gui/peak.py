from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QTabWidget, QVBoxLayout, QWidget, QLineEdit, \
                        QDoubleValidator, QLabel, QGridLayout
from numpy import asarray, nan

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

    def setPeaks(self, vib, GL, GG, h):
        '''Manually set the peak data'''
        for i, vals in enumerate(zip(vib, GL, GG, h)):
            self.pages[i].setParams(*vals)

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
        self.inputpeak = QLineEdit(self)
        self.inputGL   = QLineEdit(self)
        self.inputGG   = QLineEdit(self)
        self.inputH    = QLineEdit(self)
        self.newpeak   = QLineEdit(self)
        self.newGL     = QLineEdit(self)
        self.newGG     = QLineEdit(self)
        self.newH      = QLineEdit(self)

        self.inputpeak.setValidator(QDoubleValidator(300.0, 3000.0, 1,
                                                     self.inputpeak))
        self.inputGL.setValidator(QDoubleValidator(0.0, 100.0, 3,
                                                   self.inputGL))
        self.inputGG.setValidator(QDoubleValidator(0.0, 100.0, 3,
                                                   self.inputGG))
        self.inputH.setValidator(QDoubleValidator(0.0, 1.0, 3,
                                                  self.inputH))

        self.newpeak.setReadOnly(True)
        self.newGL.setReadOnly(True)
        self.newGG.setReadOnly(True)
        self.newH.setReadOnly(True)

        self.inputpeak.setToolTip('The vibrational frequency of this peak, '
                                  'in wavenumbers')
        self.inputGL.setToolTip('The Lorentzian FWHM broadening of this peak, '
                                'in wavenumbers')
        self.inputGG.setToolTip('The Gaussian FWHM broadening of this peak, '
                                'in wavenumbers')
        self.inputH.setToolTip('The relative height of this peak')
        self.newpeak.setToolTip('The vibrational frequency after exchange')
        self.newGL.setToolTip('The Gaussian FWHM after exchange')
        self.newGG.setToolTip('The Lorentzian FWHM after exchange')
        self.newH.setToolTip('The relative height after exchange')

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
        self.inputpeak.editingFinished.connect(self.inputParamsChanged)
        self.inputGL.editingFinished.connect(self.inputParamsChanged)
        self.inputGG.editingFinished.connect(self.inputParamsChanged)
        self.inputH.editingFinished.connect(self.inputParamsChanged)

    def viewNewParams(self, p, GL, GG, h):
        '''View the new parameters after exchange'''
        self.newpeak.setText('{0:.1f}'.format(p))
        self.newGL.setText('{0:.3f}'.format(GL))
        self.newGG.setText('{0:.3f}'.format(GG))
        self.newH.setText('{0:.3f}'.format(h))

    def setParams(self, p, GL, GG, h):
        '''Manually set the parameters on this page'''
        self.inputpeak.setText('{0:.1f}'.format(p))
        self.inputGL.setText('{0:.3f}'.format(GL))
        self.inputGG.setText('{0:.3f}'.format(GG))
        self.inputH.setText('{0:.3f}'.format(h))
        # Force an updata of the data
        self.inputpeak.editingFinished.emit()

    #######
    # SLOTS
    #######

    def inputParamsChanged(self):
        '''Collects the parameters from this page and broadcasts them'''
        vib = self.inputpeak.text().toFloat()
        GL  = self.inputGL.text().toFloat()
        GG  = self.inputGG.text().toFloat()
        h   = self.inputH.text().toFloat()
        # First check that float conversion was a success for all params
        # Of not, don't pass on data
        if not (vib[1] and GL[1] and GG[1] and h[1]):
            return
        self.changeInputParams.emit(self.ID, vib[0], GL[0], GG[0], h[0])

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
        #self.peaks    = [1960.0, 1980.0, 2000.0, 2020.0]
        self.peaks    = [nan, nan, nan, nan]
        self.GL       = [nan, nan, nan, nan]
        #self.GL       = [5.0, 5.0, 5.0, 5.0]
        self.GG       = [nan, nan, nan, nan]
        #self.GG       = [5.0, 5.0, 5.0, 5.0]
        self.h        = [nan, nan, nan, nan]
        #self.h        = [1.0, 1.0, 1.0, 1.0]
        self.newpeaks = [0.0, 0.0, 0.0, 0.0]
        self.newGL    = [0.0, 0.0, 0.0, 0.0]
        self.newGG    = [0.0, 0.0, 0.0, 0.0]
        self.newh     = [0.0, 0.0, 0.0, 0.0]

    def getParams(self):
        '''Return the input parameters for the given number of peaks'''
        return (asarray(self.peaks[:self.npeaks]),
                asarray(self.GL[:self.npeaks]),
                asarray(self.GG[:self.npeaks]),
                asarray(self.h[:self.npeaks]))

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
