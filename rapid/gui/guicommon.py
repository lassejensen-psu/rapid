from __future__ import print_function, division, absolute_import

# Non-std. lib imports
from PySide.QtGui import QErrorMessage

error = QErrorMessage()

def toolTipText(text):
    '''Creates text for a tool tip'''
    return '<html>'+text+'</html>'
