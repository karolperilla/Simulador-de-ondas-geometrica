"""Módulo de óptica geométrica: ley de Snell, ángulo crítico y reflexión interna total."""
import numpy as np


def angulo_critico(n1: float, n2: float):
    """Ángulo crítico en grados (solo existe si n1 > n2); None en caso contrario."""
    if n1 > n2:
        return float(np.degrees(np.arcsin(n2 / n1)))
    return None


def refraccion(n1: float, n2: float, theta1_deg: float):
    """Aplica la ley de Snell: n1·sen(θ1) = n2·sen(θ2).

    Devuelve un diccionario con el ángulo refractado, la desviación angular
    y si ocurre reflexión interna total.
    """
    s = n1 / n2 * np.sin(np.radians(theta1_deg))
    if s > 1:
        return {"theta2": None, "desviacion": None, "rit": True,
                "theta_critico": angulo_critico(n1, n2)}
    theta2 = float(np.degrees(np.arcsin(s)))
    return {"theta2": theta2, "desviacion": abs(theta1_deg - theta2), "rit": False,
            "theta_critico": angulo_critico(n1, n2)}


# ------------------------------------------------- dispersión de la luz (prisma)
# Modelo de Cauchy  n(λ) = A + B/λ²  (λ en µm). Coeficientes aproximados.
CAUCHY = {
    "Vidrio crown (BK7)": (1.5046, 0.00420),
    "Sílice fundida": (1.4580, 0.00354),
    "Vidrio flint denso (SF10)": (1.7280, 0.01342),
}


def indice_cauchy(lam_nm, A, B):
    """Índice de refracción dependiente de la longitud de onda (en nm)."""
    return A + B / (np.asarray(lam_nm, dtype=float) / 1000.0) ** 2


def desviacion_minima(n, alfa_deg):
    """Desviación mínima de un prisma: δmin = 2·arcsen(n·sen(α/2)) − α."""
    a = np.radians(alfa_deg)
    return float(np.degrees(2 * np.arcsin(n * np.sin(a / 2)) - a))


def _refractar(d, N, n1, n2):
    """Ley de Snell en forma vectorial. N es la normal unitaria que mira
    hacia el lado de incidencia. Devuelve None si hay reflexión total."""
    cosi = -np.dot(N, d)
    eta = n1 / n2
    k = 1 - eta ** 2 * (1 - cosi ** 2)
    if k < 0:
        return None
    return eta * d + (eta * cosi - np.sqrt(k)) * N


def trazar_prisma(n, alfa_deg, theta_i_deg, h=1.0, s=0.5):
    """Traza un rayo monocromático (índice n) a través de un prisma isósceles.

    Vértice arriba, ángulo de apertura alfa. El rayo entra por la cara
    izquierda con ángulo de incidencia theta_i y sale por la derecha.
    Devuelve un diccionario con los puntos y la desviación total (grados);
    'sale' es False si hay reflexión interna total en la segunda cara.
    """
    a = np.radians(alfa_deg)
    w = h * np.tan(a / 2)
    A = np.array([0.0, h]); B = np.array([-w, 0.0]); C = np.array([w, 0.0])
    norma = np.hypot(h, w)
    m = np.array([h, -w]) / norma          # normal interior de la cara izquierda
    nr = np.array([h, w]) / norma          # normal exterior de la cara derecha
    th = np.radians(theta_i_deg)
    rot = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    d0 = rot @ m                           # dirección del rayo incidente
    P1 = A + s * (B - A)
    d1 = _refractar(d0, -m, 1.0, n)
    u, t = np.linalg.solve(np.column_stack([C - A, -d1]), P1 - A)
    P2 = P1 + t * d1
    d2 = _refractar(d1, -nr, n, 1.0) if 0 <= u <= 1 else None
    res = {"A": A, "B": B, "C": C, "d0": d0, "P1": P1, "P2": P2, "d2": d2,
           "sale": d2 is not None, "desviacion": None}
    if d2 is not None:
        res["desviacion"] = float(np.degrees(np.arccos(np.clip(np.dot(d0, d2), -1, 1))))
    return res


# ------------------------------------------------- lentes delgadas y espejos
def formacion_imagen(tipo, f, do, h):
    """Ecuación de lentes/espejos: 1/f = 1/do + 1/di.

    tipo: 'lente' o 'espejo'. f > 0 lente convergente / espejo cóncavo,
    f < 0 divergente / convexo, f = inf espejo plano.
    Devuelve di, aumento m, posición x de la imagen (lente en x=0, objeto en
    x=−do; imagen real a la derecha en lentes y a la izquierda en espejos).
    """
    inv = 0.0 if np.isinf(f) else 1.0 / f
    d = inv - 1.0 / do
    if abs(d) < 1e-9:
        return {"infinito": True, "real": False, "di": np.inf, "m": np.inf,
                "x_img": np.nan, "h_img": np.nan, "derecha": False}
    di = 1.0 / d
    m = -di / do
    return {"infinito": False, "di": di, "m": m, "h_img": m * h,
            "x_img": di if tipo == "lente" else -di,
            "real": di > 0, "derecha": m > 0}


