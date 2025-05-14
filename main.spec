# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('dll\\libzkfpcsharp.dll', '.')],
    datas=[('dll/libzkfpcsharp.dll', 'dll'), ('data/database_visit.pdf', 'data'), ('data/prisoners.pdf', 'data'), ('data/relations.pdf', 'data'), ('data/relatives.pdf', 'data'), ('data/visit_report.db.enc', 'data'), ('driver/ZKFinger_Driver-5.3.zip', 'driver'), ('font/THSarabun Bold.ttf', 'font'), ('font/THSarabun BoldItalic.ttf', 'font'), ('font/THSarabun Italic.ttf', 'font'), ('font/THSarabun.ttf', 'font'), ('key/secret.key', 'key')],
    hiddenimports=['clr', 'System'],
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
    name='main',
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
)
