from __future__ import division
from PyQt4.QtCore import pyqtSignal, QObject, QString, Qt, QVariant
from PyQt4.QtGui import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, \
                        QSpinBox, QComboBox, QStringListModel, QCheckBox, \
                        QDoubleSpinBox, QGridLayout
from numpy.testing import assert_approx_equal
from numpy import zeros, vstack, ndenumerate, ndindex
from math import pi
from common import ZMat
HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )
indexrole = Qt.UserRole
raterole = Qt.UserRole+1

class ExchangeView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Peak Exchanges', parent = 0):
        '''Initiallize'''
        super(QGroupBox, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        # Peak number chooser
        self.numpeaks = QSpinBox(self)
        self.numpeaks.setRange(2, 4)
        # Make 4x4 matrix of QLabels
        self.exview = [[QLabel(self) for i in xrange(4)] for j in xrange(4)]
        # Enforce symmetry button
        self.symmetry = QCheckBox("Enforce Symmetry", self)
        # Exchange picker
        self.exchooser = QComboBox(self)
        # Exchange value
        self.exvalue = QDoubleSpinBox(self)
        self.exvalue.setDecimals(3)
        self.exvalue.setRange(0.0, 1.0)
        self.exvalue.setSingleStep(0.1)

    def makeConnections(self):
        '''Connect the widgets together'''

        # When the number of peaks is changed, broadcast change model
        self.numpeaks.valueChanged.connect(self.npmodel.setNumPeaks)

        # When the table has been resixed, tidy it up
        self.matrix.matrixChanged.connect(self.resetMatrix)

        # If the check state changed, change the data model
        self.symmetry.stateChanged.connect(self.changeDataModel)
        self.numpeaks.valueChanged.connect(self.changeDataModel)

        # Attach the chooser to an exchange rate
        self.exchooser.currentIndexChanged.connect(self.attachExchange)

        # If the exchange rate is changed, update the matrix
        self.exvalue.valueChanged.connect(self.newExchange)

    def initUI(self):
        '''Lays out the widgets'''
        nums = QHBoxLayout()
        nums.addWidget(QLabel("Number of Peaks: "))
        nums.addWidget(self.numpeaks)
        val = QHBoxLayout()
        val.addWidget(QLabel("Exchange: "))
        val.addWidget(self.exchooser)
        val.addWidget(self.exvalue)
        ex = QGridLayout()
        for i in xrange(4):
            for j in xrange(4):
                ex.addWidget(self.exview[i][j], i+1, j+1)
        lo = QVBoxLayout()
        lo.addLayout(nums)
        lo.addWidget(self.symmetry)
        lo.addLayout(val)
        lo.addLayout(ex)
        self.setLayout(lo)

    def setModel(self, model, npmodel):
        '''Attaches models to the views.'''
        self.matrix = model
        self.npmodel = npmodel

    #######
    # SLOTS
    #######

    def newExchange(self, value):
        '''Prepares an exchange value to be broadcasted'''
        indx = self.exchooser.currentIndex()
        npeaks = self.numpeaks.value()
        self.matrix.updateExchange(value, indx, npeaks)

    def resetMatrix(self):
        '''Reset the matrix values'''

        # Iterate over the matrix and fill the values
        for index, num in ndenumerate(self.matrix.matrix):
            self.exview[index[0]][index[1]].setText('{0:.3f}'.format(num))

        # Set all other values to two dashes
        if len(self.matrix.matrix) == 2:
            for i in xrange(4):
                for j in xrange(4):
                    if not (i < 2 and j < 2):
                        self.exview[i][j].setText('--')
        elif len(self.matrix.matrix) == 3:
            for i in xrange(4):
                for j in xrange(4):
                    if not (i < 3 and j < 3):
                        self.exview[i][j].setText('--')

    def changeDataModel(self):
        '''Change the matrix from symmetric to not or vice versa'''

        # Change the model for the combo box
        npeaks = self.npmodel.numPeaks
        self.matrix.sym = self.symmetry.isChecked()
        if self.matrix.sym:
            self.exchooser.setModel(self.matrix.symex[npeaks])
        else:
            self.exchooser.setModel(self.matrix.unsymex[npeaks])

        # Reset the matrix
        self.matrix.setMatrix(npeaks)

    def attachExchange(self, indx):
        '''Attach a new exchange rate to the chooser'''
        r = self.matrix.symrate if self.matrix.sym else self.matrix.unsymrate
        self.exvalue.setValue(r[self.npmodel.numPeaks][indx])

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

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QObject, self).__init__(parent)
        self.matrix = zeros((4,4))
        self.sym = True

        # Make the exchange models

        # First make the models with the label seen by the user
        sym = ['1 -> 2',
               '1 -> 2_1 -> 3_2 -> 3',
               '1 -> 2_1 -> 3_1 -> 4_2 -> 3_2 -> 4_3 -> 4']
        nosym = ['1_1 -> 2_2 -> 1_2',
                 '1_1 -> 2_1 -> 3_2 -> 1_2_2 -> 3_3 -> 1_3 -> 2_3',
                 '_'.join(['1', '1 -> 2', '1 -> 3', '1 -> 4',
                           '2 -> 1', '2', '2 -> 3', '2 -> 4',
                           '3 -> 1', '3 -> 2', '3', '3 -> 4',
                           '4 -> 1', '4 -> 2', '4 -> 3', '4'])]
        # A function to convert a string to a QStringListModel
        f = lambda x: QStringListModel(QString(x).split('_'))
        # The two empty elements are so the model can correspond to the number
        # of peaks
        self.symex   = ['', ''] + [f(x) for x in sym]
        self.unsymex = ['', ''] + [f(x) for x in nosym]

        # Set the indices and rates for each label
        self.symindx   =  ((), (), ((0,1),),
                           ((0,1), (0,2), (1,2)),
                           ((0,1), (0,2), (0,3),
                            (1,2), (1,3), (2,3)))
        self.unsymindx = ((), (), 
                          ((0,0), (0,1),
                           (1,0), (1,1)),
                          ((0,0), (0,1), (0,2),
                           (1,0), (1,1), (1,2),
                           (2,0), (2,1), (2,2)),
                          ((0,0), (0,1), (0,2), (0,3),
                           (1,0), (1,1), (1,2), (1,3),
                           (2,0), (2,1), (2,2), (2,3),
                           (3,0), (3,1), (3,2), (3,3)))
                                      
        self.symrate   = [[], [], [0.0], [0.0, 0.0, 0.0],
                          [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
        self.unsymrate = [[], [],
                          [0.0, 0.0,
                           0.0, 0.0],
                          [0.0, 0.0, 0.0, 
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0],
                          [0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0, 0.0]]

        self._makeConnections()

    def _makeConnections(self):
        '''Connects the contained objects together'''
        pass

    def setMatrix(self, npeaks):
        '''Set the values into the matrix'''

        # Make an alias for the proper model based on symmetry or not
        indx = self.symindx[npeaks] if self.sym else self.unsymindx[npeaks]
        rate = self.symrate[npeaks] if self.sym else self.unsymrate[npeaks]

        # Send values to the ZMat constructor
        self.matrix = ZMat(npeaks, indx, rate, self.sym)

        # Use the new values to update the internal matrix model
        if npeaks == 2:
            self.unsymrate[2][0] = self.matrix[0,0]
            self.unsymrate[2][1] = self.matrix[0,1]
            self.unsymrate[2][2] = self.matrix[1,0]
            self.unsymrate[2][3] = self.matrix[1,1]
            self.unsymrate[3][0] = self.matrix[0,0]
            self.unsymrate[3][1] = self.matrix[0,1]
            self.unsymrate[3][3] = self.matrix[1,0]
            self.unsymrate[3][4] = self.matrix[1,1]
            self.unsymrate[4][0] = self.matrix[0,0]
            self.unsymrate[4][1] = self.matrix[0,1]
            self.unsymrate[4][4] = self.matrix[1,0]
            self.unsymrate[4][5] = self.matrix[1,1]
            self.symrate[2][0]   = self.matrix[0,1]
            self.symrate[3][0]   = self.matrix[0,1]
            self.symrate[4][0]   = self.matrix[0,1]
        elif npeaks == 3:
            self.unsymrate[2][0]  = self.matrix[0,0]
            self.unsymrate[2][1]  = self.matrix[0,1]
            self.unsymrate[2][2]  = self.matrix[1,0]
            self.unsymrate[2][3]  = self.matrix[1,1]
            self.unsymrate[3][0]  = self.matrix[0,0]
            self.unsymrate[3][1]  = self.matrix[0,1]
            self.unsymrate[3][2]  = self.matrix[0,2]
            self.unsymrate[3][3]  = self.matrix[1,0]
            self.unsymrate[3][4]  = self.matrix[1,1]
            self.unsymrate[3][5]  = self.matrix[1,2]
            self.unsymrate[3][6]  = self.matrix[2,0]
            self.unsymrate[3][7]  = self.matrix[2,1]
            self.unsymrate[3][8]  = self.matrix[2,2]
            self.unsymrate[4][0]  = self.matrix[0,0]
            self.unsymrate[4][1]  = self.matrix[0,1]
            self.unsymrate[4][3]  = self.matrix[0,2]
            self.unsymrate[4][5]  = self.matrix[1,0]
            self.unsymrate[4][6]  = self.matrix[1,1]
            self.unsymrate[4][7]  = self.matrix[1,2]
            self.unsymrate[4][9]  = self.matrix[2,0]
            self.unsymrate[4][10] = self.matrix[2,1]
            self.unsymrate[4][11] = self.matrix[2,2]
            self.symrate[2][0]    = self.matrix[0,1]
            self.symrate[3][0]    = self.matrix[0,1]
            self.symrate[3][1]    = self.matrix[0,2]
            self.symrate[3][2]    = self.matrix[1,2]
            self.symrate[4][0]    = self.matrix[0,1]
            self.symrate[4][1]    = self.matrix[0,2]
            self.symrate[4][3]    = self.matrix[1,2]
        elif npeaks == 4:
            self.unsymrate[2][0]  = self.matrix[0,0]
            self.unsymrate[2][1]  = self.matrix[0,1]
            self.unsymrate[2][2]  = self.matrix[1,0]
            self.unsymrate[2][3]  = self.matrix[1,1]
            self.unsymrate[3][0]  = self.matrix[0,0]
            self.unsymrate[3][1]  = self.matrix[0,1]
            self.unsymrate[3][2]  = self.matrix[0,2]
            self.unsymrate[3][3]  = self.matrix[1,0]
            self.unsymrate[3][4]  = self.matrix[1,1]
            self.unsymrate[3][5]  = self.matrix[1,2]
            self.unsymrate[3][6]  = self.matrix[2,0]
            self.unsymrate[3][7]  = self.matrix[2,1]
            self.unsymrate[3][8]  = self.matrix[2,2]
            self.unsymrate[4][0]  = self.matrix[0,0]
            self.unsymrate[4][1]  = self.matrix[0,1]
            self.unsymrate[4][2]  = self.matrix[0,2]
            self.unsymrate[4][3]  = self.matrix[0,3]
            self.unsymrate[4][4]  = self.matrix[1,0]
            self.unsymrate[4][5]  = self.matrix[1,1]
            self.unsymrate[4][6]  = self.matrix[1,2]
            self.unsymrate[4][7]  = self.matrix[1,3]
            self.unsymrate[4][8]  = self.matrix[2,0]
            self.unsymrate[4][9]  = self.matrix[2,1]
            self.unsymrate[4][10] = self.matrix[2,2]
            self.unsymrate[4][11] = self.matrix[2,3]
            self.unsymrate[4][12] = self.matrix[3,0]
            self.unsymrate[4][13] = self.matrix[3,1]
            self.unsymrate[4][14] = self.matrix[3,2]
            self.unsymrate[4][15] = self.matrix[3,3]
            self.symrate[2][0]    = self.matrix[0,1]
            self.symrate[3][0]    = self.matrix[0,1]
            self.symrate[3][1]    = self.matrix[0,2]
            self.symrate[3][2]    = self.matrix[1,2]
            self.symrate[4][0]    = self.matrix[0,1]
            self.symrate[4][1]    = self.matrix[0,2]
            self.symrate[4][2]    = self.matrix[0,3]
            self.symrate[4][3]    = self.matrix[1,2]
            self.symrate[4][4]    = self.matrix[1,3]
            self.symrate[4][5]    = self.matrix[2,3]

        self.matrixChanged.emit()

    #######
    # SLOTS
    #######

    def resizeMatrix(self, npeaks):
        '''Resize the matrix to the number of peaks'''
        if npeaks > len(self.matrix):
            N = len(self.matrix)
            oldmatrix = self.matrix.copy()
            self.matrix = zeros((npeaks,npeaks))
            self.matrix[0:N,0:N] = oldmatrix.copy()
        else:
            self.matrix = self.matrix[0:npeaks,0:npeaks].copy()
        self.setMatrix(npeaks)

    def updateExchange(self, value, indx, npeaks):
        '''Updates the exchange with a new value'''
        model = self.symrate if self.sym else self.unsymrate
        model[npeaks][indx] = value
        self.setMatrix(npeaks)

    #########
    # SIGNALS
    #########

    # Alert when the matrix is new
    matrixChanged = pyqtSignal()
