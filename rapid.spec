# -*- mode: python -*-
import sys

# This spec file is designed to be run in this directory
# The pathex list is empty because we cannot know where 
# each user will place pyinstaller.
a = Analysis(['rapid.py'],
             pathex=[],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None)
pyz = PYZ(a.pure)

# Windows has the .exe at the end of the name
if sys.platform.startswith('win'):
    filename='rapid.exe'
else:
    filename='rapid'

# App bundle
#if False: # Skip this block because the .app doesn't run on double-click
if sys.platform.startswith('darwin'):

    # Make the executable
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=1,
              name=os.path.join('build', filename),
              debug=False,
              strip=None,
              upx=True,
              console=False)

    # Make the app bundle
    app = BUNDLE(exe,
                 a.binaries,
                 a.zipfiles,
                 a.datas,
                 version='0.1',
                 strip=None,
                 upx=True,
                 name='.'.join([filename, 'app']))

# Single executable
else:

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

