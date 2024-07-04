from collections.abc import Iterable
from typing import Tuple

from ..instancia import InstanciaAsignacionCuadrillas


TerminosObjetivo = Iterable[Tuple[float, str]]


def objetivo_beneficio_ordenes(
    instancia: InstanciaAsignacionCuadrillas,
) -> TerminosObjetivo:
    """
    Se busca maximizar la ganancia total, compuesta por el beneficio de cada orden asignada.
    """
    return [
        (orden.beneficio, f"r_{i}_{k}_{l}")
        for i, orden in enumerate(instancia.ordenes)
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def objetivo_costo_trabajadores(
    instancia: InstanciaAsignacionCuadrillas,
) -> TerminosObjetivo:
    """
    Se busca minimizar el costo total, compuesto por el costo de las asignaciones a los trabajadores.
    """
    return [
        termino
        for j in instancia.indices_trabajadores
        for termino in [
            (-1000, f"o1_{j}"),
            (-1200, f"o2_{j}"),
            (-1400, f"o3_{j}"),
            (-1500, f"o4_{j}"),
        ]
    ]
