"""Simulador Físico: Ondas y Óptica Geométrica (Streamlit ≥ 1.37).

Ejecutar con:  streamlit run app.py

Interactividad en tiempo real:
  · Prisma, ley de Snell, tanque de gotas e interferencia son componentes canvas (60 fps)
    con comunicación BIDIRECCIONAL: arrastrar con el mouse actualiza los deslizadores y
    mover un deslizador mueve el gráfico al instante.
  · Solo se ejecuta la sección elegida; cada sección es un @st.fragment.
"""
import inspect
import io

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from estilos import (CSS, ENCABEZADO, PANEL_OPTICA, FRASE,
                     TEORIA_DISPERSION, TEORIA_OPTICA, TEORIA_ESPECTRO)
from optica import (refraccion, reflectancia, CAUCHY, indice_cauchy, desviacion_minima, formacion_imagen,
                    trazar_prisma_rot, phi_desde_theta, theta_desde_phi, LAMBDAS_PRISMA, COLORES_REF)
from ondas import longitud_de_onda
from dispersion import (MODELOS, G, C, W0, BETA, vel_fase, vel_grupo, curvatura, rejilla_x, curva_ancho, pulso_2d)
from visualizacion import figura_pulso_2d, figura_paquete_1d, gif_pulso_2d, figura_lente_espejo
from viva import optica_viva, ondas_viva

st.set_page_config(page_title="Simulador Físico", page_icon="🌊", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(ENCABEZADO, unsafe_allow_html=True)

ss = st.session_state
ANCHO = ({"width": "stretch"} if "width" in inspect.signature(st.button).parameters
         else {"use_container_width": True})
NU = 0.01          # viscosidad: amortigua las ondas cortas
CTES = {"G": G, "C": C, "W0": W0, "BETA": BETA}


# ------------------------------------------------------------------ utilidades
def titulo(icono, texto):
    st.markdown(f'<div class="titulo-panel"><span>{icono}</span>{texto}</div>', unsafe_allow_html=True)


def a_png(fig, dpi=100, transparente=False):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=transparente)   # sin bbox "tight": tamaño fijo
    plt.close(fig)
    return buf.getvalue()


def mostrar(fig, dpi=100, transparente=False):
    st.image(a_png(fig, dpi, transparente), **ANCHO)


def descarga(png, nombre, clave):
    st.download_button("⬇️ Guardar imagen (PNG)", png, file_name=nombre, mime="image/png", key=clave)


def posiciones(n):
    return {1: [(0.0, 0.0)], 2: [(-4.0, 0.0), (4.0, 0.0)],
            3: [(-4.0, -2.0), (4.0, -2.0), (0.0, 4.0)],
            4: [(-5.0, -3.0), (5.0, -3.0), (-5.0, 4.0), (5.0, 4.0)]}[n]


@st.cache_data(show_spinner="Calculando el paquete de ondas…")
def calcular_paquete(modelo, k0, sigma_k, tmax):
    x = rejilla_x(modelo, k0, sigma_k, tmax)
    ts = np.linspace(0, tmax, 21)
    return x, ts, curva_ancho(modelo, k0, sigma_k, x, ts)


@st.cache_data(show_spinner="Generando la animación (unos segundos)…")
def animacion(modelos, fuentes, tmax):
    return gif_pulso_2d(list(modelos), list(fuentes), tmax)


# =====================================================================
#  ONDAS: tanque de gotas en tiempo real (canvas 60 fps, gotas arrastrables)
# =====================================================================
def _pos_defecto(n):
    base = [list(p) for p in posiciones(n)]
    return base + [list(p) for p in posiciones(4)[len(base):]]


def _reiniciar_gotas():
    ss["gpos"] = _pos_defecto(int(ss["n_w"]))


def _sync_tanque():
    v = ss.get("comp_tanque")
    if v and v.get("pos"):
        for i, p in enumerate(v["pos"][:4]):
            ss["gpos"][i] = [float(p[0]), float(p[1])]


