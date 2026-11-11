"""Módulo de visualización con Matplotlib."""
from functools import lru_cache
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon, Rectangle

AZUL = "#7FD1FF"
FONDO = "#0b1d42"
TEXTO = "#cfe3ff"
plt.rcParams.update({
    "figure.facecolor": FONDO, "axes.facecolor": "#07142f", "savefig.facecolor": FONDO,
    "axes.edgecolor": "#3a68b8", "axes.labelcolor": TEXTO, "text.color": TEXTO,
    "xtick.color": TEXTO, "ytick.color": TEXTO, "grid.color": "#2a4a86",
    "legend.facecolor": "#0b1d42", "legend.edgecolor": "#2a4a86", "font.size": 9,
})
# Agua luminosa: cian (valle) → azul profundo (reposo) → naranja (cresta)
CMAP_AGUA = LinearSegmentedColormap.from_list(
    "agua", ["#00e5ff", "#0a62d6", "#06204f", "#d9641a", "#ffd27a"])


def figura_refraccion(n1, n2, theta1, res):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axhspan(0, 1.2, color="#0b2a5e")
    ax.axhspan(-1.2, 0, color="#0e4fa0")
    ax.axhline(0, color=AZUL, lw=2)
    ax.plot([0, 0], [-1.1, 1.1], "--", color=TEXTO, lw=1)
    t1 = np.radians(theta1)
    ax.annotate("", xy=(0, 0), xytext=(-np.sin(t1), np.cos(t1)),
                arrowprops=dict(arrowstyle="-|>", color="#ff5a5a", lw=2.5))
    if res["rit"]:
        ax.annotate("", xy=(np.sin(t1), np.cos(t1)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color="#c08cff", lw=2.5))
        ax.text(0.05, -0.6, "REFLEXIÓN\nINTERNA TOTAL", color="#c08cff",
                fontsize=12, fontweight="bold")
    else:
        r = np.radians(res["theta2"])
        ax.annotate("", xy=(np.sin(r), -np.cos(r)), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color="#4db8ff", lw=2.5))
        ax.plot([0, np.sin(t1)], [0, np.cos(t1)], color="#C00000", lw=1, alpha=0.35)
    ax.text(-1.15, 1.05, f"Medio 1  (n₁ = {n1:.2f})", fontsize=10, color=AZUL)
    ax.text(-1.15, -1.12, f"Medio 2  (n₂ = {n2:.2f})", fontsize=10, color=AZUL)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("Diagrama de rayos", color=AZUL)
    fig.tight_layout()
    return fig


def figura_ondas(x, y, psi, fuentes):
    fig, ax = plt.subplots(figsize=(7, 6))
    # Escala robusta: ignora los picos cercanos a las fuentes (1/√r) para ver el patrón
    lim = float(np.percentile(np.abs(psi), 97)) or 1.0
    im = ax.imshow(psi, extent=[x[0], x[-1], y[0], y[-1]], origin="lower",
                   cmap=CMAP_AGUA, vmin=-lim, vmax=lim)
    for sx, sy, *_ in fuentes:
        ax.plot(sx, sy, "*", color="white", ms=14, mfc="yellow")
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title("Interferencia por superposición", color=AZUL)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03, label="Perturbación ψ (u.a.)")
    fig.tight_layout()
    return fig


# =====================================================================
#  Dispersión de ondas
# =====================================================================
from dispersion import (MODELOS, omega, vel_fase, vel_grupo, paquete_1d,
                        ancho_analitico, pulso_2d)
from optica import CAUCHY, indice_cauchy, trazar_prisma, desviacion_minima

ROJO, GRIS = "#ff5a5a", "#9fb4d6"


def _titulo_corto(modelo):
    return MODELOS[modelo].split(":")[0]


