# Simulador Físico — Ondas y Óptica Geométrica

```
pip install -r requirements.txt
streamlit run app.py
```

| Archivo | Contenido |
|---|---|
| `dispersion.py` | ω(k) (incluye agua de profundidad finita), velocidades de fase/grupo, paquete 1D, pulso 2D con goteo periódico (frecuencia), amplitud, profundidad y amortiguamiento |
| `optica.py` | Snell, ángulo crítico, prisma (Cauchy), lentes delgadas y espejos esféricos |
| `ondas.py` | Interferencia de fuentes puntuales (λ por frecuencia y profundidad) |
| `visualizacion.py` | Figuras Matplotlib en tema oscuro: tanque de agua, corte, mapa, óptica |
| `estilos.py` | CSS y bloques HTML del diseño |
| `viva.py` | Componentes interactivos bidireccionales (canvas 60 fps) |
| `componentes/optica_viva` | Prisma girable 360°, fotones, reflexión de Fresnel, ley de Snell |
| `componentes/ondas_viva` | Tanque de gotas arrastrables e interferencia con sonda |
| `app.py` | Interfaz Streamlit: Ondas · Óptica Geométrica · Análisis |
