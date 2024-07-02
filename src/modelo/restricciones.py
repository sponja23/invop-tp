from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import chain, pairwise, product
from typing import List, Literal, Tuple

from ..instancia import InstanciaAsignacionCuadrillas


@dataclass
class Restriccion:
    terminos_izq: List[Tuple[float, str]]
    sentido: Literal["L", "G", "E"]
    terminos_der: List[Tuple[float, str]] = field(default_factory=list)
    term_independiente: float = 0
    nombre: str = ""

    def __post_init__(self) -> None:
        # Aseguramos que todos los coeficientes sean floats
        self.terminos_izq = [(float(coef), var) for coef, var in self.terminos_izq]
        self.term_independiente = float(self.term_independiente)
        self.terminos_der = [(float(coef), var) for coef, var in self.terminos_der]


def restricciones_trabajo_simultaneo(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Para cada turno de cada día, un trabajador no puede trabajar en más de una orden.
    """
    return [
        Restriccion(
            terminos_izq=[(1, f"a_{i}_{j}_{k}_{l}") for i in instancia.indices_ordenes],
            sentido="L",
            term_independiente=1,
        )
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def restricciones_limite_diario(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Un trabajador no puede trabajar los 5 turnos del día
    """
    return [
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for i in instancia.indices_ordenes
                for l in instancia.indices_turnos
            ],
            sentido="L",
            term_independiente=4,
        )
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
    ]


def restricciones_definicion_d_jk(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la variable d_jk, que indica si el trabajador j trabaja el día k
    """
    return [
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for i in instancia.indices_ordenes
                for l in instancia.indices_turnos
            ],
            sentido="G",
            terminos_der=[(1, f"d_{j}_{k}")],
        )
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
    ] + [
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for i in instancia.indices_ordenes
                for l in instancia.indices_turnos
            ],
            sentido="L",
            terminos_der=[(5, f"d_{j}_{k}")],
        )
        for j in instancia.indices_trabajadores
        for k in instancia.indices_dias
    ]


def restricciones_limite_semanal(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Un trabajador no puede trabajar los 6 días de la semana
    """

    restriccion_semanal = [
        Restriccion(
            terminos_izq=[(1, f"d_{j}_{k}") for k in instancia.indices_dias],
            sentido="L",
            term_independiente=5,
        )
        for j in instancia.indices_trabajadores
    ]

    return restriccion_semanal


def restricciones_definicion_r_ikl(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la variable r_ikl, que indica si la orden i se realiza el día k en el turno l
    """
    return [
        Restriccion(
            terminos_izq=[(instancia.ordenes[i].cant_trab, f"r_{i}_{k}_{l}")],
            sentido="E",
            terminos_der=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for j in instancia.indices_trabajadores  # noqa: E741
            ],
        )
        for i in instancia.indices_ordenes
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def restricciones_repeticion_de_ordenes(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Cada orden puede ser realizada a lo sumo 1 vez
    """
    return [
        Restriccion(
            terminos_izq=[
                (1, f"r_{i}_{k}_{l}")
                for k in instancia.indices_dias
                for l in instancia.indices_turnos
            ],
            sentido="L",
            term_independiente=1,
        )
        for i in instancia.indices_ordenes
    ]


def restricciones_ordenes_conflictivas(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Para cada par de órdenes conflictivas, si un trabajador trabaja en una, no puede trabajar en la otra
    en el próximo turno
    """
    return chain.from_iterable(
        [
            (
                Restriccion(
                    terminos_izq=[
                        (1, f"a_{i1}_{j}_{k}_{l}"),
                        (1, f"a_{i2}_{j}_{k}_{next_l}"),
                    ],
                    sentido="L",
                    term_independiente=1,
                ),
                Restriccion(
                    terminos_izq=[
                        (1, f"a_{i2}_{j}_{k}_{l}"),
                        (1, f"a_{i1}_{j}_{k}_{next_l}"),
                    ],
                    sentido="L",
                    term_independiente=1,
                ),
            )
            for (l, next_l) in pairwise(instancia.indices_turnos)
            for k in instancia.indices_dias
            for j in instancia.indices_trabajadores
            for (i1, i2) in instancia.ordenes_conflictivas
        ]
    )


def restricciones_ordenes_correlativas(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Para cada par de órdenes correlativas, la segunda orden debe realizarse después de la primera
    """
    return [
        Restriccion(
            terminos_izq=[(1, f"r_{i1}_{k}_{l}")],
            sentido="L",
            terminos_der=[(1, f"r_{i2}_{k}_{next_l}")],
        )
        for (l, next_l) in pairwise(instancia.indices_turnos)
        for (i1, i2) in instancia.ordenes_correlativas
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    ]


def restricciones_linearizacion_remuneracion(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen las variables que linearizan la remuneración de los trabajadores
    """
    return chain.from_iterable(
        (
            # w^1_j sólo puede ser 1 si o^1_j es 5
            Restriccion(
                terminos_izq=[(5, f"w1_{j}")],
                sentido="L",
                terminos_der=[(1, f"o1_{j}")],
            ),
            # w^2_j sólo puede ser 1 si o^2_j es 5
            Restriccion(
                terminos_izq=[(5, f"w2_{j}")],
                sentido="L",
                terminos_der=[(1, f"o2_{j}")],
            ),
            # o^2_j sólo puede ser positiva si w^1_j es 1
            Restriccion(
                terminos_izq=[(1, f"o2_{j}")],
                sentido="L",
                terminos_der=[(5, f"w1_{j}")],
            ),
            # w^3_j sólo puede ser 1 si o^3_j es 5
            Restriccion(
                terminos_izq=[(5, f"w3_{j}")],
                sentido="L",
                terminos_der=[(1, f"o3_{j}")],
            ),
            # o^3_j sólo puede ser positiva si w^2_j es 1
            Restriccion(
                terminos_izq=[(1, f"o3_{j}")],
                sentido="L",
                terminos_der=[(5, f"w2_{j}")],
            ),
            # o^4_j sólo puede ser positiva si w^3_j es 1
            Restriccion(
                terminos_izq=[(1, f"o4_{j}")],
                sentido="L",
                terminos_der=[(max(len(instancia.indices_ordenes) - 15, 0), f"w3_{j}")],
            ),
        )
        for j in instancia.indices_trabajadores
    )


def restricciones_definicion_remuneracion(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la remuneración de los trabajadores
    """
    return [
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for i in instancia.indices_ordenes
                for k in instancia.indices_dias
                for l in instancia.indices_turnos
            ],
            sentido="E",
            terminos_der=[
                (1, f"o1_{j}"),
                (1, f"o2_{j}"),
                (1, f"o3_{j}"),
                (1, f"o4_{j}"),
            ],
        )
        for j in instancia.indices_trabajadores
    ]


def restricciones_diferencia_maxima_turnos(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    return [
        Restriccion(
            terminos_izq=[
                (1, f"o1_{j1}"),
                (1, f"o2_{j1}"),
                (1, f"o3_{j1}"),
                (1, f"o4_{j1}"),
                (-1, f"o1_{j2}"),
                (-1, f"o2_{j2}"),
                (-1, f"o3_{j2}"),
                (-1, f"o4_{j2}"),
            ],
            sentido="L",
            term_independiente=8,
        )
        for j1, j2 in product(instancia.indices_trabajadores, repeat=2)
        if j1 != j2
    ]