def figura_pulso_2d(x, psis, modelos, t, escala_comun=False):
    """Mapas de calor y corte y=0 de un mismo pulso en distintos medios."""
    n = len(x)
    ymax = max(float(np.abs(p).max()) for p in psis) * 1.15 or 1.0
    comun = max(float(np.percentile(np.abs(p), 99.5)) for p in psis) or 1.0
    fig = plt.figure(figsize=(11, 7.4))
    gs = fig.add_gridspec(2, len(psis), height_ratios=[3, 1.3], hspace=0.38, wspace=0.2)
    for i, (psi, m) in enumerate(zip(psis, modelos)):
        lim = comun if escala_comun else (float(np.percentile(np.abs(psi), 99.5)) or 1.0)
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(psi, extent=[x[0], x[-1], x[0], x[-1]], origin="lower",
                  cmap=CMAP_AGUA, vmin=-lim, vmax=lim)
        ax.set_title(f"{_titulo_corto(m)}\nψ máx = {np.abs(psi).max():.3f}", color=AZUL, fontsize=11)
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        axc = fig.add_subplot(gs[1, i])
        axc.plot(x, psi[n // 2, :], color=ROJO if m == "sin" else "#4db8ff", lw=1.4)
        axc.axhline(0, color=GRIS, lw=0.6)
        axc.set_ylim(-ymax, ymax)
        axc.set_xlim(x[0], x[-1])
        axc.set_xlabel("x (m)   —   corte a lo largo de y = 0")
        axc.set_ylabel("ψ")
    fig.suptitle(f"Dispersión de un pulso 2D   (t = {t:.2f} s)", color=AZUL, fontweight="bold")
    return fig


def figura_paquete_1d(modelo, k0, sigma_k, x, t, ts, ancho_num):
    """Relación de dispersión, paquete de ondas en el instante t y su ensanchamiento."""
    vf, vg = float(vel_fase(k0, modelo)), float(vel_grupo(k0, modelo))
    psi0 = paquete_1d(modelo, k0, sigma_k, x, 0.0)
    psi = paquete_1d(modelo, k0, sigma_k, x, t)
    fig = plt.figure(figsize=(11, 7.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15], hspace=0.42, wspace=0.28)

    # (a) relación de dispersión
    ax = fig.add_subplot(gs[0, 0])
    ks = np.linspace(0.05, 6, 300)
    ax.plot(ks, omega(ks, modelo), color=AZUL, lw=2, label="ω(k)")
    w0 = float(omega(k0, modelo))
    ax.plot(ks, vf * ks, "--", color=ROJO, lw=1, label=f"pendiente ω/k = v_f = {vf:.2f}")
    ax.plot(ks, w0 + vg * (ks - k0), ":", color="#4db8ff", lw=1.6, label=f"tangente dω/dk = v_g = {vg:.2f}")
    ax.plot(k0, w0, "o", color="white")
    ax.set_xlim(0, 6); ax.set_ylim(0, max(float(omega(6, modelo)) * 1.05, 1))
    ax.set_xlabel("k  (rad/m)"); ax.set_ylabel("ω  (rad/s)")
    ax.set_title("Relación de dispersión", color=AZUL, fontsize=11)
    ax.legend(fontsize=8, loc="upper left")

    # (b) ensanchamiento
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(ts, ancho_num, "o", color="#4db8ff", ms=4, label="cálculo numérico")
    tt = np.linspace(0, ts[-1], 100)
    ax2.plot(tt, [ancho_analitico(modelo, k0, sigma_k, u) for u in tt], "-", color=ROJO, lw=1.2, label="fórmula teórica")
    ax2.axvline(t, color=GRIS, lw=1, ls="--")
    ax2.set_xlabel("t  (s)"); ax2.set_ylabel("ancho del paquete σx (m)")
    ax2.set_ylim(0, max(float(np.max(ancho_num)) * 1.2, 1))
    ax2.set_title("Ensanchamiento del paquete", color=AZUL, fontsize=11)
    ax2.legend(fontsize=8, loc="lower right")

    # (c) el paquete
    ax3 = fig.add_subplot(gs[1, :])
    ax3.fill_between(x, -np.abs(psi0), np.abs(psi0), color=GRIS, alpha=0.18, label="envolvente en t = 0")
    ax3.plot(x, np.real(psi), color="#4db8ff", lw=1.2, label="onda ψ(x, t)")
    ax3.plot(x, np.abs(psi), color=AZUL, lw=2, label="envolvente |ψ|")
    ax3.plot(x, -np.abs(psi), color=AZUL, lw=2)
    xg = vg * t
    ax3.plot(xg, np.abs(psi[np.argmin(np.abs(x - xg))]), "s", color="white", ms=8, label=f"centro del paquete (v_g·t = {xg:.1f} m)")
    xf = vf * t
    if x[0] <= xf <= x[-1]:
        ax3.plot(xf, np.real(psi[np.argmin(np.abs(x - xf))]), "o", color=ROJO, ms=8, label=f"una cresta (v_f·t = {xf:.1f} m)")
    ax3.set_xlim(x[0], x[-1]); ax3.set_ylim(-1.15, 1.15)
    ax3.set_xlabel("x  (m)"); ax3.set_ylabel("ψ")
    ax3.set_title(f"Paquete de ondas en t = {t:.1f} s", color=AZUL, fontsize=11)
    ax3.legend(fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    fig.suptitle(MODELOS[modelo], color=AZUL, fontweight="bold")
    return fig


def _rgb_longitud_onda(lam):
    """Color aproximado de una longitud de onda visible (nm)."""
    if lam < 440:   r, g, b = -(lam - 440) / 60, 0.0, 1.0
    elif lam < 490: r, g, b = 0.0, (lam - 440) / 50, 1.0
    elif lam < 510: r, g, b = 0.0, 1.0, -(lam - 510) / 20
    elif lam < 580: r, g, b = (lam - 510) / 70, 1.0, 0.0
    elif lam < 645: r, g, b = 1.0, -(lam - 645) / 65, 0.0
    else:           r, g, b = 1.0, 0.0, 0.0
    f = 0.3 + 0.7 * (lam - 380) / 40 if lam < 420 else (0.3 + 0.7 * (750 - lam) / 50 if lam > 700 else 1.0)
    return tuple(max(0.0, min(1.0, (c * f) ** 0.8)) for c in (r, g, b))


def _desenfoque(img, sigma):
    """Desenfoque gaussiano separable (NumPy puro)."""
    r = max(1, int(3 * sigma))
    k = np.exp(-(np.arange(-r, r + 1) ** 2) / (2 * sigma ** 2)).astype(np.float32)
    k /= k.sum()
    p = np.pad(img, ((r, r), (0, 0), (0, 0)))
    o = sum(k[i] * p[i:i + img.shape[0]] for i in range(2 * r + 1))
    p = np.pad(o, ((0, 0), (r, r), (0, 0)))
    return sum(k[i] * p[:, i:i + img.shape[1]] for i in range(2 * r + 1))


def _trazo(lienzo, p0, p1, color, peso, ext):
    """Suma (mezcla aditiva) un segmento de luz sobre el lienzo."""
    H, W = lienzo.shape[:2]
    x0, x1, y0, y1 = ext
    a = np.array([(p0[0] - x0) / (x1 - x0) * (W - 1), (y1 - p0[1]) / (y1 - y0) * (H - 1)])
    b = np.array([(p1[0] - x0) / (x1 - x0) * (W - 1), (y1 - p1[1]) / (y1 - y0) * (H - 1)])
    n = int(np.hypot(*(b - a)) * 1.5) + 2
    t = np.linspace(0.0, 1.0, n)
    xs = np.rint(a[0] + (b[0] - a[0]) * t).astype(int)
    ys = np.rint(a[1] + (b[1] - a[1]) * t).astype(int)
    ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
    np.add.at(lienzo, (ys[ok], xs[ok]), np.asarray(color, np.float32) * peso)


def figura_prisma(material, alfa, theta_i, n_rayos=160, exagerar=1.0, h=1.6):
    """Luz blanca dispersada por un prisma: haz neón con espectro continuo.

    Lienzo de tamaño fijo (900×460 px) y encuadre fijo con el prisma centrado,
    para que la imagen no se mueva ni se deforme al cambiar los parámetros.
    exagerar > 1 amplía solo el abanico del dibujo (la curva δ(λ) es real).
    Devuelve (fig, lams, deltas).
    """
    A, B = CAUCHY[material]
    W, H = 900, 460
    cy = h / 2
    ext = (-4.5, 4.5, cy - 2.3, cy + 2.3)
    lams = np.linspace(400, 700, n_rayos)
    base = trazar_prisma(float(indice_cauchy(550, A, B)), alfa, theta_i, h=h)
    lienzo = np.zeros((H, W, 3), np.float32)
    blanco = (1.0, 1.0, 1.0)
    P1 = base["P1"]
    _trazo(lienzo, P1 - 9.0 * base["d0"], P1, blanco, 1.6, ext)
    ang_ref = float(np.arctan2(base["d2"][1], base["d2"][0])) if base["sale"] else None
    peso = 0.18 * 160.0 / n_rayos
    deltas = []
    for lam in lams:
        r = trazar_prisma(float(indice_cauchy(lam, A, B)), alfa, theta_i, h=h)
        col = np.array(_rgb_longitud_onda(lam), np.float32)
        deltas.append(r["desviacion"] if r["sale"] else np.nan)
        _trazo(lienzo, r["P1"], r["P2"], col, 0.8 * peso, ext)
        if r["sale"]:
            d = r["d2"]
            if ang_ref is not None and exagerar != 1.0:
                ang = ang_ref + exagerar * (float(np.arctan2(d[1], d[0])) - ang_ref)
                d = np.array([np.cos(ang), np.sin(ang)])
            _trazo(lienzo, r["P2"], r["P2"] + 9.0 * d, col, peso, ext)
    nucleo = _desenfoque(lienzo, 0.9)
    medio = lienzo.reshape(H // 2, 2, W // 2, 2, 3).mean(axis=(1, 3))
    brillo = np.repeat(np.repeat(_desenfoque(medio, 5.0), 2, axis=0), 2, axis=1)
    amplio = np.repeat(np.repeat(_desenfoque(medio, 14.0), 2, axis=0), 2, axis=1)
    luz = 1.0 - np.exp(-(2.6 * nucleo + 3.0 * brillo + 1.6 * amplio))
    fondo = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    fondo = (1 - fondo) * np.array([0.01, 0.02, 0.05]) + fondo * np.array([0.03, 0.07, 0.15])
    img = np.clip(fondo + luz, 0, 1)

    fig = plt.figure(figsize=(9, 4.6), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, extent=ext, aspect="equal", interpolation="bilinear")
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.axis("off")
    ax.add_patch(Polygon([base["A"], base["B"], base["C"]], closed=True,
                         fc=(0.55, 0.78, 1.0, 0.10), ec=(0.88, 0.95, 1.0, 0.95), lw=1.8, zorder=5))
    for p, q in ((base["A"], base["B"]), (base["A"], base["C"])):
        ax.plot([p[0], q[0]], [p[1], q[1]], color=(0.7, 0.88, 1, 0.35), lw=5, zorder=4)
    th = np.radians(theta_i)
    rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
    nrm = rot @ base["d0"]
    ax.plot([P1[0] - 0.8 * nrm[0], P1[0] + 0.8 * nrm[0]], [P1[1] - 0.8 * nrm[1], P1[1] + 0.8 * nrm[1]],
            "--", color="white", alpha=0.4, lw=1, zorder=6)
    ax.text(0.015, 0.96, f"{material}\nα = {alfa}°   ·   θ₁ = {theta_i}°", transform=ax.transAxes,
            color="#cfe3ff", fontsize=9, va="top", linespacing=1.5)
    if exagerar != 1.0:
        ax.text(0.985, 0.03, f"separación de colores ×{exagerar:g} (solo el dibujo)",
                transform=ax.transAxes, color="#8fa8d0", fontsize=8, ha="right")
    return fig, lams, np.array(deltas, dtype=float)


def figura_deltas(lams, deltas):
    """Curva real δ(λ): el violeta se desvía más que el rojo."""
    fig, ax2 = plt.subplots(figsize=(4.6, 2.9))
    ax2.plot(lams, deltas, color="#9fb4d6", lw=1)
    ax2.scatter(lams, deltas, c=[_rgb_longitud_onda(l) for l in lams], s=22, zorder=3)
    ax2.set_xlabel("longitud de onda λ (nm)"); ax2.set_ylabel("desviación δ (°)")
    ax2.set_title("δ(λ) real", color=AZUL, fontsize=10)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    return fig


# =====================================================================
#  Simulador de ondas (tanque de agua, corte y mapa de amplitud)
# =====================================================================
@lru_cache(maxsize=8)
def _malla_tanque(n, W=760, H=470):
    """Índices (cacheados) para proyectar el campo n×n sobre el tanque en perspectiva."""
    px = np.linspace(-1.04, 1.04, W); py = np.linspace(-0.03, 0.98, H)
    PX, PY = np.meshgrid(px, py)
    V = PY / 0.72
    U = PX / np.maximum(1 - 0.30 * V, 1e-6)
    dentro = (V >= 0) & (V <= 1) & (np.abs(U) <= 1)
    fx = np.clip((U + 1) / 2 * (n - 1), 0, n - 1); fy = np.clip(V * (n - 1), 0, n - 1)
    i0 = np.floor(fx).astype(int); j0 = np.floor(fy).astype(int)
    return dentro, i0, np.minimum(i0 + 1, n - 1), j0, np.minimum(j0 + 1, n - 1), fx - i0, fy - j0


_LUT = (CMAP_AGUA(np.linspace(0, 1, 256)) * 255).astype(np.uint8)


def figura_tanque(x, psi, t, lim, fuentes=()):
    """Tanque de agua en perspectiva (rápido: un solo imshow) con grifos sobre cada fuente."""
    R = float(np.abs(x).max())
    dentro, i0, i1, j0, j1, wx, wy = _malla_tanque(len(x))
    P = ((1 - wy) * ((1 - wx) * psi[j0, i0] + wx * psi[j0, i1])
         + wy * ((1 - wx) * psi[j1, i0] + wx * psi[j1, i1]))
    rgba = _LUT[(np.clip(P / lim, -1, 1) * 127.5 + 127.5).astype(np.uint8)].copy()
    rgba[..., 3] = np.where(dentro, 255, 0)
    fig = plt.figure(figsize=(9.2, 5.6), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(rgba, extent=(-1.04, 1.04, -0.03, 0.98), origin="lower",
              interpolation="bilinear", aspect="equal")
    ax.add_patch(Polygon([(-1, 0), (1, 0), (0.70, 0.72), (-0.70, 0.72)], closed=True,
                         fill=False, ec="#8aa0c0", lw=3.5))
    for sx, sy, *_ in fuentes:
        gx = float(np.clip(sx / R, -1, 1)) * 0.70
        ax.add_patch(Rectangle((gx - 0.035, 0.74), 0.07, 0.10, fc="#9aa6b8", ec="#dbe6f5", lw=1.2, zorder=5))
        ax.add_patch(Rectangle((gx - 0.05, 0.82), 0.10, 0.03, fc="#cfd8e6", ec="#ffffff", lw=1, zorder=5))
    chip = dict(boxstyle="round,pad=0.45", fc=FONDO, ec="#3a68b8", alpha=0.92)
    ax.text(-0.97, 0.97, "Vista de ondas (2D)", color="white", fontsize=9, va="top", bbox=chip, zorder=6)
    ax.text(0.97, 0.97, f"t = {t:.2f} s", color="white", fontsize=10, va="top", ha="right", bbox=chip, zorder=6)
    ar = dict(arrowstyle="-|>", color="white", lw=1.4)
    ax.annotate("", xy=(-0.93, 0.15), xytext=(-0.93, 0.02), arrowprops=ar)
    ax.annotate("", xy=(-0.79, 0.02), xytext=(-0.93, 0.02), arrowprops=ar)
    ax.text(-0.95, 0.17, "y", color="white", fontsize=9)
    ax.text(-0.77, 0.0, "x", color="white", fontsize=9)
    ax.set_xlim(-1.04, 1.04); ax.set_ylim(-0.03, 0.98); ax.axis("off")
    return fig


def figura_corte(x, psi, ymax):
    """Cortes de ψ a lo largo de y = 0 (rojo) y x = 0 (azul)."""
    n = len(x)
    fig, ax = plt.subplots(figsize=(4.6, 3.5))
    ax.plot(x, psi[n // 2, :], color="#ff3b3b", lw=1.6, label="Corte a lo largo de y = 0")
    ax.plot(x, psi[:, n // 2], color="#2f6bff", lw=1.6, label="Corte a lo largo de x = 0")
    ax.axhline(0, color=GRIS, lw=0.6)
    ax.set_xlim(-15, 15); ax.set_ylim(-ymax, ymax); ax.grid(alpha=0.3)
    ax.set_xlabel("x (m)"); ax.set_ylabel("ψ")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    fig.tight_layout()
    return fig


def figura_mapa(x, psi, lim):
    """Mapa de amplitud ψ(x, y) con barra de color."""
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    im = ax.imshow(psi, extent=[x[0], x[-1] + (x[1] - x[0]), x[0], x[-1] + (x[1] - x[0])],
                   origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim)
    ax.set_xlim(-15, 15); ax.set_ylim(-15, 15)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.04)
    fig.tight_layout()
    return fig


def miniatura(psi, lim):
    """Imagen RGB (array uint8) del campo, para la vista previa de la animación."""
    idx = (np.clip(psi / lim, -1, 1) + 1) / 2
    return (CMAP_AGUA(idx[::-1, :])[..., :3] * 255).astype(np.uint8)


# =====================================================================
#  Óptica: lentes delgadas y espejos esféricos
# =====================================================================
def figura_lente_espejo(tipo, f, do, h, datos):
    """Diagrama de rayos principales de una lente delgada o de un espejo."""
    lente = tipo == "lente"
    real = datos["real"]
    inf = datos["infinito"]
    xi, yi = (datos["x_img"], datos["h_img"]) if not inf else (np.nan, np.nan)
    L = max(do * 1.25, 2.3 * (abs(f) if np.isfinite(f) else do),
            min(abs(datos["di"]), 80) * 1.25 if not inf else 0)
    H = max(h * 1.9, min(abs(yi), 60) * 1.5 if not inf else 0)
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.set_xlim(-L, L); ax.set_ylim(-H, H); ax.grid(alpha=0.15)
    ax.axhline(0, color=TEXTO, lw=0.8)
    # elemento óptico
    if lente:
        ax.plot([0, 0], [-H * 0.95, H * 0.95], color="#7fd3ff", lw=3)
        a, b = ("^", "v") if f > 0 else ("v", "^")
        ax.plot(0, H * 0.95, a, color="#7fd3ff", ms=11); ax.plot(0, -H * 0.95, b, color="#7fd3ff", ms=11)
        ax.text(0.01 * L, H * 0.88, "Lente " + ("convergente" if f > 0 else "divergente"), color="#7fd3ff")
    else:
        if np.isinf(f):
            ax.plot([0, 0], [-H * 0.95, H * 0.95], color="#cfe3ff", lw=3)
            ys = np.linspace(-H * 0.95, H * 0.95, 25)
            for yy in ys:
                ax.plot([0, 0.03 * L], [yy, yy - 0.05 * H], color="#6f86b3", lw=1)
        else:
            R = 2 * abs(f)
            ys = np.linspace(-H * 0.95, H * 0.95, 80)
            sag = R - np.sqrt(np.maximum(R ** 2 - ys ** 2, 1e-9))
            xs = -sag if f > 0 else sag
            ax.plot(xs, ys, color="#cfe3ff", lw=3)
            for yy, xx in zip(ys[::4], xs[::4]):
                ax.plot([xx, xx + 0.03 * L], [yy, yy - 0.05 * H], color="#6f86b3", lw=1)
        nombre = "plano" if np.isinf(f) else ("cóncavo" if f > 0 else "convexo")
        ax.text(0.04 * L, H * 0.88, f"Espejo {nombre}", color="#cfe3ff")
    # focos
    if np.isfinite(f):
        pts = [(-f, "F"), (f, "F'")] if lente else [(-f, "F"), (-2 * f, "C")]
        for px, lab in pts:
            if abs(px) < L:
                ax.plot(px, 0, "o", color="white", ms=5)
                ax.text(px, -0.09 * H, lab, ha="center", color="white")
    # objeto
    ax.annotate("", xy=(-do, h), xytext=(-do, 0), arrowprops=dict(arrowstyle="-|>", color="#ffd54a", lw=3))
    ax.text(-do, -0.09 * H, "Objeto", ha="center", color="#ffd54a")
    tip = np.array([-do, h])

    def seg(p0, p1, col, ls="-", lw=1.8):
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=col, ls=ls, lw=lw)

    def extender(p, d, col):
        d = np.asarray(d, float)
        if abs(d[0]) < 1e-9:
            return
        xe = L if d[0] > 0 else -L
        seg(p, p + d * (xe - p[0]) / d[0], col)

    sgn = 1 if lente else -1          # lado hacia el que salen los rayos reales
    P1 = np.array([0.0, h])
    f_x = np.nan if np.isinf(f) else (f if lente else -f)   # foco del lado de salida
    cols = ["#ff5a5a", "#3ddc97", "#ffa94d"]
    # rayo 1: paralelo → pasa por el foco
    seg(tip, P1, cols[0])
    if inf:
        D1 = np.array([f_x, -h])
    else:
        D1 = np.array([xi, yi - h]) if real else np.array([-xi, h - yi])
    extender(P1, D1, cols[0])
    # rayo 2: por el centro / vértice
    seg(tip, (0, 0), cols[1])
    D2 = np.array([do, -h]) if lente else np.array([-do, -h])
    extender(np.array([0.0, 0.0]), D2, cols[1])
    # rayo 3: por el foco → sale paralelo
    if np.isfinite(f) and abs(do - f) > 1e-9:
        y3 = h * f / (f - do)
        P3 = np.array([0.0, y3])
        seg(tip, P3, cols[2])
        extender(P3, np.array([sgn, 0.0]), cols[2])
    # imagen
    if not inf:
        est = "-" if real else "--"
        ax.annotate("", xy=(xi, yi), xytext=(xi, 0),
                    arrowprops=dict(arrowstyle="-|>", color="#4de1ff", lw=3, ls=est))
        ax.text(xi, (-0.09 * H if yi > 0 else 0.05 * H), "Imagen " + ("real" if real else "virtual"),
                ha="center", color="#4de1ff")
        if not real:
            for P, col in ((P1, cols[0]), ((0.0, 0.0), cols[1])):
                seg(np.array(P, float), np.array([xi, yi]), col, "--", 1.2)
    ax.set_xlabel("posición (cm)"); ax.set_yticks([])
    ax.set_title("Trazado de rayos principales", color=AZUL)
    fig.tight_layout()
    return fig


def gif_pulso_2d(modelos, fuentes, tmax, frames=36, rango=16.0, n=256, s=0.5, fps=10):
    """Animación GIF del pulso en varios medios, lado a lado. Devuelve bytes."""
    import os, tempfile
    from matplotlib.animation import FuncAnimation, PillowWriter
    ts = np.linspace(0, tmax, frames)
    lims = []
    for m in modelos:
        _, p = pulso_2d(m, 0.6 * tmax, fuentes, rango, n, s)
        lims.append(float(np.percentile(np.abs(p), 99.5)) or 1.0)
    fig, axs = plt.subplots(1, len(modelos), figsize=(5.2 * len(modelos), 5.0))
    axs = np.atleast_1d(axs)
    ims, titulos = [], []
    for ax, m, lim in zip(axs, modelos, lims):
        x, p0 = pulso_2d(m, 0.0, fuentes, rango, n, s)
        ims.append(ax.imshow(p0, extent=[x[0], x[-1], x[0], x[-1]], origin="lower",
                             cmap=CMAP_AGUA, vmin=-lim, vmax=lim))
        titulos.append(ax.set_title("", color=AZUL, fontsize=11))
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    fig.tight_layout()
    fig.subplots_adjust(top=0.84)

    def actualizar(i):
        for im, tit, m in zip(ims, titulos, modelos):
            _, p = pulso_2d(m, ts[i], fuentes, rango, n, s)
            im.set_data(p)
            tit.set_text(f"{_titulo_corto(m)}\nt = {ts[i]:.1f} s")
        return ims

    anim = FuncAnimation(fig, actualizar, frames=frames, blit=False)
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
        ruta = f.name
    anim.save(ruta, writer=PillowWriter(fps=fps), dpi=80)
    with open(ruta, "rb") as f:
        datos = f.read()
    os.remove(ruta)
    plt.close(fig)
    return datos
