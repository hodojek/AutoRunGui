# -*- mode: python ; coding: utf-8 -*-

# Install pyinstaller by runnig
# pip install pyinstaller

# Make excutable by runnig this command
# pyinstaller.exe --onefile .\auto_run_gui.spec


block_cipher = None


a = Analysis(['src/main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [("icon.ico", "icon.ico", "DATA"),
            ("layouts.json", "layouts.json", "DATA")]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='auto_run_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False ,
          icon="icon.ico")
