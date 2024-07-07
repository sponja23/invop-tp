from itertools import product
import random
from dataclasses import dataclass
from typing import List, Tuple, Union

from ..instancia import InstanciaAsignacionCuadrillas, Orden
from .distribuciones.multivariada import DistribucionBivariada
from .distribuciones.univariada import Distribucion, DistribucionConstante


def generar_pares_ordenados(n: int, cantidad: int) -> List[Tuple[int, int]]:
    """
    Genera `cantidad` pares ordenados de números entre 0 y `n`
    """
    cantidad = min(cantidad, n * (n - 1))

    todos = [(i, j) for i, j in product(range(n), repeat=2) if i != j]

    return random.sample(todos, cantidad)


def generar_pares_no_ordenados(n: int, cantidad: int) -> List[Tuple[int, int]]:
    """
    Genera `cantidad` pares no ordenados de números entre 0 y `n`
    """
    cantidad = min(cantidad, n * (n - 1) // 2)

    todos = [(i, j) for i in range(n) for j in range(i + 1, n)]

    return random.sample(todos, cantidad)


@dataclass
class GeneradorInstancias:
    """
    Generador de instancias del problema de asignación de cuadrillas
    """

    cantidad_trabajadores: Distribucion[int]
    cantidad_ordenes: Distribucion[int]
    parametros_ordenes: Union[
        DistribucionBivariada[float, float],
        DistribucionBivariada[float, int],
    ]

    cantidad_conflictos_trabajadores: Distribucion[int] = DistribucionConstante(0)
    cantidad_ordenes_correlativas: Distribucion[int] = DistribucionConstante(0)
    cantidad_ordenes_conflictivas: Distribucion[int] = DistribucionConstante(0)
    cantidad_ordenes_repetitivas: Distribucion[int] = DistribucionConstante(0)

    def generar_instancia(self) -> InstanciaAsignacionCuadrillas:
        """
        Genera una instancia del problema de asignación de cuadrillas
        """

        cantidad_trabajadores = max(1, self.cantidad_trabajadores.muestrear())
        cantidad_ordenes = max(1, self.cantidad_ordenes.muestrear())

        ordenes = []
        for i in range(cantidad_ordenes):
            beneficio, cant_trab = self.parametros_ordenes.muestrear()

            ordenes.append(
                Orden(id=i, beneficio=beneficio, cant_trab=max(1, round(cant_trab)))
            )

        conflictos_trabajadores = generar_pares_no_ordenados(
            cantidad_trabajadores,
            max(0, self.cantidad_conflictos_trabajadores.muestrear()),
        )

        ordenes_correlativas = generar_pares_ordenados(
            cantidad_ordenes,
            max(0, self.cantidad_ordenes_correlativas.muestrear()),
        )

        ordenes_conflictivas = generar_pares_no_ordenados(
            cantidad_ordenes,
            max(0, self.cantidad_ordenes_conflictivas.muestrear()),
        )

        ordenes_repetitivas = generar_pares_no_ordenados(
            cantidad_ordenes,
            max(0, self.cantidad_ordenes_repetitivas.muestrear()),
        )

        return InstanciaAsignacionCuadrillas(
            cantidad_trabajadores=cantidad_trabajadores,
            ordenes=ordenes,
            # Evitamos repetidos: esto cambia un poco la distribución de la cantidad de conflictos
            # pero no debería ser un problema
            conflictos_trabajadores=list(set(conflictos_trabajadores)),
            ordenes_correlativas=list(set(ordenes_correlativas)),
            ordenes_conflictivas=list(set(ordenes_conflictivas)),
            ordenes_repetitivas=list(set(ordenes_repetitivas)),
        )
