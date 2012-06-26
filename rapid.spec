# -*- mode: python -*-

# This is the .spec file for PyInstaller, which is the only python
# executable generator that I have found to work with both PyQwt and Mac
a = Analysis(['../rapid/rapid.py'],
             pathex=['/amphome/smm553/programming/pyinstaller'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.linux2/rapid', 'rapid'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'rapid'))
