from __future__ import print_function, division, absolute_import

# Non-std. lib imports
from PySide.QtGui import QFrame, QPalette, QColor, QPen, QApplication
from PySide.QtCore import Qt, Signal
from pyqtgraph import PlotWidget, ViewBox
from numpy import array
from random import random

# Local imports
from common import normalize, clip
from .guicommon import error


class Plot(PlotWidget):
    '''A plot'''

    def __init__(self, parent, title = ''):
        '''Initialize the plot and it's parent class'''
        border = {'color': 0.5, 'width': 2}
        super(Plot, self).__init__(parent,
                                   viewBox=ViewBox(border=border))
        self._setupPlot(title)

    def _setupPlot(self, title):
        '''Label plot axis and put a default function on the plot'''

        # Add a title if given
        if title:
            self.setTitle(title)
        self.rawData = None

        # Default to not-reversed
        self.reversed = False

        # Set the axes for the intial data
        self.getPlotItem().setLabel('bottom', "Frequency (Wavenumbers, cm<sup>-1</sup>)")
        self.getPlotItem().getAxis('bottom').setPen('k')
        self.getPlotItem().setLabel('left', "Intensity (Normalized)")
        self.getPlotItem().getAxis('left').setPen('k')
        self.getPlotItem().setYRange(0, 1.1, padding=0)

        # # Make the background white and the line thick enough to see
        self.setBackground('w')  # White

        # Create the XY data points.  Empty for now.
        self.data = self.getPlotItem().plot([], [],
                                            antialias=True,
                                            connect='all',
                                            pen={'color': 'b', 'width': 2})

        # The raw (experimental) data, if any
        self.raw = self.getPlotItem().plot([], [],
                                           antialias=True,
                                           connect='all',
                                           pen={'color': 'g', 'width': 2})

        # # Make sure the plot is wide enough
        self.setMinimumWidth(850)

    def makeConnections(self):
        '''Connect the plot together'''
        self.scene().sigMouseMoved.connect(self.catchSelection)

    def calculatedData(self):
        '''Return the calculated data'''
        x, y = self.data.getData()
        return array(x), array(y)

    def getRawData(self):
        '''Return the raw data in same format it was read in'''
        x, y = self.raw.getData()
        return array([x, y]).T

    def setRawData(self, raw):
        '''Stores the raw data internally'''
        self.rawData = raw

    def plotRawData(self):
        '''Plot the raw data'''
        if self.rawData is None:
            error.showMessage("Cannot plot raw data, none has been given")
            return
        xlim = self.data.dataBounds(0)
        if xlim[0] > xlim[1]:
            xlim[0], xlim[1] = xlim[1], xlim[0]
        # Clip the data to only the plotting window (to remove baseline)
        raw = clip(self.rawData.copy(), xlim)
        raw[:,1] = normalize(raw[:,1])
        self.raw.setData(raw[:,0], raw[:,1])
        if not self.raw.isVisible():
            self.raw.show()
        self.replot()

    #######
    # SLOTS
    #######

    def plotCalculatedData(self, x, y):
        '''Plot the calculated data'''
        try:
            y = normalize(y)
        except ValueError:  # Occurs on startup
            return
        self.data.setData(x, y)
        self.replot()

    def clearRawData(self):
        '''Clear the raw data'''
        self.rawData = None
        self.raw.clear()

    def changeScale(self, min, max, reversed):
        '''Change the axis scale'''
        self.reversed = reversed
        self.getPlotItem().invertX(reversed)
        self.getPlotItem().setXRange(min, max)
        x, y = self.calculatedData()
        self.plotCalculatedData(x, y)
        if self.rawData is not None:
            self.plotRawData()

    def catchSelection(self, point):
        '''Catch a point and re-emit'''
        p = self.getPlotItem().getViewBox().mapSceneToView(point)
        self.pointPicked.emit(p.x(), p.y())

    #########
    # SIGNALS
    #########

    pointPicked = Signal(float, float)
