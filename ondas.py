"""Módulo de ondas: superposición de ondas circulares de fuentes puntuales en 2D."""
import numpy as np
from dispersion import k_desde_omega


def interferencia(fuentes, lam=1.0, rango=8.0, n=500, t=0.0, frecuencia=1.0):
    """Calcula la perturbación total ψ(x, y, t) sobre una malla n×n.

    fuentes: lista de (x, y, amplitud, fase_rad).
    Cada onda: A·cos(k·r − ω·t + φ) / √r. La suma de todas es el principio
    de superposición. Totalmente vectorizado con NumPy.
    """
    x = np.linspace(-rango, rango, n)
    y = np.linspace(-rango, rango, n)
    X, Y = np.meshgrid(x, y)
    k = 2 * np.pi / lam
    omega = 2 * np.pi * frecuencia
    psi = np.zeros_like(X)
    for sx, sy, amp, fase in fuentes:
        r = np.hypot(X - sx, Y - sy) + 1e-6
        psi += amp * np.cos(k * r - omega * t + fase) / np.sqrt(r)
    return x, y, psi


def longitud_de_onda(frecuencia, modelo="somera", h=5.0):
    """λ = 2π/k con ω(k) = 2π·f para el medio y la profundidad dados."""
    return 2 * np.pi / k_desde_omega(2 * np.pi * frecuencia, modelo, h)
