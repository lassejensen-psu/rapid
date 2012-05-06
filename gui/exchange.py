from __future__ import division
from PyQt4.QtCore import pyqtSignal, QObject
from PyQt4.QtGui import QGroupBox
from numpy.testing import assert_approx_equal
from math import pi
HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )

class ExchangeView(QGroupBox):
    '''The box containing the rate value'''
    from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox

    def __init__(self, title = 'Peak Exchanges', parent = 0):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        self.numpeaks = QSpinBox(self)
        self.numpeaks.setRange(2, 4)

    def makeConnections(self):
        '''Connect the widgets together'''

        # When the number of peaks is changed, broadcast change model
        self.numpeaks.valueChanged.connect(self.npmodel.setNumPeaks)

        # When the table has been resixed, tidy it up
        self.table.checkTableSize.connect(self.tidyTable)

    def initUI(self):
        '''Lays out the widgets'''
        nums = QHBoxLayout()
        nums.addWidget(QLabel("Number of Peaks: "))
        nums.addWidget(self.numpeaks)
        lo = QVBoxLayout()
        lo.addLayout(nums)
        lo.addWidget(self.table)
        self.setLayout(lo)
        self.w = self.width()

    def setModel(self, model, npmodel):
        '''Attaches models to the views.'''
        self.table = model
        self.npmodel = npmodel

    #######
    # SLOTS
    #######

    def tidyTable(self):
        '''Make the columns not so wide we need scroll bars'''

        pass
        #np = self.npmodel.numPeaks
        ## Divide the group box width by the number of columns
        #print self.size(), self.table.size()
        #wpc = self.w // self.table.columnCount()
        #print self.w, self.table.columnCount()
        ## Change each column to this width
        #for i in xrange(self.table.columnCount()):
        #    print i, wpc
            #self.table.setColumnWidth(i, wpc)

    #########
    # SIGNALS
    #########

#/\/\/\/\/\/\/\/
# NumPeaks Model
#/\/\/\/\/\/\/\/

class NumPeaks(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)

    #######
    # SLOTS
    #######

    def setNumPeaks(self, num):
        '''Sets the number of peaks'''
        self.numPeaks = num
        self.numberOfPeaksChanged.emit()

    #########
    # SIGNALS
    #########

    # The number of peaks
    numberOfPeaksChanged = pyqtSignal()

#/\/\/\/\/\/\/\/
# Exchange Model
#/\/\/\/\/\/\/\/

class ExchangeModel(QObject):
    '''Class to hold all information about the function'''
    from numpy import zeros, vstack

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.matrix = zeros(1)
        #from PyQt4.QtGui import QSizePolicy
        #sp = QSizePolicy()
        #sp.setHeightForWidth(True)
        #self.setSizePolicy(sp)
        self._makeConnections()

    def _makeConnections(self):
        '''Connects the contained objects together'''
        pass

    #######
    # SLOTS
    #######

    def resizeMatrix(self, npeaks):
        '''Resize the matrix to the number of peaks'''
        if len(self.matrix) > npeaks:
            N = len(self.matrix)
            oldmatrix = self.matrix.copy()
            self.matrix = zeros((npeaks,npeaks))
            self.matrix[0:N,0:N] = oldmatrix.copy()
        else:
            self.matrix = self.matrix[0:npeaks:0:npeaks].copy()
        self.matrixChanged.emit()

    #########
    # SIGNALS
    #########

    # Alert when the matrix is new
    matrixChanged = pyqtSignal()