@st.fragment
def seccion_ondas():
    ss.setdefault("gpos", _pos_defecto(2))
    col_a, col_b = st.columns([3.65, 1.0], gap="medium")
    with col_a:
        col_par, col_tq = st.columns([1.1, 2.6], gap="medium")
        with col_par, st.container(border=True):
            titulo("〰", "Parámetros de la simulación")
            modelo = st.selectbox("Medio dispersivo", ["agua", "somera", "corte", "flexion", "sin"],
                                  format_func=lambda m: MODELOS[m], key="m_w")
            n_gotas = st.slider("Número de gotas", 1, 4, 2, key="n_w", on_change=_reiniciar_gotas)
            tam = st.slider("Tamaño de la gota (m)", 0.3, 1.5, 0.5, 0.05, key="s_w")
            frec = st.slider("Frecuencia de goteo (Hz)", 0.2, 2.0, 0.45, 0.05, key="f_w")
            amp = st.slider("Amplitud", 0.2, 2.0, 1.0, 0.1, key="a_w")
            prof = st.slider("Profundidad del agua h (m)", 0.3, 30.0, 5.0, 0.1, key="h_w",
                             disabled=(modelo != "somera"),
                             help="Activa con el medio «Agua de profundidad finita».")
            vel = st.slider("Velocidad de la animación (×)", 0.1, 3.0, 1.0, 0.1, key="v_w")
            kt = 1.0 / tam
            st.markdown("**Para k ≈ 1/tamaño:**")
            m1, m2 = st.columns(2)
            m1.metric("v. de fase", f"{float(vel_fase(kt, modelo, prof)):.2f} m/s")
            m2.metric("v. de grupo", f"{float(vel_grupo(kt, modelo, prof)):.2f} m/s")
            st.button("↺ Recolocar gotas", on_click=_reiniciar_gotas, **ANCHO)
        with col_tq, st.container(border=True):
            ondas_viva(mode="tanque", modelo=modelo, n=int(n_gotas), pos=ss["gpos"], tam=float(tam),
                       frec=float(frec), amp=float(amp), prof=float(prof), nu=NU, vel=float(vel),
                       key="comp_tanque", default=None, on_change=_sync_tanque, **CTES)
    with col_b:
        with st.container(border=True):
            st.markdown(PANEL_OPTICA, unsafe_allow_html=True)
        st.markdown(FRASE, unsafe_allow_html=True)


# =====================================================================
#  ÓPTICA GEOMÉTRICA: prisma (giro 360°) · lente · espejo · Snell
# =====================================================================
Y0_DEF, TH_DEF = 0.15, 35.0


def _r1(x):
    return round(float(x), 1)


def _sync_prisma():                       # prisma arrastrado con el mouse → deslizadores
    v = ss.get("comp_prisma")
    if v:
        ss["phi"] = _r1(float(v["phi"]) % 360.0)
        ss["y0"] = round(float(v["y0"]), 2)
        ss["th"] = _r1(theta_desde_phi(ss["alfa"], ss["phi"]))


def _desde_phi():                         # deslizador de giro → incidencia
    ss["th"] = _r1(theta_desde_phi(ss["alfa"], ss["phi"]))


def _desde_th():                          # deslizador de incidencia → giro
    ss["phi"] = _r1(phi_desde_theta(ss["alfa"], ss["th"]))


def _desde_alfa():                        # cambia el ángulo del prisma (el giro físico se conserva)
    ss["th"] = _r1(theta_desde_phi(ss["alfa"], ss["phi"]))


def _sync_snell():
    v = ss.get("comp_snell")
    if v:
        ss["th_snell"] = min(90.0, max(0.0, _r1(v["theta1"])))


def _tabla_prisma(A, B, alfa, phi, y0):
    filas, devs = [], []
    for nombre, lam in COLORES_REF:
        n = float(indice_cauchy(lam, A, B))
        r = trazar_prisma_rot(n, alfa, phi, y0)
        filas.append({"Color": nombre, "λ (nm)": lam, "n": f"{n:.4f}",
                      "δ (°)": f"{r['desviacion']:.2f}" if r["sale"] else "—"})
    for lam in LAMBDAS_PRISMA:
        r = trazar_prisma_rot(float(indice_cauchy(lam, A, B)), alfa, phi, y0)
        if r["sale"]:
            devs.append(r["desviacion"])
    return filas, devs


