from __future__ import print_function, division, absolute_import

# Non-std. lib imports
from PySide.QtCore import Signal, QObject
from numpy import ndarray, isnan, sum

# Local imports
from rapid.common import spectrum
from rapid.gui.peak import PeakModel
from rapid.gui.exchange import ExchangeModel, NumPeaks
from rapid.gui.rate import Rate
from rapid.gui.scale import Scale


class Controller(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initialize the controller class'''
        super(Controller, self).__init__(parent)
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
        self.hasPlot = False

    def _makeConnections(self):
        '''Connect the contained widgets'''

        # When the number of peaks changes, change the matrix size
        self.numpeaks.numberOfPeaksChanged.connect(self.changeNumberOfPeaks)
        # When the number of peaks changes, also change the number of tab pages
        self.numpeaks.numberOfPeaksChanged.connect(self.peak.changePeakNum)

        # When any of the values are updated, re-plot
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
        rate = self.rate.getParams()
        exchange = self.exchange.getParams(self.numpeaks.getNumPeaks())
        xlim = self.limits[0], self.limits[1]
        reverse = self.limits[2]
        return xlim, reverse, rate, exchange, self.oldParams

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
        if k == 0 or k is None:
            return
        elif npeaks != len(vib) or isnan(sum(vib)):
            return
        elif npeaks != len(GL) or isnan(sum(GL)):
            return
        elif npeaks != len(GG) or isnan(sum(GG)):
            return
        elif npeaks != len(h) or isnan(sum(h)):
            return
        elif npeaks != len(Z):
            return
        elif len(omega) == 0:
            return
        else:
            self.hasPlot = True
        # Calculate spectrum
        I, self.newParams = spectrum(Z, k, vib, GL, GG, h, omega)
        # Send spectrum to plotter and new parameters to peak
        self.plotSpectrum.emit(omega, I)
        self.peak.setNewParams(*self.newParams)

        # Store data for later
        self.rateParams = self.rate.getParams()
        self.exchangeParams = self.exchange.getParams(npeaks)
        self.limits = self.scale.getScale()

    def changeScale(self, recalculate):
        '''Emit the new scale to use after re-plotting with new domain'''
        if recalculate:
            self.setDataForPlot()
        min, max, rev = self.scale.getScale()
        self.newXLimits.emit(min, max, rev)
        
    #########
    # SIGNALS
    #########

    # Plot the data
    plotSpectrum = Signal(ndarray, ndarray)

    # Change the scale
    newXLimits = Signal(int, int, bool)
