from collections.abc import Iterable
from dataclasses import dataclass
from typing import Dict, List

import cplex

from ..solver import ConfiguracionCPLEX, Solver

from .restricciones_deseables import EstrategiaConflictos, EstrategiaRepeticiones

from ..instancia import InstanciaAsignacionCuadrillas
from ..solucion import SolucionAnotada
from .objetivo import (
    TerminosObjetivo,
    objetivo_beneficio_ordenes,
    objetivo_costo_trabajadores,
)
from .restricciones import (
    Restriccion,
    restricciones_definicion_d_jk,
    restricciones_definicion_r_ikl,
    restricciones_definicion_remuneracion,
    restricciones_diferencia_maxima_turnos,
    restricciones_limite_diario,
    restricciones_limite_semanal,
    restricciones_linearizacion_remuneracion,
    restricciones_ordenes_conflictivas,
    restricciones_ordenes_correlativas,
    restricciones_repeticion_de_ordenes,
    restricciones_trabajo_simultaneo,
)
from .variables import (
    Variable,
    variables_asignacion_orden_trabajador_dia_turno,
    variables_realizacion_orden_dia_turno,
    variables_remuneracion_trabajador,
    variables_trabajo_trabajador_dia,
)


@dataclass
class ConfiguracionAsignacionCuadrillas:
    estrategia_conflictos: EstrategiaConflictos
    estrategia_repetitiva: EstrategiaRepeticiones


class ModeloAsignacionCuadrillas:
    def __init__(
        self,
        instancia: InstanciaAsignacionCuadrillas,
        configuracion: ConfiguracionAsignacionCuadrillas,
    ):
        self.instancia = instancia

        self.variables: List[Variable] = []
        self.restricciones: List[Restriccion] = []
        self.objetivo: List[tuple[float, str]] = []

        self.nombre_a_indice: Dict[str, int] = {}

        self.agregar_variables_base()
        self.agregar_restricciones_base()
        self.agregar_objetivo_base()

        configuracion.estrategia_conflictos(instancia, self)
        configuracion.estrategia_repetitiva(instancia, self)

    def agregar_variable(self, variable: Variable) -> None:
        self.variables.append(variable)
        self.nombre_a_indice[variable.nombre] = len(self.variables) - 1

    def agregar_variables(self, variables: Iterable[Variable]) -> None:
        for var in variables:
            self.agregar_variable(var)

    def agregar_restriccion(self, restriccion: Restriccion) -> None:
        self.restricciones.append(restriccion)

    def agregar_restricciones(self, restricciones: Iterable[Restriccion]) -> None:
        for restr in restricciones:
            self.agregar_restriccion(restr)

    def agregar_objetivo(self, terminos: TerminosObjetivo) -> None:
        self.objetivo += terminos

    def agregar_variables_base(self) -> None:
        for var_conj_fn in [
            variables_asignacion_orden_trabajador_dia_turno,
            variables_realizacion_orden_dia_turno,
            variables_trabajo_trabajador_dia,
            variables_remuneracion_trabajador,
        ]:
            self.agregar_variables(var_conj_fn(self.instancia))

    def agregar_restricciones_base(self) -> None:
        for restr_conj_fn in [
            restricciones_trabajo_simultaneo,
            restricciones_limite_diario,
            restricciones_definicion_d_jk,
            restricciones_limite_semanal,
            restricciones_definicion_r_ikl,
            restricciones_repeticion_de_ordenes,
            restricciones_ordenes_conflictivas,
            restricciones_ordenes_correlativas,
            restricciones_linearizacion_remuneracion,
            restricciones_definicion_remuneracion,
            restricciones_diferencia_maxima_turnos,
        ]:
            self.agregar_restricciones(restr_conj_fn(self.instancia))

    def agregar_objetivo_base(self) -> None:
        self.agregar_objetivo(objetivo_beneficio_ordenes(self.instancia))
        self.agregar_objetivo(objetivo_costo_trabajadores(self.instancia))

    def indice_de(self, var_nombre: str) -> int:
        return self.nombre_a_indice[var_nombre]

    def nombre_de(self, var_indice: int) -> str:
        return self.variables[var_indice].nombre

    def armar_solver(
        self,
        configuracion: ConfiguracionCPLEX = ConfiguracionCPLEX(),
    ) -> Solver:
        cpx = cplex.Cplex()
        cpx.objective.set_sense(cpx.objective.sense.maximize)

        obj_map = {nombre: coef for coef, nombre in self.objetivo}

        for var in self.variables:
            cpx.variables.add(
                obj=[obj_map.get(var.nombre, 0)],
                lb=[var.cota_inferior],
                ub=[var.cota_superior],
                types=[var.tipo],
                names=[var.nombre],
            )

        for restr in self.restricciones:
            expresion_traspuesta = []
            expresion_traspuesta += [
                (self.indice_de(var), coef) for coef, var in restr.terminos_izq
            ]
            expresion_traspuesta += [
                (self.indice_de(var), -coef) for coef, var in restr.terminos_der
            ]

            cpx.linear_constraints.add(
                lin_expr=[list(zip(*expresion_traspuesta))],
                senses=[restr.sentido],
                rhs=[restr.term_independiente],
            )

        return Solver(cpx, configuracion=configuracion)

    def anotar_solucion(self, solucion: List[float]) -> SolucionAnotada:
        assert len(solucion) == len(self.variables)
        return SolucionAnotada(
            instancia=self.instancia,
            valores={self.nombre_de(i): valor for i, valor in enumerate(solucion)},
        )
