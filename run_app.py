# -*- coding: utf-8 -*-
"""
Lanzador para el ejecutable (.exe) del Software de Calculos Mecanicos AT.

Este archivo NO forma parte de la logica de la aplicacion: su unica funcion
es arrancar Streamlit cuando la aplicacion se empaqueta con PyInstaller.
Ejecuta app.py y abre el navegador automaticamente.
"""
import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli

PORT = 8501


def base_dir() -> Path:
    """Carpeta donde estan los datos (temporal de PyInstaller o carpeta del script)."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def abrir_navegador():
    """Abre el navegador una vez el servidor esta arriba."""
    time.sleep(4)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    base = base_dir()
    app_path = base / "calculos_mecanicos_at" / "app.py"

    # Arranca el navegador en un hilo aparte
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # headless=true evita el aviso de correo en el primer arranque;
    # el navegador lo abrimos nosotros con abrir_navegador().
    #
    # El tema va por parametros y no por .streamlit/config.toml porque Streamlit
    # busca ese archivo en el directorio de trabajo, que en el .exe es el sitio
    # desde donde el usuario lo ejecuta. Debe coincidir con .streamlit/config.toml.
    sys.argv = [
        "streamlit", "run", str(app_path),
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={PORT}",
        "--browser.gatherUsageStats=false",
        "--theme.base=light",
        "--theme.primaryColor=#2874a6",
        "--theme.backgroundColor=#ffffff",
        "--theme.secondaryBackgroundColor=#eaf2f8",
        "--theme.textColor=#2c3e50",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
