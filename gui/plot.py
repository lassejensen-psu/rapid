from PyQt4.Qwt5 import QwtPlot
from PyQt4.Qt import QFrame, QPalette, QColor, QPen
from PyQt4.QtCore import Qt, pyqtSignal
from xypoints import XYPoints

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
        self.setAxisScale(self.xBottom, 0.0, 10.0)
        self.setAxisTitle(self.yLeft, "f(x)")
        self.setAxisScale(self.yLeft, -10.0, 10.0)

        # Make the background white and the line thick enough to see
        self.canvas().setLineWidth(2)
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        canvasPalette = QPalette(Qt.white)
        canvasPalette.setColor(QPalette.Foreground, Qt.gray)
        self.canvas().setPalette(canvasPalette)

        # Create the XY data points and default the function to sin()
        self.data = XYPoints(nPoints=1000)
        self.data.setPen(QPen(Qt.blue))
        self.data.attach(self)
 
        # Initiallize the data
        self.data.setDomain(0.0, 10.0)

    #######
    # SLOTS
    #######

    def plotFunction(self, function):
        '''Plot the given function'''
        self.data.setFunctionData(function)
        self.replot()

    #########
    # SIGNALS
    #########

