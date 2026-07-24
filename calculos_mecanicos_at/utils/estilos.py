"""
Estilos compartidos de la interfaz.

Streamlit no propaga el CSS entre páginas: cada página se renderiza en su propia
ejecución del script. Por eso toda página debe llamar a `aplicar_estilos()`
justo después de `st.set_page_config()`.
"""

from pathlib import Path

import streamlit as st

RUTA_CSS = Path(__file__).parent.parent / "assets" / "estilos.css"


def aplicar_estilos() -> None:
    """Inyecta la hoja de estilos compartida en la página actual."""
    if not RUTA_CSS.exists():
        return
    css = RUTA_CSS.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def encabezado_pagina(icono: str, titulo: str, descripcion: str = "") -> None:
    """
    Dibuja el banner superior de una página.

    Reemplaza el par `st.title()` + `st.markdown()` por un encabezado con
    degradado, sombra e icono, común a todos los módulos.
    """
    descripcion_html = f"<p>{descripcion}</p>" if descripcion else ""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-icono">{icono}</div>
            <div class="hero-texto">
                <h1>{titulo}</h1>
                {descripcion_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
