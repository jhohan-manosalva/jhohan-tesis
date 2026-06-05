# Trabajo de Grado — Cálculos Mecánicos de Líneas de Transmisión AT

Software educativo para el cálculo mecánico de conductores en líneas de transmisión de alta tensión (catenaria, ecuación de estado, hipótesis de cálculo, distancias de seguridad y verificación RETIE).

El código fuente de la aplicación está en la carpeta [`calculos_mecanicos_at/`](calculos_mecanicos_at/).

## Requisitos

- Python 3.11 o superior

## Cómo correr el programa

```bash
# 1. Clonar el repositorio
git clone https://github.com/jhohan-manosalva/jhohan-tesis.git
cd jhohan-tesis

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python -m streamlit run calculos_mecanicos_at/app.py
```

La aplicación se abre en el navegador en `http://localhost:8501`.

## Estructura del proyecto

- `calculos_mecanicos_at/app.py` — punto de entrada de la aplicación Streamlit
- `calculos_mecanicos_at/modules/` — módulos de cálculo (catenaria, ecuación de estado, cargas mecánicas, etc.)
- `calculos_mecanicos_at/pages/` — páginas de la interfaz
- `calculos_mecanicos_at/config/` — datos de conductores, normativa y zonas climáticas
- `calculos_mecanicos_at/tests/` — pruebas unitarias (`pytest`)
- `calculos_mecanicos_at/docs/manual_usuario.md` — manual de usuario

## Pruebas

```bash
pytest calculos_mecanicos_at/tests/
```
