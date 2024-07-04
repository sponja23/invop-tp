from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING

from .objetivo import TerminosObjetivo

from .variables import Variable

from .restricciones import Restriccion

from ..instancia import InstanciaAsignacionCuadrillas


if TYPE_CHECKING:
    from .modelo import ModeloAsignacionCuadrillas


def restricciones_evitar_conflictos(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que evitan que dos trabajadores estén en el mismo lugar al mismo tiempo
    """
    return (
        Restriccion(
            terminos_izq=[(1, f"a_{i}_{j1}_{k}_{l}"), (1, f"a_{i}_{j2}_{k}_{l}")],
            sentido="L",
            term_independiente=1,
        )
        for j1, j2 in instancia.conflictos_trabajadores
        for i in instancia.indices_ordenes
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    )


def variables_c_j1j2_i(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    Variables que indican si los trabajadores j1 y j2 están en conflicto en el orden i
    """
    return (
        Variable(
            nombre=f"c^{j1}_{j2}_{i}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for j1, j2 in instancia.conflictos_trabajadores
        for i in instancia.indices_ordenes
    )


def restricciones_definicion_c_j1j2_i(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la variable c_{j1}_{j2}_{i}, que indica si los trabajadores j1 y j2 están en conflicto en el orden i
    """
    return (
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j1}_{k}_{l}"),
                (1, f"a_{i}_{j2}_{k}_{l}"),
                (-1, f"c^{j1}_{j2}_{i}"),
            ],
            sentido="L",
            term_independiente=1,
        )
        for j1, j2 in instancia.conflictos_trabajadores
        for i in instancia.indices_ordenes
        for k in instancia.indices_dias
        for l in instancia.indices_turnos
    )


def objetivo_multa_conflictos(
    instancia: InstanciaAsignacionCuadrillas,
    penalizacion: float,
) -> TerminosObjetivo:
    """
    Objetivo que penaliza la presencia de conflictos entre trabajadores
    """
    return (
        (-penalizacion, f"c^{j1}_{j2}_{i}")
        for j1, j2 in instancia.conflictos_trabajadores
        for i in instancia.indices_ordenes
    )


def variables_t_ij(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    Variables que indican si el trabajador j realiza el orden i
    """
    return (
        Variable(
            nombre=f"t_{i}_{j}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for i in instancia.indices_ordenes
        for j in instancia.indices_trabajadores
    )


def restricciones_definicion_t_ij(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la variable t_{i}_{j}, que indica si el trabajador j realiza el orden i
    """
    return (
        Restriccion(
            terminos_izq=[
                (1, f"a_{i}_{j}_{k}_{l}")
                for k in instancia.indices_dias
                for l in instancia.indices_turnos
            ],
            sentido="E",
            terminos_der=[(1, f"t_{i}_{j}")],
        )
        for i in instancia.indices_ordenes
        for j in instancia.indices_trabajadores
    )


def restricciones_evitar_repeticiones(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que evitan que un trabajador realice dos órdenes consecutivas
    """
    return (
        Restriccion(
            terminos_izq=[(1, f"t_{i1}_{j}"), (1, f"t_{i2}_{j}")],
            sentido="L",
            term_independiente=1,
        )
        for i1, i2 in instancia.ordenes_repetitivas
        for j in instancia.indices_trabajadores
    )


def variables_re_i1i2_j(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Variable]:
    """
    Variables que indican si el trabajador j realiza los órdenes i e i+1
    """
    return (
        Variable(
            nombre=f"re_{i1}_{i2}_{j}",
            cota_inferior=0,
            cota_superior=1,
            tipo="B",
        )
        for i1, i2 in instancia.ordenes_repetitivas
        for j in instancia.indices_trabajadores
    )


def restricciones_definicion_re_i1i2_j(
    instancia: InstanciaAsignacionCuadrillas,
) -> Iterable[Restriccion]:
    """
    Restricciones que definen la variable re_{i1}_{i2}_{j}, que indica si el trabajador j realiza los órdenes i e i+1
    """
    return (
        Restriccion(
            terminos_izq=[
                (1.0, f"a_{i}_{j}_{k}_{l}")
                for i in (i1, i2)
                for k in instancia.indices_dias
                for l in instancia.indices_turnos
            ]
            + [(-1.0, f"re_{i1}_{i2}_{j}")],
            sentido="L",
            term_independiente=1,
        )
        for i1, i2 in instancia.ordenes_repetitivas
        for j in instancia.indices_trabajadores
    )


def objetivo_multa_repeticiones(
    instancia: InstanciaAsignacionCuadrillas,
    penalizacion: float,
) -> TerminosObjetivo:
    """
    Objetivo que penaliza la presencia de repeticiones de trabajadores
    """
    return (
        (-penalizacion, f"re_{i1}_{i2}_{j}")
        for i1, i2 in instancia.ordenes_repetitivas
        for j in instancia.indices_trabajadores
    )


########################################################
#                                                      #
#  Estrategias para manejar conflictos y repeticiones  #
#                                                      #
########################################################


class EstrategiaConflictos(ABC):
    @abstractmethod
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        """
        Modifica el modelo para evitar que no se cumpla la restricción de conflictos de trabajadores
        """


class IgnorarConflictos(EstrategiaConflictos):
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        pass


class EvitarConflictos(EstrategiaConflictos):
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        modelo.agregar_restricciones(restricciones_evitar_conflictos(instancia))


class MultarConflictos(EstrategiaConflictos):
    def __init__(
        self,
        penalizacion: float,
    ):
        self.penalizacion = penalizacion

    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        modelo.agregar_variables(variables_c_j1j2_i(instancia))

        modelo.agregar_restricciones(restricciones_definicion_c_j1j2_i(instancia))

        modelo.agregar_objetivo(objetivo_multa_conflictos(instancia, self.penalizacion))


class EstrategiaRepeticiones(ABC):
    @abstractmethod
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        """
        Modifica el modelo para evitar que no se cumpla la restricción de repeticiones de trabajadores
        """

    def agregar_variables_trabajador_orden(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        modelo.agregar_variables(variables_t_ij(instancia))

        modelo.agregar_restricciones(restricciones_definicion_t_ij(instancia))


class IgnorarRepeticiones(EstrategiaRepeticiones):
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        pass


class EvitarRepeticiones(EstrategiaRepeticiones):
    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        self.agregar_variables_trabajador_orden(instancia, modelo)

        modelo.agregar_restricciones(restricciones_evitar_repeticiones(instancia))


class MultarRepeticiones(EstrategiaRepeticiones):
    def __init__(
        self,
        penalizacion: float,
    ):
        self.penalizacion = penalizacion

    def __call__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        modelo: "ModeloAsignacionCuadrillas",
    ) -> None:
        self.agregar_variables_trabajador_orden(instancia, modelo)

        modelo.agregar_variables(variables_re_i1i2_j(instancia))

        modelo.agregar_restricciones(restricciones_definicion_re_i1i2_j(instancia))

        modelo.agregar_objetivo(
            objetivo_multa_repeticiones(instancia, self.penalizacion)
        )