@st.fragment
def seccion_optica():
    ss.setdefault("alfa", 60)
    ss.setdefault("th", TH_DEF)
    ss.setdefault("phi", _r1(phi_desde_theta(60, TH_DEF)))
    ss.setdefault("y0", Y0_DEF)
    c_par, c_fig, c_res = st.columns([1.05, 2.6, 1.0], gap="medium")
    with c_par, st.container(border=True):
        titulo("△", "Laboratorio de óptica")
        instr = st.selectbox("Instrumento", ["Prisma (dispersión de la luz)", "Lente delgada",
                                             "Espejo esférico", "Refracción (ley de Snell)"], key="instr")
        if instr.startswith("Prisma"):
            material = st.selectbox("Material del prisma", list(CAUCHY), key="mat")
            alfa = st.slider("Ángulo del prisma α (°)", 30, 75, key="alfa", on_change=_desde_alfa)
            phi = st.slider("Giro del prisma φ (°)", 0.0, 360.0, step=0.1, key="phi", on_change=_desde_phi,
                            help="También puedes arrastrar el prisma directamente en el gráfico.")
            theta = st.slider("Ángulo de incidencia θ₁ (°)", -180.0, 180.0, step=0.1, key="th", on_change=_desde_th,
                              help="Incidencia sobre la cara izquierda. Está ligado al giro φ.")
            y0 = st.slider("Altura del láser", -1.0, 1.0, step=0.01, key="y0")
            exag = st.slider("Exagerar dispersión (×)", 1, 12, 4, key="exag",
                             help="Solo amplía el abanico del dibujo; las tablas usan valores reales.")
            vel = st.slider("Velocidad de la animación (×)", 0.1, 3.0, 1.0, 0.1, key="vel_p")
            fotones = st.toggle("Mostrar fotones (v = c/n)", True, key="fot_p")
            refl = st.toggle("Mostrar rayos reflejados (Fresnel)", True, key="refl_p")
            inercia = st.toggle("Inercia al soltar el prisma", True, key="ine_p")
        elif instr == "Lente delgada":
            tl = st.radio("Tipo", ["Convergente", "Divergente"], horizontal=True, key="tl")
            fa = st.slider("Distancia focal |f| (cm)", 2.0, 30.0, 10.0, 0.5, key="fl")
            do = st.slider("Distancia al objeto (cm)", 3.0, 60.0, 25.0, 0.5, key="dol")
            ho = st.slider("Altura del objeto (cm)", 1.0, 6.0, 3.0, 0.5, key="hol")
            f = fa if tl == "Convergente" else -fa
        elif instr == "Espejo esférico":
            te = st.radio("Tipo", ["Cóncavo", "Convexo", "Plano"], horizontal=True, key="te")
            fa = st.slider("Distancia focal |f| (cm)", 2.0, 30.0, 10.0, 0.5, key="fe",
                           disabled=(te == "Plano"))
            do = st.slider("Distancia al objeto (cm)", 3.0, 60.0, 25.0, 0.5, key="doe")
            ho = st.slider("Altura del objeto (cm)", 1.0, 6.0, 3.0, 0.5, key="hoe")
            f = np.inf if te == "Plano" else (fa if te == "Cóncavo" else -fa)
        else:
            presets = {"Personalizado": None, "Aire → Agua": (1.00, 1.33),
                       "Aire → Vidrio": (1.00, 1.50), "Vidrio → Aire": (1.50, 1.00)}
            elegido = st.selectbox("Medios predefinidos", list(presets))
            base = presets[elegido] or (1.00, 1.50)
            n1 = st.number_input("Índice n₁", 1.0, 4.0, base[0], 0.01, key=f"n1_{elegido}")
            n2 = st.number_input("Índice n₂", 1.0, 4.0, base[1], 0.01, key=f"n2_{elegido}")
            ss.setdefault("th_snell", 55.0)
            theta1 = st.slider("Ángulo de incidencia θ₁ (°)", 0.0, 90.0, step=0.1, key="th_snell")
            vel_s = st.slider("Velocidad de la animación (×)", 0.1, 3.0, 1.0, 0.1, key="vel_s")
            fot_s = st.toggle("Mostrar fotones (v = c/n)", True, key="fot_s")

    with c_fig, st.container(border=True):
        if instr.startswith("Prisma"):
            A, B = CAUCHY[material]
            optica_viva(mode="prisma", alfa=int(alfa), phi=float(phi), y0=float(y0), A=A, B=B, exag=int(exag),
                        vel=float(vel), inercia=bool(inercia), fotones=bool(fotones), reflejados=bool(refl),
                        phi_def=_r1(phi_desde_theta(alfa, TH_DEF)), y0_def=Y0_DEF, th_def=TH_DEF,
                        key="comp_prisma", default=None, on_change=_sync_prisma)
        elif instr in ("Lente delgada", "Espejo esférico"):
            tipo = "lente" if instr == "Lente delgada" else "espejo"
            datos = formacion_imagen(tipo, f, do, ho)
            png = a_png(figura_lente_espejo(tipo, f, do, ho, datos))
            st.image(png, **ANCHO); descarga(png, "rayos.png", "dl_lente")
        else:
            res = refraccion(n1, n2, theta1)
            optica_viva(mode="snell", n1=float(n1), n2=float(n2), theta1=float(theta1), vel=float(vel_s),
                        fotones=bool(fot_s), lam=600, th_def=55.0, key="comp_snell", default=None,
                        on_change=_sync_snell)

    with c_res, st.container(border=True):
        titulo("▦", "Resultados")
        if instr.startswith("Prisma"):
            filas, devs = _tabla_prisma(A, B, alfa, phi, y0)
            n550 = float(indice_cauchy(550, A, B))
            r550 = trazar_prisma_rot(n550, alfa, phi, y0)
            st.metric("n rojo (700 nm)", f"{float(indice_cauchy(700, A, B)):.4f}")
            st.metric("n violeta (400 nm)", f"{float(indice_cauchy(400, A, B)):.4f}")
            if not r550["golpea"]:
                st.warning("El haz no toca el prisma: sube o baja el láser, o gira el prisma.")
            elif not devs:
                st.error("Reflexión interna total: ningún color sale. Cambia el giro o reduce α.")
            else:
                if len(devs) < len(LAMBDAS_PRISMA):
                    st.warning(f"{len(LAMBDAS_PRISMA) - len(devs)} de {len(LAMBDAS_PRISMA)} colores quedan atrapados (RIT).")
                st.metric("Abertura del espectro Δθ", f"{max(devs) - min(devs):.2f}°")
                st.metric("Incidencia real θ₁", f"{r550['theta_inc']:.1f}°")
                st.caption(f"Desviación mínima (550 nm): {desviacion_minima(n550, alfa):.2f}°")
                st.table(filas)
        elif instr in ("Lente delgada", "Espejo esférico"):
            if datos["infinito"]:
                st.info("El objeto está en el foco: la imagen se forma en el infinito.")
            else:
                st.metric("Distancia imagen dᵢ", f"{datos['di']:.2f} cm")
                st.metric("Aumento m", f"{datos['m']:.2f}")
                st.metric("Altura imagen", f"{abs(datos['h_img']):.2f} cm")
                tam_i = ("ampliada" if abs(datos["m"]) > 1.001 else
                         "reducida" if abs(datos["m"]) < 0.999 else "del mismo tamaño")
                st.markdown(f"**Imagen:** {'real' if datos['real'] else 'virtual'}, "
                            f"{'derecha' if datos['derecha'] else 'invertida'}, {tam_i}")
            st.caption("1/f = 1/dₒ + 1/dᵢ")
        else:
            if res["rit"]:
                st.error(f"Reflexión interna total (θ₁ = {theta1:.1f}° > θc = {res['theta_critico']:.1f}°)")
            else:
                st.metric("Ángulo refractado θ₂", f"{res['theta2']:.1f}°")
                st.metric("Desviación δ", f"{res['desviacion']:.1f}°")
            st.metric("Ángulo reflejado θr", f"{theta1:.1f}°")
            st.metric("Energía reflejada R", f"{100 * reflectancia(n1, n2, theta1):.1f} %")
            if res["theta_critico"] is not None:
                st.info(f"Ángulo crítico: {res['theta_critico']:.1f}°")
            st.caption("n₁·sen θ₁ = n₂·sen θ₂")


