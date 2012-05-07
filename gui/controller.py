from PyQt4.QtCore import pyqtSignal, QObject
from numpy import ndarray, asarray
from peak import PeakModel
from exchange import ExchangeModel, NumPeaks
from rate import Rate
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
        self._makeConnections()

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

    #######
    # SLOTS
    #######

    def changeNumberOfPeaks(self):
        '''Apply a change in the number of peaks'''
        self.exchange.resizeMatrix(self.numpeaks.numPeaks)

    def setDataForPlot(self):
        '''Assembles the data for plotting, calculates the spectrum, then emits'''

        # Assemble values
        npeaks = self.numpeaks.numPeaks
        k = self.rate.wn_rate
        Z = self.exchange.matrix
        vib = asarray(self.peak.peaks[:npeaks])
        GL = asarray(self.peak.GL[:npeaks])
        GG = asarray(self.peak.GG[:npeaks])
        h = asarray(self.peak.h[:npeaks])
        # Calculate spectrum
        I, omega, newParams = spectrum(Z, k, vib, GL, GG, h)
        # Send spectrum to plotter and new parameters to peak
        self.plotSpectrum.emit(omega, I)
        self.peak.setNewParams(*newParams)

    #########
    # SIGNALS
    #########

    # Plot the data
    plotSpectrum = pyqtSignal(ndarray, ndarray)
