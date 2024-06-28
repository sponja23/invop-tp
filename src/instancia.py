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
    def indices_trabajadores(self):
        """Índices sobre el conjunto de trabajadores de la instancia"""
        return range(self.cantidad_trabajadores)

    @property
    def indices_ordenes(self):
        """Índices sobre el conjunto de órdenes de la instancia"""
        return range(len(self.ordenes))

    @property
    def indices_dias(self):
        """Índices sobre el conjunto de días de la instancia"""
        return range(1, 7)

    @property
    def indices_turnos(self):
        """Índices sobre el conjunto de turnos de la instancia"""
        return range(1, 6)