# ------------------------------------------- prisma con giro libre de 360°
# Convención (idéntica a la del componente JS interactivo):
#   · Haz láser horizontal que viaja hacia +x a la altura y0 (coordenadas del laboratorio).
#   · Prisma isósceles con el vértice arriba y su centroide en el origen; φ = giro
#     antihorario del prisma (grados). Para φ = α/2 − θ₁ el haz incide sobre la cara
#     izquierda con ángulo θ₁ (misma definición que usa el deslizador de incidencia).
LAMBDAS_PRISMA = np.arange(400, 701, 25)
COLORES_REF = (("Rojo", 700), ("Naranja", 620), ("Amarillo", 580),
               ("Verde", 530), ("Azul", 470), ("Violeta", 400))


def phi_desde_theta(alfa_deg, theta_deg):
    """Giro φ (0–360°) del prisma que produce incidencia θ₁ en la cara izquierda."""
    return float((alfa_deg / 2.0 - theta_deg) % 360.0)


def theta_desde_phi(alfa_deg, phi_deg):
    """Incidencia θ₁ (−180°, 180°] sobre la cara izquierda para un giro φ."""
    t = (alfa_deg / 2.0 - phi_deg + 180.0) % 360.0 - 180.0
    return float(180.0 if t == -180.0 else t)


def _triangulo(alfa_deg, phi_deg, h=1.0):
    a = np.radians(alfa_deg)
    w = h * np.tan(a / 2)
    V = np.array([[0.0, 2 * h / 3], [-w, -h / 3], [w, -h / 3]])
    p = np.radians(phi_deg)
    R = np.array([[np.cos(p), -np.sin(p)], [np.sin(p), np.cos(p)]])
    return V @ R.T


def _normal_exterior(V, i):
    e = V[(i + 1) % 3] - V[i]
    N = np.array([e[1], -e[0]]) / np.hypot(*e)
    return N if np.dot(N, 0.5 * (V[i] + V[(i + 1) % 3])) > 0 else -N


def _golpe(p, d, V):
    """Primera intersección (t>0) del rayo p+t·d con el contorno del prisma."""
    mejor = None
    for i in range(3):
        a = V[i]; e = V[(i + 1) % 3] - a
        den = d[0] * e[1] - d[1] * e[0]
        if abs(den) < 1e-12:
            continue
        ap = a - p
        t = (ap[0] * e[1] - ap[1] * e[0]) / den
        u = (ap[0] * d[1] - ap[1] * d[0]) / den
        if t > 1e-9 and -1e-9 <= u <= 1 + 1e-9 and (mejor is None or t < mejor[0]):
            mejor = (t, i, p + t * d)
    return mejor


def trazar_prisma_rot(n, alfa_deg, phi_deg, y0=0.15, max_rebotes=8):
    """Traza el rayo principal (sin reflexiones parciales) a través del prisma girado.

    Devuelve dict: golpea, sale, theta_inc (incidencia real en la 1.ª cara, °),
    desviacion (°, valor absoluto respecto al haz incidente) y rebotes internos.
    """
    V = _triangulo(alfa_deg, phi_deg)
    d0 = np.array([1.0, 0.0])
    g = _golpe(np.array([-6.0, y0]), d0, V)
    vacio = {"golpea": False, "sale": False, "theta_inc": None, "desviacion": None, "rebotes": 0}
    if g is None:
        return vacio
    _, i, P = g
    No = _normal_exterior(V, i)
    theta_inc = float(np.degrees(np.arccos(np.clip(-np.dot(d0, No), -1, 1))))
    d = _refractar(d0, No, 1.0, n)
    rebotes = 0
    for _ in range(max_rebotes):
        g = _golpe(P, d, V)
        if g is None:
            break
        _, j, P = g
        Nj = _normal_exterior(V, j)
        d2 = _refractar(d, -Nj, n, 1.0)
        if d2 is None:                      # reflexión interna total: rebota
            d = d - 2 * np.dot(d, Nj) * Nj
            rebotes += 1
            continue
        ang = np.degrees(np.arctan2(d2[1], d2[0]))
        ang = (ang + 180.0) % 360.0 - 180.0
        return {"golpea": True, "sale": True, "theta_inc": theta_inc,
                "desviacion": float(abs(ang)), "rebotes": rebotes}
    return {"golpea": True, "sale": False, "theta_inc": theta_inc, "desviacion": None, "rebotes": rebotes}


def reflectancia(n1, n2, theta1_deg):
    """Reflectancia de Fresnel para luz no polarizada (fracción de energía reflejada)."""
    s = n1 / n2 * np.sin(np.radians(theta1_deg))
    if s >= 1:
        return 1.0
    ci = np.cos(np.radians(theta1_deg)); ct = np.sqrt(1 - s ** 2)
    rs = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)
    rp = (n2 * ci - n1 * ct) / (n2 * ci + n1 * ct)
    return float((rs ** 2 + rp ** 2) / 2)
