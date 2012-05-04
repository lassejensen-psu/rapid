from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QAbstractItemModel
from tokenize import generate_tokens, printtoken
from token import tok_name
from cStringIO import StringIO
from textwrap import dedent
from numpy import arange

class ExchangeModel(QAbstractItemModel):
    '''Class to hold all information about the function'''

    def __init__(self, parent):
        '''Initiallize the function class'''
        super(QAbstractItemModel, self).__init__(parent)

    def _makeConnecions(self):
        '''Connects the contained objects together'''

    #######
    # SLOTS
    #######

    #########
    # SIGNALS
    #########
