"""Módulo de dispersión de ondas.

Una onda es *dispersiva* cuando su frecuencia no es proporcional al número de onda:
ω = ω(k). Entonces cada componente viaja con su propia velocidad de fase
v_f = ω/k y el paquete completo avanza con la velocidad de grupo v_g = dω/dk.
Consecuencia visible: los pulsos se ensanchan y las ondas se "ordenan" por
longitud de onda.

El cálculo es espectral (suma de Fourier), por lo que es exacto para ondas
lineales y está totalmente vectorizado con NumPy.
"""
import numpy as np

G = 9.81      # gravedad (m/s²)
C = 1.5       # velocidad de la onda no dispersiva (m/s)
W0 = 2.0      # frecuencia de corte del medio con corte (rad/s)
BETA = 0.5    # rigidez de las ondas de flexión (m²/s)

MODELOS = {
    "sin": "Sin dispersión:  ω = c·k",
    "agua": "Agua profunda: ω = √(g·k)",
    "somera": "Agua de profundidad finita: ω = √(g·k·tanh(k·h))",
    "corte": "Medio con frecuencia de corte:  ω = √(c²k² + ω₀²)",
    "flexion": "Ondas de flexión (viga):  ω = β·k²",
}


def omega(k, modelo, h=None):
    """Relación de dispersión ω(k). h = profundidad (m) solo para 'somera'."""
    k = np.abs(k)
    if modelo == "sin":
        return C * k
    if modelo == "agua":
        return np.sqrt(G * k)
    if modelo == "somera":
        return np.sqrt(G * k * np.tanh(k * (h if h else 5.0)))
    if modelo == "corte":
        return np.sqrt((C * k) ** 2 + W0 ** 2)
    if modelo == "flexion":
        return BETA * k ** 2
    raise ValueError(f"Modelo desconocido: {modelo}")


def vel_fase(k, modelo, h=None):
    """Velocidad de fase v_f = ω/k."""
    return omega(k, modelo, h) / np.abs(k)


def vel_grupo(k, modelo, h=None, dk=1e-5):
    """Velocidad de grupo v_g = dω/dk (derivada centrada)."""
    return (omega(k + dk, modelo, h) - omega(k - dk, modelo, h)) / (2 * dk)


def curvatura(k, modelo, h=None, dk=1e-3):
    """ω''(k): mide cuánto se ensancha un paquete (0 = no se ensancha)."""
    return (omega(k + dk, modelo, h) - 2 * omega(k, modelo, h) + omega(k - dk, modelo, h)) / dk ** 2


def k_desde_omega(w, modelo, h=None):
    """Número de onda k tal que ω(k) = w (inversión numérica; ω es creciente)."""
    ks = np.linspace(1e-3, 80.0, 8000)
    return float(np.interp(w, omega(ks, modelo, h), ks))


# ---------------------------------------------------------------- paquete 1D
def ancho_analitico(modelo, k0, sigma_k, t):
    """Ancho teórico del paquete gaussiano: σx(t) = σx0·√(1 + (ω''σk² t)²)."""
    sx0 = 1.0 / (sigma_k * np.sqrt(2))
    return sx0 * np.sqrt(1 + (curvatura(k0, modelo) * sigma_k ** 2 * t) ** 2)


def rejilla_x(modelo, k0, sigma_k, tmax, n=1500):
    """Eje x que contiene al paquete durante todo el intervalo [0, tmax]."""
    sx0 = 1.0 / (sigma_k * np.sqrt(2))
    xmin = -7 * sx0
    xmax = vel_grupo(k0, modelo) * tmax + 7 * ancho_analitico(modelo, k0, sigma_k, tmax)
    return np.linspace(xmin, xmax, n)


def paquete_1d(modelo, k0, sigma_k, x, t, nk=600):
    """ψ(x,t) = ∫ A(k)·exp[i(kx − ω(k)t)] dk, con A gaussiana centrada en k0.

    Se normaliza para que |ψ(0,0)| = 1. Devuelve el campo complejo
    (su parte real es la onda; su módulo es la envolvente).
    """
    k = np.linspace(max(k0 - 6 * sigma_k, 1e-6), k0 + 6 * sigma_k, nk)
    dk = k[1] - k[0]
    amp = np.exp(-((k - k0) ** 2) / (2 * sigma_k ** 2))
    fase = np.outer(x, k) - omega(k, modelo)[None, :] * t
    psi = (amp[None, :] * np.exp(1j * fase)).sum(axis=1) * dk
    return psi / (sigma_k * np.sqrt(2 * np.pi))


def ancho_numerico(x, psi):
    """Desviación estándar de la intensidad |ψ|² (medida real del ancho)."""
    w = np.abs(psi) ** 2
    w = w / w.sum()
    m = (x * w).sum()
    return float(np.sqrt(((x - m) ** 2 * w).sum()))


def curva_ancho(modelo, k0, sigma_k, x, ts):
    """Ancho numérico σx(t) para una lista de tiempos."""
    return np.array([ancho_numerico(x, paquete_1d(modelo, k0, sigma_k, x, t)) for t in ts])


# ------------------------------------------------------------------ pulso 2D
def pulso_2d(modelo, t, fuentes, rango=16.0, n=384, s=0.5, h=None,
             frecuencia=None, nu=0.0, max_gotas=8):
    """Evolución de gotas gaussianas 2D sobre un medio dispersivo.

    fuentes: lista de (x, y, amplitud). Cada componente de Fourier evoluciona
    como cos(ω(|k|)·(t − tⱼ))·exp(−ν k² (t − tⱼ)) (solución lineal exacta con
    amortiguamiento viscoso ν). Si 'frecuencia' (Hz) no es None, cada fuente
    gotea periódicamente (tⱼ = j/frecuencia, hasta max_gotas) y se superponen.
    Devuelve (x, ψ) con ψ de forma (n, n).
    """
    x = np.linspace(-rango, rango, n, endpoint=False)
    X, Y = np.meshgrid(x, x)
    psi0 = np.zeros_like(X)
    for sx, sy, amp in fuentes:
        psi0 += amp * np.exp(-((X - sx) ** 2 + (Y - sy) ** 2) / (2 * s ** 2))
    kx = 2 * np.pi * np.fft.fftfreq(n, d=x[1] - x[0])
    K = np.hypot(*np.meshgrid(kx, kx))
    w = omega(K, modelo, h)
    if frecuencia:
        j = np.arange(0, int(t * frecuencia + 1e-9) + 1)[-max_gotas:]
        tj = j / frecuencia
    else:
        tj = np.array([0.0])
    fac = np.zeros_like(K)
    for ti in tj:
        dt = t - ti
        fac += np.cos(w * dt) * np.exp(-nu * K ** 2 * dt)
    return x, np.real(np.fft.ifft2(np.fft.fft2(psi0) * fac))
