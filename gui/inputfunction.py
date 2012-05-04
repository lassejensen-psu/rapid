from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QLineEdit

class InputFunction(QLineEdit):
    '''Special class for inputting a function'''

    def __init__(self, parent):
        '''Initiallize the class'''
        super(QLineEdit, self).__init__(parent)

    #######
    # SLOTS
    #######

    def plotFunction(self):
        '''Slot to tell this class the user wants to plot the function'''
        self.broadcastFunction.emit(self.text())

    #########
    # SIGNALS
    #########

    # Emit the function to plot
    broadcastFunction = pyqtSignal(str)

