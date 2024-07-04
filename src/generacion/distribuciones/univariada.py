import random
from abc import ABC, abstractmethod
from typing import Generic, TypeVar


N = TypeVar("N", int, float)


class Distribucion(ABC, Generic[N]):
    """La distribución de un número"""

    @abstractmethod
    def muestrear(self) -> N:
        """Muestrea un número entero"""


class DistribucionConstante(Distribucion[N]):
    """Distribución constante"""

    def __init__(self, valor: N):
        self.valor: N = valor

    def muestrear(self) -> N:
        return self.valor


class DistribucionUniforme(Distribucion[N]):
    """Distribución uniforme"""

    def __init__(self, minimo: N, maximo: N):
        self.minimo: N = minimo
        self.maximo: N = maximo

    def muestrear(self) -> N:
        if isinstance(self.minimo, float):
            return random.uniform(self.minimo, self.maximo)  # type: ignore
        else:
            return random.randint(self.minimo, self.maximo)


class DistribucionNormal(Distribucion[float]):
    """Distribución normal"""

    def __init__(self, media: float, desvio: float):
        self.media = media
        self.desvio = desvio

    def muestrear(self) -> float:
        return random.gauss(self.media, self.desvio)
