from PyQt4.QtCore import pyqtSignal, QObject
#from peak_data_model import PeakData
from exchange import ExchangeModel, NumPeaks
from rate import Rate


class Controller(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent, exchangeparent):
        '''Initiallize the controller class'''
        super(QObject, self).__init__(parent)
        self.rate = Rate(self)
        self.numpeaks = NumPeaks(self)
        self.exchange = ExchangeModel(exchangeparent)
        self._makeConnections()


    def _makeConnections(self):
        '''Connect the contained widgets'''

        # When the number of peaks changes, change the matrix size
        self.numpeaks.numberOfPeaksChanged.connect(self.changeNumberOfPeaks)

    #######
    # SLOTS
    #######

    def changeNumberOfPeaks(self):
        '''Apply a change in the number of peaks'''
        self.exchange.resizeMatrix(self.numpeaks.numPeaks)

    #########
    # SIGNALS
    #########

