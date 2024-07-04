from abc import ABC, abstractmethod
from math import sqrt
import random
from typing import Generic, Tuple, TypeVar

from .univariada import Distribucion

Matriz2D = Tuple[Tuple[float, float], Tuple[float, float]]


def cholesky_2d(matriz: Matriz2D) -> Matriz2D:
    """Descomposición de Cholesky para matrices SDP 2x2"""
    (a, b), (b_, c) = matriz
    assert a > 0 and c > 0 and a * c > b**2 and b == b_

    sqrt_a = sqrt(a)

    return (
        (sqrt_a, 0.0),
        (b / sqrt_a, sqrt(a * c - b**2) / sqrt_a),
    )


N = TypeVar("N", int, float)


class DistribucionBivariada(ABC, Generic[N]):
    """Distribución bivariada"""

    @abstractmethod
    def muestrear(self) -> Tuple[N, N]:
        """Muestrea un par de números"""


class DistribucionIndependiente(DistribucionBivariada[N]):
    """Distribución bivariada independiente"""

    def __init__(self, dist1: Distribucion[N], dist2: Distribucion[N]):
        self.dist1: Distribucion[N] = dist1
        self.dist2: Distribucion[N] = dist2

    def muestrear(self) -> Tuple[N, N]:
        return self.dist1.muestrear(), self.dist2.muestrear()


class DistribucionNormalBivariada(DistribucionBivariada[float]):
    """Distribución normal bivariada"""

    def __init__(self, media: Tuple[float, float], matriz_cov: Matriz2D):
        self.media = media
        self.cholesky_decomp = cholesky_2d(matriz_cov)

    def muestrear(self) -> Tuple[float, float]:
        z1, z2 = random.gauss(0, 1), random.gauss(0, 1)
        x, y = self.media
        (a, _), (b, c) = self.cholesky_decomp

        # Demostración: https://math.stackexchange.com/a/1344953
        return (
            x + a * z1,
            y + b * z1 + c * z2,
        )
