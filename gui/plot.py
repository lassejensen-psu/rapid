from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve
from PyQt4.Qt import QFrame, QPalette, QColor, QPen
from PyQt4.QtCore import Qt, pyqtSignal
from common import normalize

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
        self.setAxisTitle(self.xBottom, "x")
        self.setAxisScale(self.xBottom, 1950.0, 2050.0)
        self.setAxisTitle(self.yLeft, "f(x)")
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
        self.data.setPen(QPen(Qt.blue))
        self.data.attach(self)

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

    #########
    # SIGNALS
    #########