# =====================================================================
#  TEORÍA
# =====================================================================
def seccion_teoria():
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, html in ((c1, TEORIA_DISPERSION), (c2, TEORIA_OPTICA), (c3, TEORIA_ESPECTRO)):
        with col, st.container(border=True):
            st.markdown(html, unsafe_allow_html=True)
    with st.expander("📐 Fórmulas clave"):
        f1, f2 = st.columns(2)
        with f1:
            st.latex(r"\omega=\omega(k)\qquad v_f=\frac{\omega}{k}\qquad v_g=\frac{d\omega}{dk}")
            st.latex(r"\omega^2=g\,k\tanh(kh)")
        with f2:
            st.latex(r"n_1\sin\theta_1=n_2\sin\theta_2\qquad \theta_c=\arcsin\frac{n_2}{n_1}")
            st.latex(r"n(\lambda)=A+\frac{B}{\lambda^2}\qquad \frac1f=\frac1{d_o}+\frac1{d_i}")
    with st.expander("🧭 ¿Cómo usar el simulador?"):
        st.markdown("- **Ondas:** elige el medio, el número de gotas, su frecuencia, amplitud y la profundidad; "
                    "arrastra las gotas o toca el agua para soltar otra.\n"
                    "- **Óptica Geométrica:** arrastra el prisma para girarlo 360° (los deslizadores se mueven con él) "
                    "o mueve los deslizadores y el prisma gira.\n"
                    "- **Análisis:** compara con un medio sin dispersión, paquetes 1D e interferencia.")


