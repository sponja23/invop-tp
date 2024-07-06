from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Orden:
    id: int
    beneficio: float
    cant_trab: int


@dataclass
class InstanciaAsignacionCuadrillas:
    """Clase que representa una instancia del problema de asignación de cuadrillas"""

    """Cantidad de trabajadores disponibles (T)"""
    cantidad_trabajadores: int

    """Cantidad de órdenes a asignar (O)"""
    ordenes: List[Orden]

    """Conflictos entre trabajadores: (A,B) <=> A y B no pueden trabajar en la misma orden"""
    conflictos_trabajadores: List[Tuple[int, int]]

    """Órdenes correlativas: (A,B) <=> Después de A se debe hacer B"""
    ordenes_correlativas: List[Tuple[int, int]]

    """Órdenes conflictivas: (A,B) <=> Si un trabajador trabaja en A/B, no puede trabajar después en B/A"""
    ordenes_conflictivas: List[Tuple[int, int]]

    """Órdenes repetitivas: (A,B) <=> A y B no pueden ser asignadas al mismo trabajador"""
    ordenes_repetitivas: List[Tuple[int, int]]

    @property
    def indices_trabajadores(self) -> range:
        """Índices sobre el conjunto de trabajadores de la instancia"""
        return range(self.cantidad_trabajadores)

    @property
    def indices_ordenes(self) -> range:
        """Índices sobre el conjunto de órdenes de la instancia"""
        return range(len(self.ordenes))

    @property
    def indices_dias(self) -> range:
        """Índices sobre el conjunto de días de la instancia"""
        return range(1, 7)

    @property
    def indices_turnos(self) -> range:
        """Índices sobre el conjunto de turnos de la instancia"""
        return range(1, 6)

    def beneficio_maximo(self) -> float:
        """Calcula el beneficio máximo posible de la instancia"""
        return sum(orden.beneficio for orden in self.ordenes if orden.beneficio > 0)

    def beneficio_maximo_pagando_minimo(self) -> float:
        """Calcula el beneficio máximo posible de la instancia pagando el mínimo"""
        return sum(
            max(orden.beneficio - 1000 * orden.cant_trab, 0) for orden in self.ordenes
        )

    def cantidad_de_ordenes_posibles(self) -> int:
        """Calcula la cantidad de órdenes posibles de asignar"""
        return sum(
            1 for orden in self.ordenes if orden.cant_trab <= self.cantidad_trabajadores
        )

    @staticmethod
    def leer_texto(path: str) -> "InstanciaAsignacionCuadrillas":
        """
        Lee la instancia usando el formato de texto especificado en el enunciado.
        """

        with open(path, "r") as f:
            # Lectura cantidad de trabajadores
            cantidad_trabajadores = int(f.readline())

            # Lectura cantidad de ordenes
            cantidad_ordenes = int(f.readline())

            # Lectura de las ordenes
            ordenes = []
            for i in range(cantidad_ordenes):
                id, beneficio, cant_trab = f.readline().rstrip().split(" ")
                ordenes.append(
                    Orden(
                        id=int(id),
                        beneficio=float(beneficio),
                        cant_trab=int(cant_trab),
                    )
                )

            # Lectura cantidad de conflictos entre los trabajadores
            cantidad_conflictos_trabajadores = int(f.readline())

            # Lectura conflictos entre los trabajadores
            conflictos_trabajadores = []
            for i in range(cantidad_conflictos_trabajadores):
                j1, j2 = f.readline().split(" ")
                conflictos_trabajadores.append((int(j1), int(j2)))

            # Lectura cantidad de ordenes correlativas
            cantidad_ordenes_correlativas = int(f.readline())

            # Lectura ordenes correlativas
            ordenes_correlativas = []
            for i in range(cantidad_ordenes_correlativas):
                i1, i2 = f.readline().split(" ")
                ordenes_correlativas.append((int(i1), int(i2)))

            # Lectura cantidad de ordenes conflictivas
            cantidad_ordenes_conflictivas = int(f.readline())

            # Lectura ordenes conflictivas
            ordenes_conflictivas = []
            for i in range(cantidad_ordenes_conflictivas):
                i1, i2 = f.readline().split(" ")
                ordenes_conflictivas.append((int(i1), int(i2)))

            # Lectura cantidad de ordenes repetitivas
            cantidad_ordenes_repetitivas = int(f.readline())

            # Lectura ordenes repetitivas
            ordenes_repetitivas = []
            for i in range(cantidad_ordenes_repetitivas):
                i1, i2 = f.readline().split(" ")
                ordenes_repetitivas.append((int(i1), int(i2)))

            return InstanciaAsignacionCuadrillas(
                cantidad_trabajadores=cantidad_trabajadores,
                ordenes=ordenes,
                conflictos_trabajadores=conflictos_trabajadores,
                ordenes_correlativas=ordenes_correlativas,
                ordenes_conflictivas=ordenes_conflictivas,
                ordenes_repetitivas=ordenes_repetitivas,
            )

    def guardar_texto(self, path: str) -> None:
        """
        Guarda la instancia usando el formato de texto especificado en el enunciado.
        """

        lines = [
            # Cantidad de trabajadores
            self.cantidad_trabajadores,
            # Cantidad de órdenes
            len(self.ordenes),
            # Órdenes
            *[
                f"{orden.id} {orden.beneficio} {orden.cant_trab}"
                for orden in self.ordenes
            ],
            # Cantidad de conflictos entre los trabajadores
            len(self.conflictos_trabajadores),
            # Conflictos entre los trabajadores
            *[f"{j1} {j2}" for j1, j2 in self.conflictos_trabajadores],
            # Cantidad de órdenes correlativas
            len(self.ordenes_correlativas),
            # Órdenes correlativas
            *[f"{i1} {i2}" for i1, i2 in self.ordenes_correlativas],
            # Cantidad de órdenes conflictivas
            len(self.ordenes_conflictivas),
            # Órdenes conflictivas
            *[f"{i1} {i2}" for i1, i2 in self.ordenes_conflictivas],
            # Cantidad de órdenes repetitivas
            len(self.ordenes_repetitivas),
            # Órdenes repetitivas
            *[f"{i1} {i2}" for i1, i2 in self.ordenes_repetitivas],
        ]

        with open(path, "w") as f:
            f.write("\n".join(map(str, lines)))
