from __future__ import print_function, division, absolute_import

# Std. lib imports
from math import pi
from textwrap import dedent

# Non-std. lib imports
from PySide.QtCore import Signal, QObject, Qt, QRegExp
from PySide.QtGui import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, \
                        QLineEdit, QComboBox, QStringListModel, QCheckBox, \
                        QGridLayout, QDoubleValidator, QRadioButton
from numpy.testing import assert_approx_equal
from numpy import zeros, vstack, ndenumerate, ndindex, ndarray

# Local imports
from rapid.common import ZMat
from rapid.gui.guicommon import error
from rapid.gui.guicommon import toolTipText as ttt


HZ2WAVENUM = 1 / ( 100 * 2.99792458E8 * 2 * pi )
indexrole = Qt.UserRole
raterole = Qt.UserRole+1


class ExchangeView(QGroupBox):
    '''The box containing the rate value'''

    def __init__(self, title = 'Peak Exchange Matrix', parent = None):
        '''Initialize'''
        super(ExchangeView, self).__init__(parent)
        self.setTitle(title)
        self._createWidgets()

    def _createWidgets(self):
        '''Create the widgets contained in this box'''
        # Peak number chooser
        self.numpeaks = [QRadioButton("2"),
                         QRadioButton("3"),
                         QRadioButton("4")]
        
        self.numpeaks[0].setToolTip(ttt('Model the exchange of 2 peaks'))
        self.numpeaks[1].setToolTip(ttt('Model the exchange of 3 peaks'))
        self.numpeaks[2].setToolTip(ttt('Model the exchange of 4 peaks'))
        # Make 4x4 matrix of QLabels
        self.exview = [[QLabel(self) for i in xrange(4)] for j in xrange(4)]
        for i in xrange(4):
            for e in self.exview[i]:
                e.setToolTip(ttt('The current exchange matrix'))
        # Enforce symmetry button
        self.symmetry = QCheckBox("Enforce Symmetry", self)
        self.symmetry.setToolTip(ttt('If symmetry is on then you only need to '
                                     'manually set the upper triangle of the '
                                     'exchange matrix.  Thse values are '
                                     'mirrored '
                                     'in the lower triangle and the diagonals '
                                     'are automatically set so that each row '
                                     'sums to 1. '
                                     'Otherwise you must set every element'))
        # Exchange picker
        self.exchooser = QComboBox(self)
        self.exchooser.setToolTip(ttt('Choose between which two peaks to set '
                                  'the exchange (relative) rate'))
        # Exchange value
        self.exvalue = QLineEdit(self)
        self.exvalue.setToolTip(ttt('The exchange (relative) rate'))
        self.exvalue.setValidator(QDoubleValidator(0.0, 1.0, 3, self.exvalue))

    def makeConnections(self):
        '''Connect the widgets together'''
        # When the table has been resized, tidy it up
        self.matrix.matrixChanged.connect(self.resetMatrix)
        # If the check state changed, change the data model
        self.symmetry.stateChanged.connect(self.changeDataModel)
        self.numpeaks[0].clicked.connect(self.changeDataModel)
        self.numpeaks[1].clicked.connect(self.changeDataModel)
        self.numpeaks[2].clicked.connect(self.changeDataModel)
        # Attach the chooser to an exchange rate
        self.exchooser.currentIndexChanged.connect(self.attachExchange)
        # If the exchange rate is changed, update the matrix
        self.exvalue.editingFinished.connect(self.newExchange)

    def initUI(self):
        '''Lays out the widgets'''
        nums = QHBoxLayout()
        nums.addWidget(QLabel("Number of Peaks: "))
        nums.addWidget(self.numpeaks[0])
        nums.addWidget(self.numpeaks[1])
        nums.addWidget(self.numpeaks[2])
        val = QHBoxLayout()
        val.addWidget(QLabel("Exchange: "))
        val.addStretch()
        val.addWidget(self.exchooser)
        self.exvalue.setMaximumWidth(50)
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

    def setNumPeaks(self, npeaks):
        '''Manually set the number of peaks'''
        if npeaks == 2:
            self.numpeaks[0].click()
        elif npeaks == 3:
            self.numpeaks[1].click()
        elif npeaks == 4:
            self.numpeaks[2].click()
        else:
            error.showMessage('Only valid number of peaks is 2, 3, or 4')

    def setMatrixSymmetry(self, sym):
        '''Manually set the matrix symmetry'''
        self.symmetry.setChecked(sym)

    def setMatrix(self, Z):
        '''Manually set the matrix elements with a numpy matrix'''
        npeaks = self.npmodel.getNumPeaks()
        self.matrix.matrix = Z[0:npeaks,0:npeaks]
        self.matrix.updateInternalModel(npeaks)
        self.resetMatrix()

    #######
    # SLOTS
    #######

    def newExchange(self):
        '''Prepares an exchange value to be broadcasted'''
        try:
            value = round(float(self.exvalue.text()), 3)
        except ValueError:
            value = 0.0
        indx = self.exchooser.currentIndex()
        if self.numpeaks[0].isChecked():
            npeaks = 2
        elif self.numpeaks[1].isChecked():
            npeaks = 3
        elif self.numpeaks[2].isChecked():
            npeaks = 4
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
        if self.numpeaks[0].isChecked():
            npeaks = 2
        elif self.numpeaks[1].isChecked():
            npeaks = 3
        elif self.numpeaks[2].isChecked():
            npeaks = 4
        self.npmodel.setNumPeaks(npeaks)
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
        self.exvalue.setText('{0:.3f}'.format(r[self.npmodel.numPeaks][indx]))

    #########
    # SIGNALS
    #########

#/\/\/\/\/\/\/\/
# NumPeaks Model
#/\/\/\/\/\/\/\/


class NumPeaks(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(NumPeaks, self).__init__(parent)
        self.numPeaks = 2

    def getNumPeaks(self):
        '''Return the number of peak'''
        return self.numPeaks

    #######
    # SLOTS
    #######

    def setNumPeaks(self, num):
        '''Sets the number of peaks'''
        self.numPeaks = num
        self.numberOfPeaksChanged.emit(self.numPeaks)

    #########
    # SIGNALS
    #########

    # The number of peaks
    numberOfPeaksChanged = Signal(int)

#/\/\/\/\/\/\/\/
# Exchange Model
#/\/\/\/\/\/\/\/


class ExchangeModel(QObject):
    '''Class to hold all information about the function'''

    def __init__(self, parent = None):
        '''Initiallize the function class'''
        super(ExchangeModel, self).__init__(parent)
        self.matrix = zeros((2,2))
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
        f = lambda x: QStringListModel(x.split('_'))
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

        # Send values to the ZMat constructor then update
        self.matrix = ZMat(npeaks, indx, rate, self.sym)
        self.updateInternalModel(npeaks)

    def updateInternalModel(self, npeaks):
        '''Updates the internal representation from the matrix'''

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

    def getParams(self, npeaks):
        '''Return the exchange parameters'''
        if self.sym:
            return self.symrate[npeaks], self.symindx[npeaks], True
        else:
            return self.unsymrate[npeaks], self.unsymindx[npeaks], False

    def getMatrix(self):
        '''Return the actual exchange matrix'''
        return self.matrix

    #######
    # SLOTS
    #######

    def resizeMatrix(self, npeaks):
        '''Resize the matrix to the number of peaks'''
        self.matrix = zeros((npeaks,npeaks))
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
    matrixChanged = Signal()