# =====================================================================
#  ANÁLISIS: comparación · paquete 1D · interferencia
# =====================================================================
def _sync_interf():                        # fuentes arrastradas con el mouse → campos x, y
    v = ss.get("comp_interf")
    if v and v.get("pos"):
        for i, p in enumerate(v["pos"][:5]):
            ss[f"x{i}"] = max(-12.0, min(12.0, float(p[0])))
            ss[f"y{i}"] = max(-12.0, min(12.0, float(p[1])))


@st.fragment
def seccion_analisis():
    sub = st.radio("sub", ["💧 Sin dispersión vs dispersión", "〰️ Paquete de ondas 1D",
                           "✳️ Interferencia continua"], horizontal=True, key="nav2",
                   label_visibility="collapsed")
    with st.container(border=True):
        if sub.startswith("💧"):
            cp, cg = st.columns([1, 2.4])
            with cp:
                m_c = st.selectbox("Medio", ["agua", "somera", "corte", "flexion"],
                                   format_func=lambda m: MODELOS[m], key="m2d")
                t_c = st.slider("Tiempo t (s)", 0.0, 10.0, 6.0, 0.25, key="t2d")
                n_c = st.slider("Número de gotas", 1, 3, 1, key="nf2d")
                s_c = st.slider("Tamaño de la gota (m)", 0.3, 1.5, 0.5, 0.05, key="s2d")
                comun_c = st.checkbox("Misma escala de color", False, key="esc2d")
            fu_c = [(sx, sy, 1.0) for sx, sy in posiciones(n_c)]
            x_c, p_ref = pulso_2d("sin", t_c, fu_c, n=256, s=s_c)
            _, p_dis = pulso_2d(m_c, t_c, fu_c, n=256, s=s_c)
            with cg:
                png = a_png(figura_pulso_2d(x_c, [p_ref, p_dis], ["sin", m_c], t_c, comun_c))
                st.image(png, **ANCHO); descarga(png, "dispersion_pulso.png", "dl_pulso")
            if st.button("🎞️ Generar animación (GIF)", key="gif2d"):
                gif = animacion(("sin", m_c), tuple(fu_c), 10.0)
                st.image(gif, caption="Sin dispersión (izq.) y con dispersión (der.)")
                st.download_button("⬇️ Descargar GIF", gif, file_name="dispersion.gif",
                                   mime="image/gif", key="dl_gif")
        elif sub.startswith("〰️"):
            cp, cg = st.columns([1, 2.4])
            with cp:
                modelo1 = st.selectbox("Medio", list(MODELOS), index=4,
                                       format_func=lambda m: MODELOS[m], key="m1d")
                k0 = st.slider("Número de onda central k₀ (rad/m)", 1.0, 5.0, 2.0, 0.1, key="k01d")
                sig = st.slider("Anchura espectral σₖ (rad/m)", 0.1, 0.6, 0.4, 0.05, key="sk1d")
                sig_ef = min(sig, k0 / 4)
                if sig_ef < sig:
                    st.warning(f"σₖ se limitó a {sig_ef:.2f} (k₀/4) para mantener k > 0.")
                t1 = st.slider("Tiempo t (s)", 0.0, 10.0, 10.0, 0.5, key="t1d")
                c1, c2 = st.columns(2)
                c1.metric("v. de fase", f"{float(vel_fase(k0, modelo1)):.2f} m/s")
                c2.metric("v. de grupo", f"{float(vel_grupo(k0, modelo1)):.2f} m/s")
                st.metric("Curvatura ω″", f"{float(curvatura(k0, modelo1)):.3f}")
            x1, ts1, ancho1 = calcular_paquete(modelo1, k0, sig_ef, 10.0)
            with cg:
                png = a_png(figura_paquete_1d(modelo1, k0, sig_ef, x1, t1, ts1, ancho1))
                st.image(png, **ANCHO); descarga(png, "dispersion_paquete.png", "dl_paquete")
        else:
            cp, cg = st.columns([1, 2.4])
            defecto = [(-2.5, 0.0), (2.5, 0.0), (0.0, 4.5), (0.0, -4.5), (5.0, 3.0)]
            for i in range(5):
                ss.setdefault(f"x{i}", defecto[i][0]); ss.setdefault(f"y{i}", defecto[i][1])
            with cp:
                n_fuentes = st.slider("Número de fuentes", 1, 5, 3, key="nfi")
                modo = st.radio("Definir la onda por", ["Longitud de onda", "Frecuencia y profundidad"], key="modo_i")
                if modo == "Longitud de onda":
                    lam = st.slider("Longitud de onda λ (m)", 0.5, 3.0, 1.0, 0.05, key="lam_i")
                    frec_i = st.slider("Frecuencia f (Hz)", 0.2, 2.0, 1.0, 0.05, key="fi_lam")
                else:
                    frec_i = st.slider("Frecuencia f (Hz)", 0.3, 2.0, 0.8, 0.05, key="fi")
                    prof_i = st.slider("Profundidad h (m)", 0.1, 10.0, 2.0, 0.1, key="pi")
                    lam = float(longitud_de_onda(frec_i, "somera", prof_i))
                    st.caption(f"λ = {lam:.2f} m  (ω² = g·k·tanh(k·h))")
                rango = st.slider("Tamaño de la región (± m)", 4, 12, 8, key="rg_i")
                vista = st.radio("Vista", ["Onda en movimiento", "Patrón de intensidad (franjas)"], key="vista_i")
                vel_i = st.slider("Velocidad de la animación (×)", 0.1, 3.0, 1.0, 0.1, key="vel_i")
                fuentes_i = []
                for i in range(n_fuentes):
                    with st.expander(f"Fuente {i + 1}", expanded=(i == 0)):
                        sx = st.number_input("x", -12.0, 12.0, step=0.5, format="%.1f", key=f"x{i}")
                        sy = st.number_input("y", -12.0, 12.0, step=0.5, format="%.1f", key=f"y{i}")
                        amp_i = st.slider("Amplitud", 0.1, 2.0, 1.0, 0.1, key=f"a{i}")
                        fase = st.slider("Fase (rad)", 0.0, 6.28, 0.0, 0.1, key=f"f{i}")
                    fuentes_i.append([float(sx), float(sy), float(amp_i), float(fase)])
            with cg:
                ondas_viva(mode="interferencia", fuentes=fuentes_i, lam=float(lam), f=float(frec_i),
                           rango=float(rango), vel=float(vel_i),
                           vista="intensidad" if vista.startswith("Patrón") else "onda",
                           key="comp_interf", default=None, on_change=_sync_interf, **CTES)


# =====================================================================
#  NAVEGACIÓN: solo se ejecuta la sección elegida
# =====================================================================
SECCIONES = {"🌊 Ondas": seccion_ondas, "🔺 Óptica Geométrica": seccion_optica,
             "📘 Teoría": seccion_teoria, "📈 Análisis": seccion_analisis}
elegida = st.radio("Sección", list(SECCIONES), horizontal=True, key="nav", label_visibility="collapsed")
SECCIONES[elegida]()
