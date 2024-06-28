from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Literal

from ..instancia import InstanciaAsignacionCuadrillas


@dataclass
class Variable:
    nombre: str
    cota_inferior: float
    cota_superior: float
    tipo: Literal["C", "I", "B"]

    def __post_init__(self):
        self.costo = float(self.costo)
        self.cota_inferior = float(self.cota_inferior)
        self.cota_superior = float(self.cota_superior)


def variables_asignacion_orden_trabajador_dia_turno(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    `a_{i}_{j}_{k}_{l}` = 1 sii el trabajador j trabaja en la orden i el día k en el turno l
    """
    return [
        Variable(
            nombre=f"a_{i}_{j}_{k}_{l}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for i in instancia.indices_ordenes
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def variables_realizacion_orden_dia_turno(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    `r_{i}_{k}_{l}` = 1 sii la orden i se realiza el día k en el turno l
    """
    return [
        Variable(
            nombre=f"r_{i}_{k}_{l}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for i in instancia.indices_ordenes
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def variables_trabajo_trabajador_dia(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    `d_{j}_{k}` = 1 sii el trabajador j trabaja el día k
    """
    return [
        Variable(
            nombre=f"d_{j}_{k}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
    ]


def variables_remuneracion_trabajador(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    Las variables relacionadas a la remuneración de los trabajadores:
    - `o1_{j}`: la cantidad de órdenes realizadas en el rango [0, 5].
    - `o2_{j}`: la cantidad de órdenes realizadas en el rango [6, 10].
    - `o3_{j}`: la cantidad de órdenes realizadas en el rango [11, 15].
    - `o4_{j}`: la cantidad de órdenes realizadas después de 15.
    - `w1_{j}` = 1 sii el trabajador j realiza al menos 5 órdenes.
    - `w2_{j}` = 1 sii el trabajador j realiza al menos 10 órdenes.
    - `w3_{j}` = 1 sii el trabajador j realiza al menos 15 órdenes.
    """
    return chain.from_itertools(
        [
            (
                Variable(
                    nombre=f"o1_{j}",
                    cota_inferior=0,
                    cota_superior=min(5, len(instancia.indices_ordenes)),
                    tipo="I",
                ),
                Variable(
                    nombre=f"o2_{j}",
                    cota_inferior=0,
                    cota_superior=min(5, max(len(instancia.indices_ordenes) - 5), 0),
                    tipo="I",
                ),
                Variable(
                    nombre=f"o3_{j}",
                    cota_inferior=0,
                    cota_superior=min(5, max(len(instancia.indices_ordenes) - 10), 0),
                    tipo="I",
                ),
                Variable(
                    nombre=f"o4_{j}",
                    cota_inferior=0,
                    cota_superior=max(len(instancia.indices_ordenes) - 15, 0),
                    tipo="I",
                ),
                Variable(
                    nombre=f"w1_{j}",
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                ),
                Variable(
                    nombre=f"w2_{j}",
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                ),
                Variable(
                    nombre=f"w3_{j}",
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                ),
            )
            for j in instancia.indices_trabajadores
        ]
    )
