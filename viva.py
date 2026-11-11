"""Componentes interactivos (canvas en el navegador, 60 fps) con comunicación bidireccional."""
import os
import streamlit.components.v1 as components

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "componentes")
optica_viva = components.declare_component("optica_viva", path=os.path.join(_DIR, "optica_viva"))
ondas_viva = components.declare_component("ondas_viva", path=os.path.join(_DIR, "ondas_viva"))
