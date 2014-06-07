from __future__ import print_function, division, absolute_import

# Non-std. lib imports
from PyQt4.QtCore import QString
from PyQt4.QtGui import QErrorMessage

error = QErrorMessage()

def toolTipText(text):
    '''Creates text for a tool tip'''
    return QString('<html>'+text+'</html>')
