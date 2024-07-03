from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .variables import Variable

from .restricciones import Restriccion

from ..instancia import InstanciaAsignacionCuadrillas


if TYPE_CHECKING:
    from .modelo import ModeloAsignacionCuadrillas


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
        modelo.agregar_restricciones(
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
        modelo.agregar_variables(
            Variable(
                nombre=f"c^{j1}_{j2}_{i}",
                cota_inferior=0,
                cota_superior=1,
                tipo="B",
            )
            for j1, j2 in instancia.conflictos_trabajadores
            for i in instancia.indices_ordenes
        )

        modelo.agregar_restricciones(
            Restriccion(
                terminos_izq=[
                    (1.0, f"a_{i}_{j}_{k}_{l}")
                    for j in (j1, j2)
                    for k in instancia.indices_dias
                    for l in instancia.indices_turnos
                ]
                + [(-1.0, f"c^{j1}_{j2}_{i}")],
                sentido="L",
                term_independiente=1,
            )
            for j1, j2 in instancia.conflictos_trabajadores
            for i in instancia.indices_ordenes
        )

        modelo.agregar_objetivo(
            (-self.penalizacion, f"c^{j1}_{j2}_{i}")
            for j1, j2 in instancia.conflictos_trabajadores
            for i in instancia.indices_ordenes
        )


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
        modelo.agregar_variables(
            Variable(
                nombre=f"t_{i}_{j}",
                cota_inferior=0,
                cota_superior=1,
                tipo="B",
            )
            for i in instancia.indices_ordenes
            for j in instancia.indices_trabajadores
        )

        modelo.agregar_restricciones(
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

        modelo.agregar_restricciones(
            Restriccion(
                terminos_izq=[(1, f"t_{i1}_{j}"), (1, f"t_{i2}_{j}")],
                sentido="L",
                term_independiente=1,
            )
            for i1, i2 in instancia.ordenes_repetitivas
            for j in instancia.indices_trabajadores
        )


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

        modelo.agregar_variables(
            Variable(
                nombre=f"re^{i1}_{i2}_{j}",
                cota_inferior=0,
                cota_superior=1,
                tipo="B",
            )
            for i1, i2 in instancia.ordenes_repetitivas
            for j in instancia.indices_trabajadores
        )

        modelo.agregar_restricciones(
            Restriccion(
                terminos_izq=[
                    (1.0, f"a_{i}_{j}_{k}_{l}")
                    for i in (i1, i2)
                    for k in instancia.indices_dias
                    for l in instancia.indices_turnos
                ]
                + [(-1.0, f"re^{i1}_{i2}_{j}")],
                sentido="L",
                term_independiente=1,
            )
            for i1, i2 in instancia.ordenes_repetitivas
            for j in instancia.indices_trabajadores
        )

        modelo.agregar_objetivo(
            (-self.penalizacion, f"re^{i1}_{i2}_{j}")
            for i1, i2 in instancia.ordenes_repetitivas
            for j in instancia.indices_trabajadores
        )
