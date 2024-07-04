import random
from dataclasses import dataclass

from ..instancia import InstanciaAsignacionCuadrillas, Orden
from .distribuciones.multivariada import DistribucionBivariada
from .distribuciones.univariada import Distribucion


@dataclass
class GeneradorInstancias:
    """
    Generador de instancias del problema de asignación de cuadrillas
    """

    cantidad_trabajadores: Distribucion[int]
    cantidad_ordenes: Distribucion[int]
    parametros_ordenes: DistribucionBivariada[float]

    cantidad_conflictos_trabajadores: Distribucion[int]
    cantidad_ordenes_correlativas: Distribucion[int]
    cantidad_ordenes_conflictivas: Distribucion[int]
    cantidad_ordenes_repetitivas: Distribucion[int]

    def generar_instancia(self) -> InstanciaAsignacionCuadrillas:
        """
        Genera una instancia del problema de asignación de cuadrillas
        """

        cantidad_trabajadores = min(1, self.cantidad_trabajadores.muestrear())
        cantidad_ordenes = min(1, self.cantidad_ordenes.muestrear())

        ordenes = []
        for i in range(cantidad_ordenes):
            beneficio, cant_trab = self.parametros_ordenes.muestrear()

            cant_trab = min(1, cant_trab)

            ordenes.append(Orden(id=i, beneficio=beneficio, cant_trab=round(cant_trab)))

        conflictos_trabajadores = [
            (
                random.randint(0, cantidad_trabajadores - 1),
                random.randint(0, cantidad_trabajadores - 1),
            )
            for _ in range(min(0, self.cantidad_conflictos_trabajadores.muestrear()))
        ]

        ordenes_correlativas = [
            (
                random.randint(0, cantidad_ordenes - 1),
                random.randint(0, cantidad_ordenes - 1),
            )
            for _ in range(min(0, self.cantidad_ordenes_correlativas.muestrear()))
        ]

        ordenes_conflictivas = [
            (
                random.randint(0, cantidad_ordenes - 1),
                random.randint(0, cantidad_ordenes - 1),
            )
            for _ in range(min(0, self.cantidad_ordenes_conflictivas.muestrear()))
        ]

        ordenes_repetitivas = [
            (
                random.randint(0, cantidad_ordenes - 1),
                random.randint(0, cantidad_ordenes - 1),
            )
            for _ in range(min(0, self.cantidad_ordenes_repetitivas.muestrear()))
        ]

        return InstanciaAsignacionCuadrillas(
            cantidad_trabajadores=cantidad_trabajadores,
            ordenes=ordenes,
            conflictos_trabajadores=conflictos_trabajadores,
            ordenes_correlativas=ordenes_correlativas,
            ordenes_conflictivas=ordenes_conflictivas,
            ordenes_repetitivas=ordenes_repetitivas,
        )
