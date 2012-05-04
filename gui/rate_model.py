from PyQt4.QtCore import pyqtSignal, QObject
from math import pi
HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )

class Rate(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)

    def setConverter(self, unit):
        '''Sets the function to perform rate conversion to cm^{-1}'''

        conv = {
                 'fs'   : lambda x : HZ2WAVENUM / ( 1E-15 * x ),
                 'ps'   : lambda x : HZ2WAVENUM / ( 1E-12 * x ),
                 'ns'   : lambda x : HZ2WAVENUM / ( 1E-9  * x ),
                 's'    : lambda x : HZ2WAVENUM / (         x ),
                 '1/fs' : lambda x : HZ2WAVENUM * 1E15 * x,
                 '1/ps' : lambda x : HZ2WAVENUM * 1E12 * x,
                 '1/ns' : lambda x : HZ2WAVENUM * 1E9  * x,
                 '1/s'  : lambda x : HZ2WAVENUM        * x,
               }
        try:
            self.converter = conv[str(unit)]
        except KeyError:
            pass # This happens when we set a new model.  Ignore

    #######
    # SLOTS
    #######

    def setRate(self, rate):
        '''Sets the rate and emits the result'''
        self.rate = rate
        self.rateInUnits.emit(self.rate)
        self.rateInWavenumbers.emit(self.converter(self.rate))

    #########
    # SIGNALS
    #########

    # The rate in the units the user wants
    rateInUnits = pyqtSignal(float)

    # The rate in wavenumbers
    rateInWavenumbers = pyqtSignal(float)
