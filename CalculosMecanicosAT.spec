# -*- mode: python ; coding: utf-8 -*-
"""
Configuracion de PyInstaller para empaquetar el Software de Calculos
Mecanicos AT (Streamlit) como ejecutable de Windows.

Uso:  pyinstaller CalculosMecanicosAT.spec
Salida:  dist/CalculosMecanicosAT/CalculosMecanicosAT.exe
"""
from PyInstaller.utils.hooks import collect_all, copy_metadata

datas = []
binaries = []
hiddenimports = []

# Paquetes con datos/binarios internos que hay que empacar completos.
for pkg in ["streamlit", "altair", "plotly"]:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Streamlit consulta su version en tiempo de ejecucion -> necesita su metadata.
for pkg in ["streamlit"]:
    datas += copy_metadata(pkg)

# Datos propios del proyecto (se conserva la estructura de carpetas).
datas += [
    ("calculos_mecanicos_at", "calculos_mecanicos_at"),
    ("CABLES ACSR.xlsx", "."),
]

# Modulos que se importan de forma indirecta.
hiddenimports += [
    "streamlit.web.cli",
    "openpyxl",
    "matplotlib",
    "reportlab",
    "fpdf",
    "scipy",
]

a = Analysis(
    ["run_app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CalculosMecanicosAT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CalculosMecanicosAT",
)
