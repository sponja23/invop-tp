from collections.abc import Iterable
from itertools import chain
from typing import Tuple

from ..instancia import InstanciaAsignacionCuadrillas


TerminosObjetivo = Iterable[Tuple[float, str]]


def objetivo_asignacion_cuadrillas(
    instancia: InstanciaAsignacionCuadrillas,
) -> TerminosObjetivo:
    """
    Se busca maximizar la ganancia total, compuesta por el beneficio de cada orden asignada
    y el costo de las asignaciones a los trabajadores.
    """
    return [
        (orden.beneficio, f"r_{i}_{k}_{l}")
        for i, orden in enumerate(instancia.ordenes)
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ] + list(
        chain.from_iterable(
            (
                (-1000, f"o1_{j}"),
                (-1200, f"o2_{j}"),
                (-1400, f"o3_{j}"),
                (-1500, f"o4_{j}"),
            )
            for j in instancia.indices_trabajadores
        )
    )
