from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve
from PyQt4.Qt import QFrame, QPalette, QColor, QPen
from PyQt4.QtCore import Qt, pyqtSignal
from numpy import array
from common import normalize, clip

class Plot(QwtPlot):
    '''A plot'''

    def __init__(self, parent, title = ''):
        '''Initiallize the plot and it's parent class'''
        super(QwtPlot, self).__init__(parent)
        self._setupPlot(title)

    def _setupPlot(self, title):
        '''Label plot axis and put a default function on the plot'''

        # Add a title if given
        if title:
            self.setTitle(title)

        # Set the axes for the intial data
        self.setAxisTitle(self.xBottom, "Frequency (Wavenumbers)")
        self.setAxisTitle(self.yLeft, "Intensity (Normalized)")
        self.setAxisScale(self.yLeft, -0.1, 1.1)

        # Make the background white and the line thick enough to see
        self.canvas().setLineWidth(2)
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        canvasPalette = QPalette(Qt.white)
        canvasPalette.setColor(QPalette.Foreground, Qt.gray)
        self.canvas().setPalette(canvasPalette)

        # Create the XY data points
        self.data = QwtPlotCurve()
        self.data.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.data.setPen(QPen(Qt.blue, 2))
        self.data.attach(self)

        # The raw (experimental) data, if any
        self.raw = QwtPlotCurve()
        self.raw.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.raw.setPen(QPen(Qt.darkGreen, 2))
        self.raw.attach(self)

        # Make sure the plot is wide enough
        self.setMinimumWidth(800)

    #######
    # SLOTS
    #######

    def plotFunction(self, x, y):
        '''Plot the given function'''
        y = normalize(y)
        self.data.setData(x, y)
        self.replot()

    def plotRawData(self, x, y):
        '''Plot the raw data'''
        y = normalize(y)
        # Clip the data to only the plotting window (to remove baseline)
        combined = array([[i, j] for i, j in zip(x, y)])
        s = self.axisScaleDiv(self.xBottom)
        xlim = s.lowerBound(), s.upperBound()
        if xlim[0] > xlim[1]:
            xlim[0], xlim[1] = xlim[1], xlim[0]
        combined = clip(combined, xlim)
        self.raw.setData(combined[:,0], combined[:,1])
        if not self.raw.isVisible():
            self.raw.show()
        self.replot()

    def clearRawData(self):
        '''Clear the raw data'''
        self.raw.hide()

    def changeScale(self, min, max, reversed):
        '''Change the axis scale'''
        if reversed:
            self.setAxisScale(self.xBottom, max, min)
        else:
            self.setAxisScale(self.xBottom, min, max)
        self.replot()

    #########
    # SIGNALS
    #########

