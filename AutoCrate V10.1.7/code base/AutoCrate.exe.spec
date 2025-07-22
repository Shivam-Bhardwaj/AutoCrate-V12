# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['nx_expressions_generator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['front_panel_logic', 'front_panel_logic_unified', 'back_panel_logic', 'end_panel_logic', 'top_panel_logic', 'skid_logic', 'left_panel_logic', 'right_panel_logic', 'plywood_layout_generator'],
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
    name='AutoCrate.exe',
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
