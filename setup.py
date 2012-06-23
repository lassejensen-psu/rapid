from distutils.core import setup
import py2exe

setup(windows=['spectral_exchange.py'],
      options={'py2exe' : 
                {'includes':['sip', 'PyQt4.QtGui',
				    'PyQt4.QtCore',
				    'PyQt4.Qwt5']
                }
              }
)
