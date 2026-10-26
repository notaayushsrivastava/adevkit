# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

embedded_skills_path = Path('devkit/skills/embedded')
datas = []
if embedded_skills_path.exists():
    datas.append(('devkit/skills/embedded', 'devkit/skills/embedded'))

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'typer',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.table',
        'inquirerpy',
        'prompt_toolkit',
        'pydantic',
        'pydantic_core',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='devkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
