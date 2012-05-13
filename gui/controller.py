from PyQt4.QtCore import pyqtSignal, QObject
from numpy import ndarray
from peak import PeakModel
from exchange import ExchangeModel, NumPeaks
from rate import Rate
from scale import Scale
from common import spectrum


class Controller(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the controller class'''
        super(QObject, self).__init__(parent)
        self.rate = Rate(self)
        self.numpeaks = NumPeaks(self)
        self.exchange = ExchangeModel(self)
        self.peak = PeakModel(self)
        self.scale = Scale(self)
        self._makeConnections()
        self.oldParams = None
        self.newParams = None
        self.rateParams = None
        self.exchangeParams = None
        self.limits = None

    def _makeConnections(self):
        '''Connect the contained widgets'''

        # When the number of peaks changes, change the matrix size
        self.numpeaks.numberOfPeaksChanged.connect(self.changeNumberOfPeaks)
        # When the number of peaks changes, also change the number of tab pages
        self.numpeaks.numberOfPeaksChanged.connect(self.peak.changePeakNum)

        # When any of the values are updated, replot
        self.rate.rateChanged.connect(self.setDataForPlot)
        self.exchange.matrixChanged.connect(self.setDataForPlot)
        self.peak.inputParamsChanged.connect(self.setDataForPlot)

        # Change the plot scale
        self.scale.scaleChanged.connect(self.changeScale)

    def getParametersForScript(self):
        '''Return the parameters in a format to make a script file'''
        xlim = self.limits[0], self.limits[1]
        reverse = self.limits[2]
        return xlim, reverse, self.oldParams, self.newParams

    def getParametersForInput(self):
        '''Return the parameters in a format to make an input file'''
        pass

    #######
    # SLOTS
    #######

    def changeNumberOfPeaks(self):
        '''Apply a change in the number of peaks'''
        self.exchange.resizeMatrix(self.numpeaks.numPeaks)

    def setDataForPlot(self):
        '''Assembles the data for plotting, calculates the spectrum, then emits'''

        # Assemble values
        omega = self.scale.getDomain()
        npeaks = self.numpeaks.getNumPeaks()
        k = self.rate.getConvertedRate()
        Z = self.exchange.getMatrix()
        self.oldParams = self.peak.getParams()
        vib, GL, GG, h = self.oldParams
        # Don's plot if there is some error
        if k == 0:
            return
        elif npeaks != len(vib):
            return
        elif npeaks != len(GL):
            return
        elif npeaks != len(GG):
            return
        elif npeaks != len(h):
            return
        elif npeaks != len(Z):
            return
        elif len(omega) == 0:
            return
        # Calculate spectrum
        I, self.newParams = spectrum(Z, k, vib, GL, GG, h, omega)
        # Send spectrum to plotter and new parameters to peak
        self.plotSpectrum.emit(omega, I)
        self.peak.setNewParams(*self.newParams)

        # Store data for later
        self.rateParams = self.rate.getParams()
        self.exchangeParams = self.exchange.getParams(npeaks)
        self.limits = self.scale.getScale()

    def changeScale(self, reverseOnly):
        '''Emit the new scale to use after replotting with new domain'''
        if not reverseOnly:
            self.setDataForPlot()
        min, max, rev = self.scale.getScale()
        self.newXLimits.emit(min, max, rev)
        
    #########
    # SIGNALS
    #########

    # Plot the data
    plotSpectrum = pyqtSignal(ndarray, ndarray)

    # Change the scale
    newXLimits = pyqtSignal(int, int, bool)
