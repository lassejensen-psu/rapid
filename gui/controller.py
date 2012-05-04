from PyQt4.QtCore import pyqtSignal, QObject
#from peak_data_model import PeakData
#from exchange_model import ExchangeMatrix
from rate_model import Rate


class Controller(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the controller class'''
        super(QObject, self).__init__(parent)
        self.rate = Rate(self)
        self._makeConnections()


    def _makeConnections(self):
        '''Connect the contained widgets'''
        pass

    #######
    # SLOTS
    #######


    #########
    # SIGNALS
    #########

