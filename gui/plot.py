from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotPicker
from PyQt4.Qt import QFrame, QPalette, QColor, QPen
from PyQt4.QtCore import Qt, pyqtSignal
from numpy import array
from common import normalize, clip
from guicommon import error

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
        self.rawData = None

        # Set the axes for the intial data
        self.setAxisTitle(self.xBottom, "Frequency (Wavenumbers, cm<sup>-1</sup>)")
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

        # Get a plot picker to get the current coordinates
        self.picker = QwtPlotPicker(
                        QwtPlot.xBottom,
                        QwtPlot.yLeft,
                        QwtPlotPicker.PointSelection | QwtPlotPicker.DragSelection,
                        QwtPlotPicker.CrossRubberBand,
                        QwtPlotPicker.ActiveOnly,
                        self.canvas())
        self.picker.setRubberBandPen(QPen(Qt.black))
        self.picker.setTrackerPen(QPen(Qt.red))

    def makeConnections(self):
        '''Connect the plot together'''
        self.picker.selected.connect(self.catchSelection)
        self.picker.moved.connect(self.catchSelection)

    def calculatedData(self):
        '''Return the calculated data'''
        x = array(self.data.data().xData())
        y = array(self.data.data().yData())
        return x, y

    def getRawData(self):
        '''Return the raw data in same format it was read in'''
        x = array(self.raw.data().xData())
        y = array(self.raw.data().yData())
        return array([x, y]).T

    def setRawData(self, raw):
        '''Stores the raw data internally'''
        self.rawData = raw

    def plotRawData(self):
        '''Plot the raw data'''
        if self.rawData is None:
            error.showMessage("Cannot plot raw data, none has been given")
            return
        s = self.axisScaleDiv(self.xBottom)
        xlim = [s.lowerBound(), s.upperBound()]
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
        y = normalize(y)
        self.data.setData(x, y)
        self.replot()

    def clearRawData(self):
        '''Clear the raw data'''
        self.raw.hide()
        self.rawData = None
        self.replot()

    def changeScale(self, min, max, reversed):
        '''Change the axis scale'''
        if reversed:
            self.setAxisScale(self.xBottom, max, min)
        else:
            self.setAxisScale(self.xBottom, min, max)
        self.replot()
        if self.rawData is not None:
            self.plotRawData()

    def catchSelection(self, point):
        '''Catch a point and re-emit'''
        self.pointPicked.emit(point.x(), point.y())

    #########
    # SIGNALS
    #########

    pointPicked = pyqtSignal(float, float)
