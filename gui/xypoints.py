from PyQt4.Qwt5 import QwtPlotCurve, QwtPlotItem
from numpy import zeros, linspace

class XYPoints(QwtPlotCurve):
    '''Actual points plotted on a curve'''

    def __init__(self, nPoints = 1000, title = ''):
        '''Initiallize the data and the curve itself'''
        super(QwtPlotCurve, self).__init__(title)
        self.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.setNumberOfPoints(nPoints)
        self.clear()

    def clear(self):
        '''Reset all values to zero'''
        self.x = zeros(self.nPoints)
        self.y = zeros(self.nPoints)

    def setNumberOfPoints(self, num):
        '''Sets the number of points to plot'''
        self.nPoints = num

    def getNumberOfPoints(self):
        '''Retrieves the number of points'''
        return self.nPoints 

    def setDomain(self, xmin, xmax):
        '''Sets the x-values to be evenly spaced between two values'''
        self.x = linspace(xmin, xmax, self.getNumberOfPoints())

    def getDomain(self):
        '''Returns the domain'''
        return self.x

    def getValues(self):
        '''Returns the values'''
        return self.y

    def setFunctionData(self, function):
        '''Applies a function to the y-data'''
        self.y = function(self.x)
        self.setData(self.x, self.y)
