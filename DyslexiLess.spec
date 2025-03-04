# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['improved_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'pynput.keyboard'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DyslexiLess',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/vanguardhive/Desktop/TRABAJOS/SALA-CREATIVA/dyslexiless-AI-typing/resources/icon.png'],
)
app = BUNDLE(
    exe,
    name='DyslexiLess.app',
    icon='/Users/vanguardhive/Desktop/TRABAJOS/SALA-CREATIVA/dyslexiless-AI-typing/resources/icon.png',
    bundle_identifier=None,
)
