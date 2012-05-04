from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QStandardItemModel, QStandardItem
from tokenize import generate_tokens, printtoken
from token import tok_name
from cStringIO import StringIO
from textwrap import dedent
from numpy import arange

# Load a predefined selection of functions from numpy & friends
from math import pi, e
npstr = ('abs, absolute, add, multiply, angle, arccos, arcsin, '
         'arctan, arccosh, arcsinh, arctanh, arctan2, ceil, floor, '
         'round, conj, conjugate, cos, sin, tan, cosh, sinh, tanh, '
         'fix, hypot, maximum, minimum, sqrt, square, sign, real, '
         'imag, remainder, modf, fmod, mod, true_divide, subtract, '
         'floor_divide, power, reciprocal, exp, expm1, exp2, log, '
         'log10, log2, log1p, prod, sum, degrees, radians'
        )
exec 'from numpy import '+npstr
conststr = 'epsilon_0, h, hbar, R, N_A'
exec 'from scipy.constants import '+conststr
specstr = 'erf, erfc, wofz'
exec 'from scipy.special import '+specstr

# We want ln to be interprited as log, and I as 1j
ln = log
I = 1j

# Store the function names and constant names
funcnames = set(npstr.split(', ')+specstr.split(', ')+['ln'])
constnames = set(conststr.split(', ')+['pi,', 'e', 'I'])

# Make a dictionary of allowed function names
functs = dict([(k, locals().get(k, None)) for k in funcnames|constnames])

# A test domain
testdomain = arange(10)

class Function(QStandardItemModel):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QStandardItemModel, self).__init__(parent)

    def _makeFactoryFunction(self, funcStr):
        '''Make a function factory that can be used to quickly edit the
        functions variable parameters'''

        # Make the parameter list for the function factory
        paramStr = ', '.join([self.getName(i) for i in xrange(self.nParams)])

        # Create the factory function
        factStr = 'lambda {params}: lambda x: {func}'
        factStr = factStr.format(params=paramStr, func=funcStr)
        try:
            self.factory = eval(factStr, functs)
        except NameError, SyntaxError:
            from sys import exit
            exit('Died from invalid function')

    def getFunction(self):
        '''Return the function'''
        return self.function

    def getName(self, index):
        '''Gets the name for some parameter'''
        return str(self.item(index, 0).text())

    def getMaxValue(self, index):
        '''Gets the maximum value for some parameter'''
        return self.item(index, 3).text().toFloat()[0]

    def getMinValue(self, index):
        '''Gets the minimum value for some parameter'''
        return self.item(index, 2).text().toFloat()[0]

    def getValue(self, index):
        '''Gets the value for some parameter'''
        return self.item(index, 1).text().toFloat()[0]

    #######
    # SLOTS
    #######

    def parseFunction(self, funcStr):
        '''Parse a string and store as a mathematical function'''

        # Create a row then delete it to fix a bug
        self.appendRow([QStandardItem('Test'),
                        QStandardItem('1.0'),
                        QStandardItem('0.0'),
                        QStandardItem('10.0')])

        # Reset the parameters and flags
        self.clear()
        self.isComplex = False
        self.funcStr = funcStr

        # The string must be file-like to tokenize it
        string = StringIO(str(funcStr))
        # Parse the string for tokens, similar to the python interpriter
        for tok in generate_tokens(string.readline):
            # Any token that is classified as a name but is not a predefined
            # function or constant is assumed to be a variable
            if tok_name[tok[0]] == 'NAME':
                # The token 'x' is reserved as the domain variable
                if tok[1] == 'x':
                    pass
                # The rest are stored as parameters.  Store the name the first
                # column, the value in the second, the min value in the third
                # and the max value in the last
                elif tok[1] not in funcnames|constnames:
                    # Only add this parameter if it does not yet exist
                    if not self.findItems(tok[1]):
                        self.appendRow([QStandardItem(tok[1]),
                                        QStandardItem('1.0'),
                                        QStandardItem('0.0'),
                                        QStandardItem('10.0')])
                # Check if this is a complex function
                elif tok[1] == 'I':
                    self.isComplex = True
        
        # Reset the number of parameters
        self.nParams = self.rowCount()

        # Make the factory function used to generate the plotting function
        self._makeFactoryFunction(funcStr)
        # Use the factory function to create the plotting function
        self.setFunctionParameters(False)

        # Last, check that the function actual is valid
        try:
           vals = self.function(testdomain)
        except ValueError:
            from sys import exit
            exit('Died from invalid math')

        # Emit the function
        self.hasPlotableFunction.emit(self.function)
    
    def setFunctionParameters(self, emit):
        '''Inserts the parameters into the factory to get the function'''

        # Build a list of the parameters to pass
        params = [self.getValue(i) for i in xrange(self.nParams)]

        # Use the parameters to make the plottable function
        self.function = self.factory(*params)

        # Emit the signal now if needed
        if emit:
            self.hasPlotableFunction.emit(self.function)
    
    def setMaxValue(self, index, max):
        '''Sets the maximum value for some parameter'''
        self.setItem(index, 3, QStandardItem(str(max)))
        self.maxValueChanged.emit(index, max) 

    def setMinValue(self, index, min):
        '''Sets the minimum value for some parameter'''
        self.setItem(index, 2, QStandardItem(str(min)))
        self.maxValueChanged.emit(index, min) 

    def setValue(self, index, val):
        '''Sets the value for some parameter and then replot'''
        self.setItem(index, 1, QStandardItem(str(val)))
        self.valueChanged.emit(index, val) 
        self.setFunctionParameters(True)

    #########
    # SIGNALS
    #########

    # Broadcast the function to plot
    hasPlotableFunction = pyqtSignal(object)

    # A change in the max, min, or actual value has occured
    maxValueChanged = pyqtSignal(int, float)
    minValueChanged = pyqtSignal(int, float)
    valueChanged    = pyqtSignal(int, float)
