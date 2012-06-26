from __future__ import division
from sys import argv, stderr
from os import environ
from textwrap import dedent
from PyQt4.QtGui import QMainWindow, QWidget, QVBoxLayout, \
                        QHBoxLayout, QLabel, QPushButton, QTabWidget, \
                        QAction, QKeySequence, QFileDialog, QPushButton
from PyQt4.Qt import qApp
from numpy import loadtxt, array
from input_reader import ReaderError
from plot import Plot
from rate import RateView
from exchange import ExchangeView
from scale import ScaleView
from peak import PeakView
from controller import Controller
from common import save_script, read_input, ZMat, write_data
from guicommon import error
from guicommon import toolTipText as ttt

class MainWindow(QMainWindow):
    '''The main window of the program'''

    def __init__(self):
        '''Initiallize the main window and it's parents'''
        super(MainWindow, self).__init__()
        self._createtWidgets()
        self._initUI()
        self._makeMenu()
        self._makeConnections()
        self.fileName = None
        self.scriptName = None
        self.expName = None
        self.rawName = None

        # Set initial number of peaks
        self.exchange.setNumPeaks(2)
        # Set matrix to symmetric by default
        self.exchange.setMatrixSymmetry(True)
        # Set the initial window.  
        self.scale.setValue(1900, 2100, False)
        # Default to rate in units of THz
        self.rate.setUnit('THz')
        # Clear button starts off inactive
        self.clear.setEnabled(False)

    def _createtWidgets(self):
        '''Creates all the widgets'''

        # Make the views
        self.plot = Plot(self)
        self.rate = RateView(parent=self)
        self.exchange = ExchangeView(parent=self)
        self.peak = PeakView(parent=self)
        self.scale = ScaleView(parent=self)

        # Create the model controller
        self.control = Controller(self)

        # Attach models to the views
        self.rate.setModel(self.control.rate)
        self.exchange.setModel(self.control.exchange, self.control.numpeaks)
        self.peak.setModel(self.control.peak)
        self.scale.setModel(self.control.scale)

        # Init the UI of all the views
        self.rate.initUI()
        self.exchange.initUI()
        self.peak.initUI()
        self.scale.initUI()

        # Last, make inter-view connections
        self.rate.makeConnections()
        self.exchange.makeConnections()
        self.peak.makeConnections()
        self.scale.makeConnections()
        self.plot.makeConnections()

        # The window will own a button to clear raw data
        self.clear = QPushButton('Clear Raw Data', self)
        self.clear.setToolTip(ttt('Remove raw data from the plot '
                                  'if there is any'))

    def _initUI(self):
        '''Sets up the layout of the window'''

        # Define a central widget and a layout for the window
        self.setCentralWidget(QWidget())
        self.mainLayout = QHBoxLayout()
        self.setWindowTitle('Spectral Exchange')

        # Make a layout for all the parameter views
        params = QVBoxLayout()
        params.addWidget(self.rate)
        params.addWidget(self.exchange)
        params.addWidget(self.peak)

        # Add the parameter dialog
        self.mainLayout.addLayout(params)

        # Add the plot 
        plot_lim = QVBoxLayout()
        plot_lim.addWidget(self.plot)
        lim_clear = QHBoxLayout()
        lim_clear.addWidget(self.scale)
        lim_clear.addWidget(self.clear)
        plot_lim.addLayout(lim_clear)
        self.mainLayout.addLayout(plot_lim)

        # Add the widgets to the central widget
        self.centralWidget().setLayout(self.mainLayout)

    def _makeConnections(self):
        '''Connect the widgets to each other'''

        # When the controller says plot, plot
        self.control.plotSpectrum.connect(self.plot.plotCalculatedData)

        # When the controller says resize x limits, do so
        self.control.newXLimits.connect(self.plot.changeScale)

        # Clear raw data if pushed
        self.clear.clicked.connect(self.clearRawData)

        # If the plot is clicked, send info to the scale widget
        self.plot.pointPicked.connect(self.scale.setSelection)


    def _makeMenu(self):
        '''Makes the menu bar for this widget'''
        # Get the menu bar object
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&File')

        # Open action
        open = QAction('&Open', self)
        open.setShortcuts(QKeySequence.Open)
        open.triggered.connect(self.openFromInput)
        open.setToolTip('Open an already made input file')
        self.fileMenu.addAction(open)

        # Save action
        save = QAction('&Save', self)
        save.setShortcuts(QKeySequence.Save)
        save.triggered.connect(self.saveToInput)
        save.setToolTip('Save settings to an input file')
        self.fileMenu.addAction(save)

        # Save action
        saveas = QAction('Save As', self)
        saveas.triggered.connect(self.saveToInputAs)
        self.fileMenu.addAction(saveas)

        # Menu seperator
        self.fileMenu.addSeparator()

        # Import action
        imp = QAction('&Import raw XY data', self)
        imp.setShortcut(QKeySequence('Ctrl+I'))
        imp.triggered.connect(self.importXYData)
        imp.setToolTip('Import raw data an plot alongside calculated data')
        self.fileMenu.addAction(imp)

        # Export action
        exp = QAction('&Export calculated XY data', self)
        exp.setShortcut(QKeySequence('Ctrl+E'))
        exp.triggered.connect(self.exportXYData)
        exp.setToolTip('Export calculated data to a file for use elsewhere')
        self.fileMenu.addAction(exp)

        # Make script action
        scr = QAction('Make Sc&ript', self)
        scr.setShortcut(QKeySequence('Ctrl+R'))
        scr.triggered.connect(self.makeScript)
        scr.setToolTip('Create a python script that directly recreates this '
                       'spectrum')
        self.fileMenu.addAction(scr)

        # Menu seperator
        self.fileMenu.addSeparator()

        # Quit action
        quit = QAction('&Quit', self)
        quit.setShortcuts(QKeySequence.Quit)
        quit.triggered.connect(qApp.quit)
        self.fileMenu.addAction(quit)

    #######
    # SLOTS
    #######

    def clearRawData(self):
        '''Clear the raw data from the plot'''
        self.plot.clearRawData()
        self.clear.setEnabled(False)

    def openFromInput(self):
        '''Open parameters from an input file'''
        filter = 'Input Files (*.inp);;All (*)'
        s = QFileDialog.getOpenFileName(self, 'Open Input File',
                                              '', filter)
        # Continue unless the user hit cancel
        if not s:
            return
        fileName = s

        # Read given input file
        try:
            args = read_input(fileName)
        except ReaderError as r: # Error reading the input file
            error.showMessage(str(r))

        # Set the number of peaks
        npeaks = len(args.num)
        if npeaks < 2:
            error.showMessage('Need at least 2 peaks for exchange')
            return
        elif npeaks > 4:
            error.showMessage('This GUI can only handle up to 4 peaks. '
                              'Use the command-line version for an arbitrary '
                              'number of peaks')
            return
        self.exchange.setNumPeaks(npeaks)

        # Set the exchange
        matrix = ZMat(npeaks, args.exchanges, args.exchange_rates,
                      args.symmetric_exchange)
        self.exchange.setMatrixSymmetry(args.symmetric_exchange)
        self.exchange.setMatrix(matrix)

        # Set the rate
        if 'lifetime' in args:
            self.rate.setUnit(args.lifetime[1])
            self.rate.setRate(args.lifetime[0])
        else:
            self.rate.setUnit(args.rate[1])
            self.rate.setRate(args.rate[0])

        # Set the peak data
        self.peak.setPeaks(args.vib, args.Gamma_Lorentz, args.Gamma_Gauss,
                           args.heights)

        # Plot this data
        self.control.setDataForPlot()

        # Plot raw data if it exists
        if args.raw is not None:
            self.rawName = args.rawName
            self.plot.setRawData(args.raw)
            self.plot.plotRawData()
            self.clear.setEnabled(True)

        # Set the limits
        self.scale.setValue(args.xlim[0], args.xlim[1], args.reverse)

        # Default the script file name or data file nameif given
        if args.data:
            self.expName = args.data
        elif args.save_plot_script:
            self.scriptName = args.args.save_plot_script

    def saveToInput(self):
        '''Save current settings to current input file if available'''
        if not self.control.hasPlot:
            error.showMessage('Cannot save.. there is no data to save yet')
            return
        if self.fileName is None:
            self.saveToInputAs()
        else:
            self.inputGen(self.fileName)

    def saveToInputAs(self):
        '''Save current settings to an input file of specified name'''
        if not self.control.hasPlot:
            error.showMessage('Cannot save.. there is no data to save yet')
            return
        filter = 'Input Files (*.inp);;All (*)'
        d = '' if self.fileName is None else self.fileName
        s = QFileDialog.getSaveFileName(self, 'Save Input File',
                                              d, filter)
        # Continue unless the user hit cancel
        if not s:
            return
        self.fileName = s

        # Generate the input file
        self.inputGen(self.fileName)

    def exportXYData(self):
        '''Export current spectrum to XY data'''
        if not self.control.hasPlot:
            error.showMessage('Cannot export.. there is no data to export yet')
            return
        filter = 'Data Files (*.txt *.data);;All (*)'
        d = '' if self.expName is None else self.expName
        s = QFileDialog.getSaveFileName(self, 'Export calculated XY data',
                                              d, filter)
        # Continue unless the user hit cancel
        if not s:
            return
        self.expName = s

        # Grab the XY data from the plot
        x, y = self.plot.calculatedData()
        # Save in a standard format
        try:
            write_data(x, y, self.expName)
        except (IOError, OSError) as e:
            error.showMessage(str(e))

    def importXYData(self):
        '''Import data from an XY file'''
        filter = 'Data Files (*.txt *.data);;All (*)'
        d = '' if self.rawName is None else self.rawName
        s = QFileDialog.getOpenFileName(self, 'Import raw XY data',
                                              d, filter)
        # Continue unless the user hit cancel
        if not s:
            return
        self.rawName = s

        # Load raw data and plot in a second curve
        rawData = loadtxt(str(self.rawName))
        self.plot.setRawData(rawData)
        self.plot.plotRawData()
        self.clear.setEnabled(True)

    def makeScript(self):
        '''Open parameters from an input file'''
        if not self.control.hasPlot:
            error.showMessage('Cannot save.. there is no data to save yet')
            return
        filter = 'Python Scripts (*.py)'
        d = '' if self.scriptName is None else self.scriptName
        s = QFileDialog.getSaveFileName(self, 'Make script',
                                              d, filter)
        # Continue unless the user hit cancel
        if not s:
            return
        self.scriptName = s

        # Get parameters needed
        xlim, rev, oldp, newp = self.control.getParametersForScript()
        x, y = self.plot.calculatedData()
        if self.clear.isEnabled():
            raw = self.plot.rawData()
        else:
            raw = None
        save_script(x, y, raw, xlim, rev, oldp, newp, self.scriptName)

    def inputGen(self, fileName):
        '''Generate an input file'''

        # Open file for writing        
        try:
            fl = open(fileName, 'w')
        except (IOError, OSError) as e:
            error.showError(str(e))

        # Generate a template string to print
        s = dedent('''\
            # The rate or lifetime of the reaction
            {rate}

            # The exchange matrix
            {exchange}

            # The peak data
            {peaks}

            # The plot limits
            {limits}

            # Raw input file, if any
            {raw}
            ''')

        # Get the parameters from the underlying data
        xlim, rev, rate, exchange, peaks = self.control.getParametersForInput()

        # Create the rate string
        if rate[1] in ('s', 'ns', 'ps', 'fs'):
            lr = 'lifetime'
        else:
            lr = 'rate'
        ratestr = '{0} {1[0]:.3G} {1[1]}'.format(lr, rate)

        # Create exchange string
        exstr = []
        if not exchange[2]:
            exstr.append('nosym')
        f = 'exchange {0:d} {1:d} {2:.3f}'
        for indx, r in zip(exchange[1], exchange[0]):
            exstr.append(f.format(indx[0]+1, indx[1]+1, r))
        exstr = '\n'.join(exstr)

        # Create peak string
        peakstr = []
        f = 'peak {0:.2f} {1:.3f} L={2:.3f} G={3:.3f}'
        for p, l, g, h in zip(peaks[0], peaks[1], peaks[2], peaks[3]):
            peakstr.append(f.format(p, h, l, g))
        peakstr = '\n'.join(peakstr)
            
        # Create the limits string
        limitstr = 'xlim {0[0]:d} {0[1]:d}'.format(xlim)
        if rev:
            limitstr += '\nreverse'

        # Create the IO string
        if self.rawName is not None:
            rawstr = 'raw {0}'.format(self.rawName)
        else:
            rawstr = ''

        # Write the string to file
        fl.write(s.format(rate=ratestr, peaks=peakstr, limits=limitstr,
                          exchange=exstr, raw=rawstr))

        # Close file
        fl.close()

    #########
    # SIGNALS
    #########
