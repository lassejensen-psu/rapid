from PyQt4.QtCore import QString
from PyQt4.QtGui import QErrorMessage

error = QErrorMessage()

def toolTipText(text):
    '''Creates text for a tool tip'''
    return QString('<html>'+text+'</html>')
