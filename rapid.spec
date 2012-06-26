# -*- mode: python -*-
import sys

# This spec file is designed to be run in this directory
# The pathex list is empty because we cannot know where 
# each user will place pyinstaller.
a = Analysis(['rapid.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)

# Mac OS X app bundle
if sys.platform.startswith('darwin'):
    pass

# Not Mac OS X, single executable
else:

    # Windows has the .exe at the end of the name
    if sys.platform.startswith('win'):
        filename='rapid.exe'
    else:
        filename='rapid'

    # Define how to create the single executable file
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=filename,
              debug=False,
              strip=None,
              upx=True,
              console=False)

